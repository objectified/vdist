import logging
import os
import shutil
import re
import json
import threading

from jinja2 import Environment, FileSystemLoader

from vdist import defaults
from vdist.buildmachine import BuildMachine


class BuildProfile(object):

    def __init__(self, **kwargs):
        self.required_attrs = ['profile_id', 'docker_image', 'script']
        self.optional_attrs = ['insecure_registry']

        for arg in kwargs:
            if arg not in self.required_attrs and \
                    arg not in self.optional_attrs:
                raise AttributeError('attribute not allowed: %s' % arg)

        self.__dict__.update(kwargs)

        self.validate()

        if hasattr(self, 'insecure_registry') and \
                self.insecure_registry == 'true':
            self.insecure_registry = True
        else:
            self.insecure_registry = False

    def validate(self):
        for attr in self.required_attrs:
            if not hasattr(self, attr):
                raise AttributeError(
                    'build profile misses attribute: %s' % attr)
        return True

    def __str__(self):
        return str(self.__dict__)


class Build(object):

    def __init__(self, app, version, source, profile,
                 name=None, use_local_pip_conf=False, build_deps=None,
                 runtime_deps=None, fpm_args='', pip_args='',
                 working_dir='', python_basedir=defaults.PYTHON_BASEDIR,
                 compile_python=True,
                 compile_python_version=defaults.PYTHON_VERSION,
                 requirements_path='/requirements.txt'):
        self.app = app
        self.version = version
        self.source = source
        self.use_local_pip_conf = use_local_pip_conf
        self.working_dir = working_dir
        self.requirements_path = requirements_path
        self.python_basedir = python_basedir
        self.compile_python = compile_python
        self.compile_python_version = compile_python_version

        self.build_deps = []
        if build_deps:
            self.build_deps = build_deps

        self.runtime_deps = []
        if runtime_deps:
            self.runtime_deps = runtime_deps

        self.profile = profile
        self.fpm_args = fpm_args
        self.pip_args = pip_args

        if not name:
            self.name = self.get_safe_dirname()
        else:
            self.name = name

    def __str__(self):
        return str(self.__dict__)

    def get_project_root_from_source(self):
        if self.source['type'] == 'git':
            return os.path.basename(self.source['uri'])
        if self.source['type'] in ['directory', 'git_directory']:
            return os.path.basename(self.source['path'])
        return ''

    def get_safe_dirname(self):
        return re.sub(
            '[^A-Za-z0-9\.\-]',
            '_',
            '-'.join(
                [self.app, self.version, self.profile]
            )
        )


