'''Utility functions for releases'''

from fabric.api import *  # noqa
from fabric.tasks import _is_task, WrappedCallableTask


def execute_pseudo_task(fn=None, obj=None, name=None):
    '''Safely call a function as a WrappedCallableTask

    This alters the function `fn` and creates a
    :py:class:`WrappedCallableTask`, also updating host and role parameters to
    match the environment

    :param fn: function to alter
    :param obj: object to search on
    :param name: object function name as string
    '''
    try:
        # Alternate form of call
        if obj is not None and name is not None:
            fn = getattr(obj, name)
        if not callable(fn):
            raise ValueError(
                "Function `fn` must be callable, "
                "or function `name` must exist on object `obj`"
            )
        if not _is_task(fn):
            fn = WrappedCallableTask(fn)
        fn.hosts = env.hosts
    except AttributeError:
        pass
    else:
        execute(fn)
