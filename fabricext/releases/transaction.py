'''
Fabric transaction support
'''

import types

from fabric.api import *  # noqa
from fabric.utils import error, warn
from fabric.colors import green


class Transaction(object):
    '''Create a context manager to wrap up a transaction with rollbacks.

    This class is used to wrap up code with an exception test and rollback.
    Rollback functions can be added using the :py:meth:`.on_rollback` method of
    an instance of the :py:class:`.Transaction` context manager::

        with transaction() as t:
            run('mkdir /tmp/foobar')
            t.on_rollback('rm -rf /tmp/foobar')

    The :py:meth:`.on_rollback` method appends each rollback function to a list
    of rollback calls -- either a string instance or a callable function can be
    passed. On an exception in the context manager, each rollback is called
    in reverse.
    '''

    def __init__(self):
        self.rollback_cmds = []

    def __enter__(self):
        puts(green('Starting transaction.'))
        return self

    def __exit__(self, type, value, tb):
        if tb is None:
            puts(green('Finishing transaction.'))
        else:
            error('Transaction failed.', func=warn)
            error('Rolling back.', func=warn)
            self.rollback()

    def on_rollback(self, cmd):
        '''Append command `cmd` to rollback list.

        The `cmd` parameter can be a string, which is then run remotely on the
        host, or it can be a function, which is called directly on rollback.

        :param cmd: command to execute on rollback
        :type cmd: str or function
        '''
        self.rollback_cmds.append(cmd)

    def rollback(self):
        '''Rollback transaction by executing the list of rollback commands.

        Each command in `rollback_cmds` will be executed remotely. If `cmd` is a
        string, execute remotely. If `cmd` is a function, call the function.
        '''
        for cmd in self.get_rollback_cmds():
            if isinstance(cmd, str):
                run(cmd)
            elif isinstance(cmd, types.FunctionType):
                cmd()
            else:
                raise Exception('Unknown rollback type')

    def get_rollback_cmds(self):
        try:
            while True:
                yield self.rollback_cmds.pop()
        except IndexError:
            pass


# For readability
def transaction(*args, **kwargs):
    return Transaction(*args, **kwargs)