class Builder(object):

    def __init__(
            self,
            profiles_dir=defaults.LOCAL_PROFILES_DIR,
            machine_logs=True, docker_args=None):
        logging.basicConfig(format='%(asctime)s %(levelname)s '
                            '[%(threadName)s] %(name)s %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger('Builder')

        self.build_basedir = os.path.join(
            os.getcwd(),
            defaults.BUILD_BASEDIR)
        self.profiles = {}
        self.builds = []

        self.machine_logs = machine_logs
        self.local_profiles_dir = profiles_dir
        self.docker_args = docker_args

    def add_build(self, **kwargs):
        self.builds.append(Build(**kwargs))

    def _add_profiles_from_file(self, config_file):
        with open(config_file) as f:
            profiles = json.loads(f.read())

            for profile_id in profiles:
                profile = BuildProfile(
                    profile_id=profile_id,
                    docker_image=profiles[profile_id]['docker_image'],
                    script=profiles[profile_id]['script'],
                    insecure_registry=profiles[profile_id].get(
                        'insecure_registry', 'false')
                )

                self.profiles[profile_id] = profile

    def _load_profiles(self):
        internal_profiles = os.path.join(
            os.path.dirname(__file__),
            'profiles', 'internal_profiles.json')
        self._add_profiles_from_file(internal_profiles)

        local_profiles = os.path.join(
            self.local_profiles_dir, defaults.LOCAL_PROFILES_FILE)
        if os.path.isfile(local_profiles):
            self._add_profiles_from_file(local_profiles)

    def _render_template(self, build):
        internal_template_dir = os.path.join(
            os.path.dirname(__file__), 'profiles')

        local_template_dir = os.path.abspath(self.local_profiles_dir)

        env = Environment(loader=FileSystemLoader(
            [internal_template_dir, local_template_dir]))

        if build.profile not in self.profiles:
            raise BuildProfileNotFoundException(
                'profile not found: %s' % build.profile)

        profile = self.profiles[build.profile]
        template_name = profile.script
        template = env.get_template(template_name)

        scratch_dir = os.path.join(
            defaults.SHARED_DIR,
            defaults.SCRATCH_DIR
        )

        # local uid and gid are needed to correctly set permissions
        # on the created artifacts after the build completes
        return template.render(
            local_uid=os.getuid(),
            local_gid=os.getgid(),
            project_root=build.get_project_root_from_source(),
            package_build_root=defaults.PACKAGE_BUILD_ROOT,
            shared_dir=defaults.SHARED_DIR,
            scratch_dir=scratch_dir,
            **build.__dict__
        )

    def _clean_build_basedir(self):
        if os.path.exists(self.build_basedir):
            shutil.rmtree(self.build_basedir)

    def _create_build_basedir(self):
        os.mkdir(self.build_basedir)

    def _write_build_script(self, path, script):
        with open(path, 'w+') as f:
            f.write(script)
        os.chmod(path, 0o777)

    def _populate_scratch_dir(self, scratch_dir, build):
        # write rendered build script to scratch dir
        self._write_build_script(
            os.path.join(scratch_dir, defaults.SCRATCH_BUILDSCRIPT_NAME),
            self._render_template(build)
        )

        # copy local ~/.pip if necessary
        if build.use_local_pip_conf:
            shutil.copytree(
                os.path.join(os.path.expanduser('~'), '.pip'),
                os.path.join(scratch_dir, '.pip')
            )

        # local source type, copy local dir to scratch dir
        if build.source['type'] in ['directory', 'git_directory']:
            if not os.path.exists(build.source['path']):
                raise ValueError(
                    'path does not exist: %s' % build.source['path'])
            else:
                subdir = os.path.basename(build.source['path'])
                shutil.copytree(
                    build.source['path'],
                    os.path.join(scratch_dir, subdir)
                )

    def _create_build_dir(self, build):
        subdir_name = build.get_safe_dirname()

        build_dir = os.path.join(self.build_basedir, subdir_name)

        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        os.mkdir(build_dir)

        # create "scratch" subdirectory for stuff needed at build time
        scratch_dir = os.path.join(build_dir, defaults.SCRATCH_DIR)
        os.mkdir(scratch_dir)

        # write necessary stuff to scratch_dir
        self._populate_scratch_dir(scratch_dir, build)

        return build_dir

    def run_build(self, build):
        profile = self.profiles[build.profile]

        build_dir = self._create_build_dir(build)

        self.logger.info('launching docker image: %s' % profile.docker_image)

        build_machine = BuildMachine(
            machine_logs=self.machine_logs,
            image=profile.docker_image,
            insecure_registry=profile.insecure_registry,
            docker_args=self.docker_args
        )

        self.logger.info('Running build machine for: %s' % build.name)
        build_machine.launch(build_dir=build_dir)

        self.logger.info('Shutting down build machine: %s' % build.name)
        build_machine.shutdown()

    def build(self):
        self._load_profiles()
        self._clean_build_basedir()
        self._create_build_basedir()

        if len(self.builds) < 1:
            raise NoBuildsFoundException()

        threads = []

        for build in self.builds:
            t = threading.Thread(
                name=build.name,
                target=self.run_build,
                args=(build,)
            )
            threads.append(t)
            t.start()


class BuildProfileNotFoundException(Exception):
    pass


class TemplateNotFoundException(Exception):
    pass


class NoBuildsFoundException(Exception):
    pass
