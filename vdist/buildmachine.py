import itertools
import logging
import os
import subprocess

from vdist import defaults


class BuildMachine(object):

    def __init__(self, machine_logs=True, image=None, insecure_registry=False,
                 docker_cli='docker'):
        self.logger = logging.getLogger('BuildMachine')

        self.machine_logs = machine_logs
        self.image = image

        self.container_id = None

        self.docker_cli = docker_cli

        self.insecure_registry = insecure_registry

    def _run_cli(self, cmd):
        self.logger.info('Running command: "%s"' % cmd)
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        media = [p.stdout, p.stderr]
        first_line = self._read_from_media(media)

        p.stdout.close()
        p.stderr.close()
        p.wait()

        return first_line

    def _read_from_media(self, media):
        first_line = None
        for input_to_read in media:
            for line in iter(input_to_read.readline, b''):
                line = str(line.decode("UTF-8")).strip()
                if not first_line:
                    first_line = line
                self.logger.info(line)
        return first_line

    @staticmethod
    def _binds_to_shell_volumes(binds):
        if defaults.PYTHON3_INTERPRETER:
            vol_list = ['-v %s:%s' % (k, v) for k, v in binds.items()]
        else:
            vol_list = ['-v %s:%s' % (k, v) for k, v in binds.iteritems()]
        return ' '.join(vol_list)

    def launch(self, build_dir, extra_binds=None):
        binds = {build_dir: defaults.SHARED_DIR}
        if extra_binds:
            binds = list(itertools.chain(binds.items(), extra_binds.items()))
        path_to_command = os.path.join(
            defaults.SHARED_DIR,
            defaults.SCRATCH_DIR,
            defaults.SCRATCH_BUILDSCRIPT_NAME
        )
        self.logger.info('Starting container: %s' % self.image)
        self.container_id = self._run_cli(
            '%s run -d -ti %s %s bash' %
            (self.docker_cli,
             self._binds_to_shell_volumes(binds),
             self.image))

        self._run_cli(
            '%s exec %s %s' %
            (self.docker_cli, self.container_id, path_to_command))

    def shutdown(self):
        self.logger.info('Stopping container: %s' % self.container_id)
        self._run_cli('%s stop %s' % (self.docker_cli, self.container_id))

        self.logger.info('Removing container: %s' % self.container_id)
        self._run_cli('%s rm -f %s' % (self.docker_cli, self.container_id))
