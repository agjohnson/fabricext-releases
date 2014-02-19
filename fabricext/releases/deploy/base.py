'''Deployment base tasks'''

import os.path

from fabric.api import env, execute, abort, runs_once, puts
from fabric.colors import green

from ..release import Release
from ..inject import TaskInjector, methodtask


class DeployBase(TaskInjector):

    def __init__(self, deploy_path=None, release=None, hosts=None, roles=None,
            **kwargs):
        self.envs = {}
        if release is not None or deploy_path is not None:
            self.add_env(
                'default',
                deploy_path=deploy_path,
                release=release,
                default=True,
                hosts=hosts,
                roles=roles,
                **kwargs
            )

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
            self.set_env(**self.envs[role])
            self.update_tasks()
        except KeyError:
            abort("Missing environment role '{0}'".format(role))

    def add_env(self, role, deploy_path=None, release=None, default=False,
            hosts=[], roles=[], **kwargs):
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
        :param deploy_path: deploy path to create release
        :param release: customized release
        :param default: set env as default environment
        :param hosts: set roles for hosts
        :param roles: set roles for tasks
        :param kwargs: keyword arguments for overriding instance variables
        '''
        # Create release object
        if release is None and deploy_path is not None:
            self.deploy_path = deploy_path
            release = Release(deploy_path)
        elif release is not None:
            self.deploy_path = release.base_path
        else:
            raise ValueError('Missing both deploy_path and release keywords')

        self.envs[role] = {
            'deploy_path': deploy_path,
            'release': release,
            'hosts': hosts,
            'roles': roles
        }
        self.envs[role].update(kwargs)
        if default:
            self.set_env(**self.envs[role])

    def set_env(self, **kwargs):
        '''Set deploy arguments based on environment arguments'''
        for (k, v) in kwargs.items():
            setattr(self, k, v)

    def local_path(self, *args):
        return os.path.join(
            os.path.dirname(env.real_fabfile),
            *args
        )

    def remote_path(self, name):
        return os.path.join(self.release.base_path, name)
