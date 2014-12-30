class BuildMachine(object):

    def __init__(self, flavor):
        self.flavor = flavor

    def get_flavor(self):
        return self.flavor

    def launch(self):
        pass

    def shutdown(self):
        pass
