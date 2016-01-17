import logging
import traceback
import importlib


logger = logging.getLogger("barython")


def safe_import(module_name, class_name):
    """
    try to import a module, and if it fails because an ImporError
    it logs on WARNING, and logs the traceback on DEBUG level

    Thanks for qtile for this function
    """
    if type(class_name) is list:
        for name in class_name:
            safe_import(module_name, name)
        return
    package = __package__
    # python 3.2 don't set __package__
    if not package:
        package = __name__
    try:
        module = importlib.import_module(module_name, package)
        globals()[class_name] = getattr(module, class_name)
    except ImportError as error:
        msg = "Can't Import Widget: '%s.%s', %s"
        logger.warning(msg % (module_name, class_name, error))
        logger.debug(traceback.format_exc())


# safe_import(".date", "Date")
