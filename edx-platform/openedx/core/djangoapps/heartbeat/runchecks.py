from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def runchecks(include_extended=False):
    """
    Iterates through a tuple of systems checks, then returns a dictionary containing the check name as the key, and a
    dict containing a status boolean and string describing the status, including any failure or error messages
    """
    response_dict = {}

    list_of_checks = list(settings.HEARTBEAT_CHECKS)
    if include_extended:
        list_of_checks += settings.HEARTBEAT_EXTENDED_CHECKS

    for path in list_of_checks:
        module, _, attr = path.rpartition('.')
        try:
            if module[0] == '.':  # Relative path, assume relative to this app
                mod = import_module(module, __package__)
            else:
                mod = import_module(module)
            func = getattr(mod, attr)

            check_name, is_ok, message = func()
            response_dict[check_name] = {
                'status': is_ok,
                'message': message
            }
        except ImportError as e:
            raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "%s" callable' % (module, attr))

    return response_dict
