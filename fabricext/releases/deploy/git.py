'''
Fabric Git release deployment model
'''

import os
import os.path

from fabric.api import run, lcd, local, puts
from fabric.colors import green, red
from fabric.contrib.project import rsync_project

from ..inject import methodtask
from .base import DeployBase


class GitDeploy(DeployBase):

    def __init__(self, name, deploy_path, build_path=None, *args, **kwargs):
        super(GitDeploy, self).__init__(deploy_path, *args, **kwargs)
        self.name = name
        if build_path is None:
            build_path = self.local_path('build')
        self.build_path = build_path

    @methodtask
    def build(self):
        '''Build project'''
        if not os.path.exists(self.build_path):
            os.mkdir(self.build_path)
        try:
            self.checkout()
        except AttributeError:
            pass
        super(GitDeploy, self).build()

    def checkout(self):
        raise NotImplementedError('Missing method `checkout`')

    def sync(self):
        try:
            puts(green('Rsync files to remote host.'))
            rsync_project(
                remote_dir=self.remote_path('cache'),
                local_dir="{}/".format(self.build_path),
                delete=True,
                extra_opts='-c'
            )
            run('rsync -lrp {cache}/ {release}/'.format(
                cache=self.remote_path('cache'),
                release=self.release.current_release_path()
            ))
        except Exception as e:
            puts(red(
                'Failure updating code on remote servers: {0}'.format(str(e))
            ))


class GitIndexDeploy(GitDeploy):
    '''Git checkout index deployment

    :param branch: optional branch name
    '''

    def checkout(self):
        puts(green('Checking out index to temporary path.'))
        try:
            with lcd(self.local_path()):
                local('git checkout-index --prefix={path}/ -a'.format(
                    path=self.build_path
                ))
        except:
            puts(red('Failure checking out.'))
