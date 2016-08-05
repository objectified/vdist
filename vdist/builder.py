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
                 runtime_deps=None, custom_filename=None,
                 fpm_args='', pip_args='',
                 package_install_root=None,
                 package_tmp_root=None,
                 working_dir='', python_basedir=None,
                 compile_python=True,
                 python_version=defaults.PYTHON_VERSION,
                 requirements_path='/requirements.txt'):
        self.app = app
        self.version = version.format(**os.environ)
        self.source = source
        self.use_local_pip_conf = use_local_pip_conf
        if package_install_root is None:
            self.package_install_root = defaults.PACKAGE_INSTALL_ROOT.format(**os.environ)
        else:
            self.package_install_root = package_install_root.format(**os.environ)
        if package_tmp_root is None:
            self.package_tmp_root = defaults.PACKAGE_TMP_ROOT.format(**os.environ)
        else:
            self.package_tmp_root = package_tmp_root.format(**os.environ)
        self.working_dir = working_dir.format(**os.environ)
        self.requirements_path = requirements_path.format(**os.environ)
        if python_basedir is None:
            self.python_basedir = "/".join([defaults.PYTHON_BASEDIR, app]).format(**os.environ)
        else:
            self.python_basedir = python_basedir.format(**os.environ)
        self.compile_python = compile_python
        self.python_version = python_version.format(**os.environ)
        if custom_filename:
            self.custom_filename = custom_filename.format(**os.environ)
        else:
            self.custom_filename = None

        self.build_deps = []
        if build_deps:
            self.build_deps = build_deps

        self.runtime_deps = []
        if runtime_deps:
            self.runtime_deps = runtime_deps

        self.profile = profile
        self.fpm_args = fpm_args.format(**os.environ)
        self.pip_args = pip_args.format(**os.environ)

        if not name:
            self.name = self.get_safe_dirname()
        else:
            self.name = name

    def __str__(self):
        return str(self.__dict__)

    def get_project_root_from_source(self):
        if self.source['type'] == 'git':
            return os.path.basename(self.source['uri'].rstrip('/'))
        if self.source['type'] in ['directory', 'git_directory']:
            return os.path.basename(self.source['path'].rstrip('/'))
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
            machine_logs=True):
        logging.basicConfig(format='%(asctime)s %(levelname)s '
                            '[%(threadName)s] %(name)s %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger('Builder')

        self.build_basedir = defaults.BUILD_BASEDIR
        self.profiles = {}
        self.builds = []

        self.machine_logs = machine_logs
        self.local_profiles_dir = profiles_dir

    def add_build(self, **kwargs):
        self.builds.append(Build(**kwargs))

    def _create_vdist_dir(self):
        vdist_path = os.path.join(os.path.expanduser('~'), '.vdist')
        if not os.path.exists(vdist_path):
            self.logger.info('Creating: %s' % vdist_path)
            os.mkdir(vdist_path)

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
            shared_dir=defaults.SHARED_DIR,
            scratch_dir=scratch_dir,
            **build.__dict__
        )

    def _clean_build_basedir(self):
        if os.path.exists(self.build_basedir):
            shutil.rmtree(self.build_basedir)

    def _create_build_basedir(self):
        os.mkdir(self.build_basedir)

    @staticmethod
    def _write_build_script(path, script):
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
                    build.source['path'].rstrip('/'),
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
            insecure_registry=profile.insecure_registry
        )

        self.logger.info('Running build machine for: %s' % build.name)
        build_machine.launch(build_dir=build_dir)

        self.logger.info('Shutting down build machine: %s' % build.name)
        build_machine.shutdown()

        self.logger.info('*** Resulting OS packages are in: %s ***' % build_dir)

    def get_available_profiles(self):
        self._load_profiles()
        return self.profiles

    def build(self):
        self._create_vdist_dir()
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

        for t in threads:
            t.join()


class BuildProfileNotFoundException(Exception):
    pass


class TemplateNotFoundException(Exception):
    pass


class NoBuildsFoundException(Exception):
    pass
