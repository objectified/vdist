import yaml


class ApplicationConfig(object):

    def load(self, config_file):
        with open(config_file, 'r') as f:
            yaml_dict = yaml.load(f)
            self.__dict__.update(**yaml_dict)

    def validate(self):
        expected_attrs = ['app', 'version', 'git_url', 'build_deps',
                          'runtime_deps', 'build_machine']
        for attr in expected_attrs:
            if attr not in self.__dict__:
                raise ValueError('Config attribute missing: %s' % attr)

        return True

    def __str__(self):
        return 'app: %s, version: %s: git_url: %s, build_deps: %s, ' \
            'runtime_deps: %s, build_machine: %s, build_pipeline: %s' % \
            (self.app, self.version, self.git_url,
             ', '.join(self.build_deps),
             ', '.join(self.runtime_deps),
             self.build_machine, self.build_pipeline
             )
