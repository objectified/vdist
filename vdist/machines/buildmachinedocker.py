import logging

import docker
from docker.utils import kwargs_from_env

from vdist.machines.buildmachine import BuildMachine


class BuildMachineDocker(object):

    def __init__(self, machine_logs=True, image=None):
        self.logger = logging.getLogger('BuildMachineDocker')

        self.dockerclient = docker.Client(**kwargs_from_env())
        self.container = None

        self.machine_logs = machine_logs
        self.image = image

    def _image_exists(self, image):
        for img in self.dockerclient.images():
            if image in img['RepoTags']:
                return True
        return False

    def _pull_image(self, image):
        self.dockerclient.pull(image)

    def launch(self, build_dir):
        if not self._image_exists(self.image):
            self.logger.info(
                'Image does not exist: %s, pulling from repo..' % self.image)
            self._pull_image(self.image)

        self.logger.info('Starting container: %s' % self.image)
        self.container = self.dockerclient.create_container(
            image=self.image,
            command='/opt/buildscript.sh')
        self.dockerclient.start(
            container=self.container.get('Id'),
            binds={build_dir: '/opt'})
        lines = self.dockerclient.logs(container=self.container.get('Id'),
                                       stdout=True, stderr=True, stream=True)
        for line in lines:
            if self.machine_logs:
                self.logger.info(line.strip())

    def shutdown(self):
        self.dockerclient.stop(container=self.container.get('Id'))
        self.dockerclient.remove_container(container=self.container.get('Id'))
