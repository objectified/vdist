import logging
import os
import shutil
import re
import json
import threading

from jinja2 import Environment, FileSystemLoader

from vdist.machines.buildmachinefactory import BuildMachineFactory


class Build(object):

    def __init__(self, name, app, version, git_url, build_deps=None,
                 runtime_deps=None, build_machine=None, fpm_args=''):
        self.name = name
        self.app = app
        self.version = version
        self.git_url = git_url

        self.build_deps = []
        if build_deps:
            self.build_deps = build_deps

        self.runtime_deps = []
        if runtime_deps:
            self.runtime_deps = runtime_deps

        self.build_machine = build_machine
        self.fpm_args = fpm_args

    def __str__(self):
        return 'name: %s, app: %s, version: %s, git_url: %s, build_deps: %s' \
            ' runtime_deps: %s, build_machine: %s, fpm_args: %s' \
            (self.name, self.app, self.version, self.git_url,
             ', '.join(self.build_deps), ', '.join(self.runtime_deps),
             self.build_machine, self.fpm_args)


class Builder(object):

    def __init__(self, local_template_path='templates', machine_logs=True):
        logging.basicConfig(format='%(asctime)s %(levelname)s '
                            '[%(threadName)s] %(name)s %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger('Builder')

        self.build_basedir = os.path.join(os.getcwd(), 'dist')
        self.builds = []
        self.mappings = {}

        self.machine_logs = machine_logs
        self.local_template_path = local_template_path

    def add_build(self, **kwargs):
        self.builds.append(Build(**kwargs))

    def _load_mappings(self):
        internal_settings = os.path.join(
            os.path.dirname(__file__),
            'templates', 'internal_mappings.json')

        with open(internal_settings) as f:
            self.mappings.update(json.loads(f.read()))

        local_template_mappings = os.path.join(self.local_template_path,
                                               'mappings.json')
        if os.path.isfile(local_template_mappings):
            with open(local_template_mappings) as f:
                self.mappings.update(json.loads(f.read()))
        else:
            self.logger.info('No local mappings found in %s' %
                             local_template_mappings)

    def _render_template(self, build):
        template = None

        internal_template_dir = os.path.join(
            os.path.dirname(__file__), 'templates')

        local_template_dir = os.path.abspath(self.local_template_path)

        env = Environment(loader=FileSystemLoader(
            [internal_template_dir, local_template_dir]))
        if build.build_machine in self.mappings:
            template_name = self.mappings[build.build_machine]['template']
            template = env.get_template(template_name)
        else:
            raise TemplateNotFoundException()

        return template.render(
            app=build.app,
            build_deps=build.build_deps,
            runtime_deps=build.runtime_deps,
            git_url=build.git_url,
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
                [build.app, build.version, build.build_machine]
            )
        )

        build_dir = os.path.join(self.build_basedir, subdir_name)

        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        os.mkdir(build_dir)

        return build_dir

    def run_build(self, build):
        # only supported driver for now
        driver = 'docker'
        flavor = self.mappings[build.build_machine]['flavor']

        build_dir = self._create_build_dir(build)

        self.logger.info('creating build machine "%s" with driver: %s, '
                         'flavor: %s' %
                         (build.build_machine, driver, flavor))
        build_machine = BuildMachineFactory.create_build_machine(
            driver=driver,
            flavor=flavor,
            machine_logs=self.machine_logs
        )

        self.logger.info('writing build script to: %s' % build_dir)
        self._write_build_script(
            os.path.join(build_dir, 'buildscript.sh'),
            self._render_template(build)
        )

        self.logger.info('Running build machine: %s' % flavor)
        build_machine.launch(build_dir=build_dir)

        self.logger.info('Shutting down build machine: %s' % flavor)
        build_machine.shutdown()

    def build(self):
        self._load_mappings()
        self._clean_build_basedir()
        self._create_build_basedir()

        threads = []

        for build in self.builds:
            t = threading.Thread(
                name=build.name,
                target=self.run_build,
                args=(build,)
            )
            threads.append(t)
            t.start()
        else:
            raise NoBuildsFoundException()


class TemplateNotFoundException(Exception):
    pass


class NoBuildsFoundException(Exception):
    pass
