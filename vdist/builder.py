import logging
import os
import shutil
import re

from jinja2 import Environment, PackageLoader

from vdist.machines.buildmachinefactory import BuildMachineFactory
from vdist.template_mappings import mappings


class Build(object):

    def __init__(self, name, app, version, git_url, build_deps=None,
                 runtime_deps=None, build_machine=None, fpm_args=''):
        self.name = name
        self.app = app
        self.version = version
        self.git_url = git_url

        if not build_deps:
            self.build_deps = []
        else:
            self.build_deps = build_deps

        if not runtime_deps:
            self.runtime_deps = []
        else:
            self.runtime_deps = runtime_deps

        if 'driver' not in build_machine or 'flavor' not in build_machine:
            raise ValueError("build_machine should have "
                             "'driver' and 'flavor' keys")

        self.build_machine = build_machine
        self.fpm_args = fpm_args

    def __str__(self):
        return 'name: %s, app: %s, version: %s, git_url: %s, build_deps: %s' \
            ' runtime_deps: %s, build_machine driver: %s' \
            'build_machine flavor: %s, fpm_args: %s' % \
            (self.name, self.app, self.version, self.git_url,
             ', '.join(self.build_deps), ', '.join(self.runtime_deps),
             self.build_machine['driver'], self.build_machine['flavor'],
             self.fpm_args)


class Builder(object):

    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s '
                            '%(name)s %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger('Builder')

        self.build_basedir = os.getcwd() + '/dist'

        self.builds = []

    def add_build(self, **kwargs):
        self.builds.append(Build(**kwargs))

    def _render_template(self, build):
        env = Environment(loader=PackageLoader('vdist', 'templates'))
        template = env.get_template(mappings[build.build_machine['flavor']])

        return template.render(
            app=build.app,
            build_deps=build.build_deps,
            runtime_deps=build.runtime_deps,
            git_url=build.git_url,
            version=build.version,
            fpm_args=build.fpm_args
        )

    def _clean_build_basedir(self):
        if os.path.exists(self.build_basedir):
            shutil.rmtree(self.build_basedir)

    def _create_build_basedir(self):
        os.mkdir(self.build_basedir)

    def _write_build_script(self, path, script):
        with open(path, 'w+') as f:
            f.write(script)
        os.chmod(path, 0777)

    def _create_build_dir(self, build):
        subdir_name = re.sub(
            '[^A-Za-z0-9\.\-]',
            '_',
            '-'.join(
                [build.app, build.version, build.build_machine['flavor']]
            )
        )

        build_dir = self.build_basedir + '/' + subdir_name

        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        os.mkdir(build_dir)

        return build_dir

    def run_build(self, build):
        driver = build.build_machine['driver']
        flavor = build.build_machine['flavor']

        build_dir = self._create_build_dir(build)

        self.logger.info('creating build machine with driver: %s, flavor: %s' %
                         (driver, flavor))
        build_machine = BuildMachineFactory.create_build_machine(
            driver=driver,
            flavor=flavor
        )

        self.logger.info('writing build script to: %s' % build_dir)
        self._write_build_script(
            build_dir + '/buildscript.sh',
            self._render_template(build)
        )

        self.logger.info('Running build machine: %s' % flavor)
        build_machine.launch(build_dir=build_dir)

        self.logger.info('Shutting down build machine: %s' % flavor)
        build_machine.shutdown()

    def build(self):
        self._clean_build_basedir()
        self._create_build_basedir()

        for build in self.builds:
            self.run_build(build)
