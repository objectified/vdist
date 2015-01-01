import yaml


class ConfigError(Exception):
    pass


class ApplicationConfig(object):

    def load(self, config_file):
        with open(config_file, 'r') as f:
            yaml_dict = yaml.load(f)
            self.__dict__.update(**yaml_dict)

        if 'fpm_args' not in self.__dict__:
            self.fpm_args = ''

    def validate(self):
        expected_attrs = ['app', 'version', 'git_url', 'build_deps',
                          'runtime_deps', 'build_machine']
        for attr in expected_attrs:
            if attr not in self.__dict__:
                raise ConfigError('Config attribute missing: %s' % attr)

        if type(self.build_deps) is not list:
            raise ConfigError('build_deps should be a list')

        if type(self.runtime_deps) is not list:
            raise ConfigError('build_deps should be a list')

        return True

    def __str__(self):
        str_repr = 'app: %s, version: %s: git_url: %s, build_deps: %s, ' \
            'runtime_deps: %s, build_machine: %s, build_pipeline: %s' \
            'fpm_args: %s' % \
            (self.app, self.version, self.git_url,
             ', '.join(self.build_deps),
             ', '.join(self.runtime_deps),
             self.build_machine, self.build_pipeline,
             self.fpm_args
             )

        return str_repr
