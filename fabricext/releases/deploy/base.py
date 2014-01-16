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

        # Set fabric options
        env.new_style_tasks = True
        env.colorize_errors = True

    @methodtask
    def build(self):
        '''Build project'''
        try:
            fn = getattr(self, 'compile')
        except AttributeError:
            pass
        finally:
            fn()

    @methodtask
    def update(self):
        '''Sync project with server'''
        with self.release:
            try:
                fn = getattr(self, 'sync')
            except AttributeError:
                pass
            finally:
                fn()
                try:
                    fn = getattr(self, 'finalize')
                except AttributeError:
                    pass
                finally:
                    fn()

    def local_path(self, *args):
        return os.path.join(
            os.path.dirname(env.real_fabfile),
            *args
        )

    def remote_path(self, name):
        return os.path.join(self.release.base_path, name)
