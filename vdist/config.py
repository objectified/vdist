import yaml


class ApplicationConfig(object):

    def load(self, config_file):
        with open(config_file, 'r') as f:
            yaml_dict = yaml.load(f)
            self.__dict__.update(**yaml_dict)

    def validate(self):
        expected_attrs = ['app', 'git_url', 'build_deps', 'runtime_deps',
                          'build_machine']
        for attr in expected_attrs:
            if attr not in self.__dict__:
                raise Exception('Config attribute missing: %s' % attr)

    def __str__(self):
        return 'app: %s, git_url: %s, build_deps: %s, runtime_deps: %s, ' \
            'build_machine: %s, pipeline: %s' % \
            (self.app, self.git_url,
             ', '.join(self.build_deps),
             ', '.join(self.runtime_deps),
             self.build_machine, self.pipeline
             )
