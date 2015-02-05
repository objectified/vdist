import logging
import os

import docker
from docker.utils import kwargs_from_env

from vdist import defaults


class BuildMachine(object):

    def __init__(self, machine_logs=True, image=None, insecure_registry=False,
                 docker_args=None):
        self.logger = logging.getLogger('BuildMachine')

        if docker_args:
            env_kwargs = kwargs_from_env()
            env_kwargs.update(docker_args)

            self.dockerclient = docker.Client(**env_kwargs)
        else:
            self.dockerclient = docker.Client(**kwargs_from_env())

        self.container = None

        self.machine_logs = machine_logs
        self.image = image

        self.insecure_registry = insecure_registry

    def _image_exists(self, image):
        for img in self.dockerclient.images():
            if image in img['RepoTags']:
                return True
        return False

    def _pull_image(self, image):
        self.logger.info('Insecure registry: %s' % self.insecure_registry)

        self.dockerclient.pull(image, insecure_registry=self.insecure_registry)

    def launch(self, build_dir, extra_binds=None):
        if not self._image_exists(self.image):
            self.logger.info(
                'Image does not exist: %s, pulling from repo..' % self.image)
            self._pull_image(self.image)

        binds = {build_dir: defaults.SHARED_DIR}
        if extra_binds:
            binds = binds.items() + extra_binds.items()

        path_to_command = os.path.join(
            defaults.SHARED_DIR,
            defaults.SCRATCH_DIR,
            defaults.SCRATCH_BUILDSCRIPT_NAME
        )
        self.logger.info('Starting container: %s' % self.image)
        self.container = self.dockerclient.create_container(
            image=self.image,
            command=path_to_command)

        self.dockerclient.start(
            container=self.container.get('Id'),
            binds=binds)

        lines = self.dockerclient.logs(container=self.container.get('Id'),
                                       stdout=True, stderr=True, stream=True)
        for line in lines:
            if self.machine_logs:
                self.logger.info(line.strip())

    def shutdown(self):
        self.dockerclient.stop(container=self.container.get('Id'))
        self.dockerclient.remove_container(container=self.container.get('Id'))
