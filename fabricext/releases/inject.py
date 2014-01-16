'''Fabric task injection class'''

import inspect

from fabric import state
from fabric.tasks import WrappedCallableTask


def methodtask(*args, **kwargs):
    '''Adds metadata to a class method for injection

    This decorator adds metadata to a class method, which is used when
    injecting the method as a task into Fabric's command list.
    '''
    def inner(fn):
        fn.task = lambda x: WrappedCallableTask(x, *args, **kwargs)
        return fn

    try:
        if callable(args[0]):
            return inner(args[0])
    except IndexError:
        pass
    return inner


class TaskInjector(object):

    def include_tasks(self, namespace=None):
        '''Inject functions into Fabric's command state'''
        for (name, fn) in inspect.getmembers(self.__class__):
            if isinstance(fn, WrappedCallableTask):
                state.comands[name] = fn
            elif hasattr(fn, 'task'):
                try:
                    # Insert directly into Fabric command state
                    wrapped = fn.task(getattr(self, name))
                    state.commands[wrapped.name] = wrapped
                    state.env.new_style_tasks = True
                except:
                    pass
