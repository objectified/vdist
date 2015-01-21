import logging
import os
import shutil
import re
import json
import threading

from jinja2 import Environment, FileSystemLoader

from vdist.machines.buildmachinedocker import BuildMachineDocker


class BuildMachine(object):

    def __init__(self, **kwargs):
        self.required_attrs = ['machine_id', 'docker_image', 'script']
        self.optional_attrs = ['insecure_registry']

        for arg in kwargs:
            if arg not in self.required_attrs and \
                    arg not in self.optional_attrs:
                raise AttributeError('attribute not allowed: %s' % arg)

        self.__dict__.update(kwargs)

        self.validate()

        if hasattr(self, 'insecure_registry') and \
                self.insecure_registry == 'false':
            self.insecure_registry = False

    def validate(self):
        for attr in self.required_attrs:
            if not hasattr(self, attr):
                raise AttributeError(
                    'build machine misses attribute: %s' % attr)
        return True

    def __str__(self):
        return str(self.__dict__)


class Build(object):

    def __init__(self, name, app, version, transport, build_deps=None,
                 runtime_deps=None, build_machine_id=None, fpm_args=''):
        self.name = name
        self.app = app
        self.version = version
        self.transport = transport

        self.build_deps = []
        if build_deps:
            self.build_deps = build_deps

        self.runtime_deps = []
        if runtime_deps:
            self.runtime_deps = runtime_deps

        self.build_machine_id = build_machine_id
        self.fpm_args = fpm_args

    def __str__(self):
        return str(self.__dict__)


class Builder(object):

    def __init__(self, local_template_path='templates', machine_logs=True):
        logging.basicConfig(format='%(asctime)s %(levelname)s '
                            '[%(threadName)s] %(name)s %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger('Builder')

        self.build_basedir = os.path.join(os.getcwd(), 'dist')
        self.build_machines = {}
        self.builds = []

        self.machine_logs = machine_logs
        self.local_template_path = local_template_path

    def add_build(self, **kwargs):
        self.builds.append(Build(**kwargs))

    def _add_build_machines_from_file(self, config_file):
        with open(config_file) as f:
            machines = json.loads(f.read())

            for machine_id in machines:
                machine = BuildMachine(
                    machine_id=machine_id,
                    docker_image=machines[machine_id]['docker_image'],
                    script=machines[machine_id]['script']
                )
                self.build_machines[machine_id] = machine

    def _load_mappings(self):
        internal_build_machines = os.path.join(
            os.path.dirname(__file__),
            'templates', 'internal_build_machines.json')
        self._add_build_machines_from_file(internal_build_machines)

        local_build_machines = os.path.join(
            self.local_template_path, 'build_machines.json')
        if os.path.isfile(local_build_machines):
            self._add_build_machines_from_file(local_template_mappings)

    def _render_template(self, build):
        template = None

        internal_template_dir = os.path.join(
            os.path.dirname(__file__), 'templates')

        local_template_dir = os.path.abspath(self.local_template_path)

        env = Environment(loader=FileSystemLoader(
            [internal_template_dir, local_template_dir]))

        if build.build_machine_id not in self.build_machines:
            raise BuildMachineNotFoundException(
                'machine not found: %s' % build.build_machine_id)

        machine = self.build_machines[build.build_machine_id]
        template_name = machine.script
        template = env.get_template(template_name)

        return template.render(
            app=build.app,
            build_deps=build.build_deps,
            runtime_deps=build.runtime_deps,
            transport=build.transport,
            version=build.version,
            fpm_args=build.fpm_args,
            local_uid=os.getuid(),
            local_gid=os.getgid()
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

    def _create_build_dir(self, build):
        subdir_name = re.sub(
            '[^A-Za-z0-9\.\-]',
            '_',
            '-'.join(
                [build.app, build.version, build.build_machine_id]
            )
        )

        build_dir = os.path.join(self.build_basedir, subdir_name)

        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        os.mkdir(build_dir)

        return build_dir

    def run_build(self, build):
        machine = self.build_machines[build.build_machine_id]

        build_dir = self._create_build_dir(build)

        self.logger.info('launching docker image: %s' % machine.docker_image)

        build_machine = BuildMachineDocker(
            machine_logs=self.machine_logs,
            image=machine.docker_image
        )

        self.logger.info('writing build script to: %s' % build_dir)
        self._write_build_script(
            os.path.join(build_dir, 'buildscript.sh'),
            self._render_template(build)
        )

        self.logger.info('Running build machine for: %s' % build.name)
        build_machine.launch(build_dir=build_dir)

        self.logger.info('Shutting down build machine: %s' % build.name)
        build_machine.shutdown()

    def build(self):
        self._load_mappings()
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


class BuildMachineNotFoundException(Exception):
    pass


class TemplateNotFoundException(Exception):
    pass


class NoBuildsFoundException(Exception):
    pass
