'''Deployment base tasks'''

import os.path

from fabric.api import env, execute, abort, runs_once

from ..release import Release
from ..inject import TaskInjector, methodtask


class DeployBase(TaskInjector):

    def __init__(self, deploy_path, release=None):
        self.deploy_path = deploy_path
        if release is None:
            release = Release(deploy_path)
        self.release = release
        self.envs = {}

        # Set fabric options
        env.new_style_tasks = True
        env.colorize_errors = True

    @methodtask
    @runs_once
    def build(self):
        '''Build project'''
        try:
            fn = getattr(self, 'compile')
        except AttributeError:
            pass
        else:
            fn()

    @methodtask
    @runs_once
    def update(self):
        '''Sync project with server'''
        with self.release:
            # Pre sync setup
            try:
                fn = getattr(self, 'setup')
            except AttributeError:
                pass
            else:
                execute(fn)
            # Sync files to remote
            try:
                fn = getattr(self, 'sync')
            except AttributeError:
                pass
            else:
                execute(fn)
            # Post sync setup
            try:
                fn = getattr(self, 'finalize')
            except AttributeError:
                pass
            else:
                execute(fn)

    @methodtask
    def finalize(self):
        '''Finalize release'''
        self.release.symlink()
        self.release.cleanup()

    @methodtask
    def rollback(self):
        '''Rollback to previous release'''
        self.release.rollback_release()

    @methodtask
    @runs_once
    def env(self, role):
        '''Set environment role to ROLE'''
        try:
            for (k, v) in self.envs[role].items():
                setattr(self, k, v)
        except KeyError:
            abort("Missing environment role '{0}'".format(role))

    def add_env(self, role, **kwargs):
        '''Add environment role to role lookup

        All `kwargs` specified here will override attributes on an instance of
        this class, allowing for path overrides for staging areas, etc. For
        example::

            deploy = DeployBase('/tmp/deploy_path/stage')
            deploy.add_env('prod', release=Release('/tmp/deploy_path/prod'))
            deploy.include_tasks()

        The above example will expose the `env` task, which will set the base
        deploy path to `/tmp/deploy_path/prod`::

            fab env:prod update

        :param role: role name
        :param kwargs: keyword arguments for overriding instance variables
        '''
        self.envs[role] = kwargs

    def local_path(self, *args):
        return os.path.join(
            os.path.dirname(env.real_fabfile),
            *args
        )

    def remote_path(self, name):
        return os.path.join(self.release.base_path, name)
