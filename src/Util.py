from functools import wraps
import logging
from logging import info


class CustomFormatter(logging.Formatter):
    def format(self, rec):
        return rec.levelname


# create logger
logger = logging.getLogger('simple_example')

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = CustomFormatter()

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def dae_setter(f):
    """Declare that a method sets the DAE wiring table

    This decorator was designed to work on subclasses of the
    ScanningInstrument class.  The following functionality is added
    into the class

    1) If the wiring tables are already in the correct state, the function
    returns immediately without taking any other actions
    2) If the wiring tables are in a different state, the change to the wiring
    tables is printed to the prompt before performing the actual change

    #1 of the above is the most important, as it allows the wiring
    tables to be set on any function call without worrying about
    wasting time reloading an existing configuration

    Please note that this decorator assumes that the title of the
    method begins with "setup_dae_", followed by the new of the state
    of the wiring table.

    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        request = f.__name__[10:]
        if request == self._dae_mode:
            return
        info("Setup {} for {}".format(type(self).__name__,
                                      request.replace("_", " ")))
        f(self, *args, **kwargs)
        self._dae_mode = request
    return wrapper


SCALES = {"uamps": 90, "frames": 0.1, "seconds": 1,
          "minutes": 60, "hours": 3600}


def wait_time(call):
    name, args, kwargs = call
    if name != "waitfor":
        return 0
    key = kwargs.keys()[0]
    return SCALES[key] * kwargs[key]


def pretty_print_time(s):
    from datetime import timedelta, datetime
    hours = s/3600.0
    delta = timedelta(0, s)
    skeleton = "The script should finish in {} hours\nat {}"
    return skeleton.format(hours, delta+datetime.now())



def user_script(f):
    """Perform some sanity checking on a user script before it is run"""
    @wraps(f)
    def inner(*args, **kwargs):
        from genie import mock_gen
        from mock import Mock
        code = f.__name__ + "("
        code += ", ".join(args)
        for k in kwargs:
            code += ", " + k + "=" + kwargs[k]
        code += ")"
        mock_gen.reset_mock()
        logging.info("Validating Script {}".format(f.__name__))
        logging.getLogger().disabled = True
        try:
            eval(code, {"gen": mock_gen, "logging": Mock()}, {f.__name__: f})
        finally:
            logging.getLogger().disabled = False
        calls = mock_gen.mock_calls
        time = sum([wait_time(call) for call in calls])
        logging.info(pretty_print_time(time))
        f(*args, **kwargs)
    return inner
