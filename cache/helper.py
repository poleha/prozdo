from . import constants
from django.db.models import Model

def rec_getattr(obj, attr):
    try:
        if '.' not in attr:
            try:
                return getattr(obj, attr)
            except:
                return obj.get(attr, None)
        else:
            L = attr.split('.')
            return rec_getattr(getattr(obj, L[0]), '.'.join(L[1:]))
    except:
        return None

def make_key_from_args(args, kwargs):
    res_args = ''
    for arg in args + tuple(kwargs.values()):
        if isinstance(arg, tuple(constants.CACHED_METHOD_SPECIAL_CASES.keys())):
            res_arg = type(arg).__name__
            for v in constants.CACHED_METHOD_SPECIAL_CASES[type(arg)]:
                res_arg += '_' + str(rec_getattr(arg, v))
            res_args += '_' + res_arg
        elif isinstance(arg, Model):
            res_args += '{0}-{1}'.format(type(arg).__name__, arg.pk)
        elif isinstance(arg, str):
            res_args += '_' + arg
        else:
            res_args += '_' + str(arg)
    return res_args