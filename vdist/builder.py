import logging
import os
import shutil

from jinja2 import Environment, PackageLoader

from vdist.machines.buildmachinefactory import BuildMachineFactory
from vdist.template_mappings import mappings


class Builder(object):

    def __init__(self, config):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger('Builder')

        self.config = config

        self.build_dir = os.getcwd() + '/build'
        self.build_script_path = self.build_dir + '/buildscript.sh'

    def _render_template(self, flavor):
        env = Environment(loader=PackageLoader('vdist', 'templates'))
        template = env.get_template(mappings[flavor])

        return template.render(
            app=self.config.app,
            build_deps=self.config.build_deps,
            runtime_deps=self.config.runtime_deps,
            git_url=self.config.git_url
        )

    def _clean_build_dir(self):
        shutil.rmtree(self.build_dir)

    def _create_build_dir(self):
        os.mkdir(self.build_dir)

    def _write_build_script(self, script):
        with open(self.build_script_path, 'w+') as f:
            f.write(script)
        os.chmod(self.build_script_path, 0777)

    def run(self):
        driver = self.config.build_machine['driver']
        flavor = self.config.build_machine['flavor']

        self.logger.info('creating build machine with driver: %s, flavor: %s' %
                         (driver, flavor))
        build_machine = BuildMachineFactory.create_build_machine(
            driver=driver,
            flavor=flavor
        )

        if os.path.isdir(self.build_dir):
            self._clean_build_dir()

        self.logger.info('creating build dir: %s' % self.build_dir)
        self._create_build_dir()

        self.logger.info('writing build script to: %s' % self.build_script_path)
        self._write_build_script(self._render_template(flavor))

        self.logger.info('Launching build machine: %s' % flavor)
        build_machine.launch(build_dir=self.build_dir)
        build_machine.shutdown()
