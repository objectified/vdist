from vdist.machines.buildmachinedocker import BuildMachineDocker


class BuildMachineFactory(object):

    supported_drivers = {
        'docker': BuildMachineDocker
    }

    @classmethod
    def create_build_machine(cls, driver=None, flavor=None, machine_logs=True):
        if driver not in BuildMachineFactory.supported_drivers:
            raise Exception('Driver not supported: %s' % driver)
        else:
            return BuildMachineFactory.supported_drivers[driver](
                flavor, machine_logs)
