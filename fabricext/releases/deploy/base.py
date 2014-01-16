'''Deployment base tasks'''

import os.path

from fabric.api import env

from ..release import Release
from ..inject import TaskInjector, methodtask


class DeployBase(TaskInjector):

    def __init__(self, deploy_path, release=None):
        self.deploy_path = deploy_path
        if release is None:
            release = Release(deploy_path)
        self.release = release

    @methodtask
    def build(self):
        '''Build project'''
        try:
            self.compile()
        except AttributeError:
            pass

    @methodtask
    def update(self):
        '''Sync project with server'''
        with self.release:
            try:
                self.sync()
            except AttributeError:
                pass
            try:
                self.finalize()
            except AttributeError:
                pass

    def local_path(self, *args):
        return os.path.join(
            os.path.dirname(env.real_fabfile),
            *args
        )

    def remote_path(self, name):
        return os.path.join(self.release.base_path, name)
