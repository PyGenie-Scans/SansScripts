"""Useful utilities for scriping"""
from functools import wraps
import logging
from logging import info


def dae_setter(inner):
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
    @wraps(inner)
    def wrapper(self, *args, **kwargs):
        """Memoize the dae mode"""
        request = inner.__name__[10:]
        if request == self._dae_mode:  # pylint: disable=protected-access
            return
        info("Setup {} for {}".format(type(self).__name__,
                                      request.replace("_", " ")))
        inner(self, *args, **kwargs)
        self._dae_mode = request  # pylint: disable=protected-access
    return wrapper


SCALES = {"uamps": 90, "frames": 0.1, "seconds": 1,
          "minutes": 60, "hours": 3600}


def wait_time(call):
    """Calculate the time spent waiting by a mock wait call."""
    name, _, kwargs = call
    if name != "waitfor":
        return 0
    key = kwargs.keys()[0]
    return SCALES[key] * kwargs[key]


def pretty_print_time(seconds):
    """Given a number of seconds, generate a human readable time string."""
    from datetime import timedelta, datetime
    hours = seconds/3600.0
    delta = timedelta(0, seconds)
    skeleton = "The script should finish in {} hours\nat {}"
    return skeleton.format(hours, delta+datetime.now())


def user_script(script):
    """Perform some sanity checking on a user script before it is run"""
    @wraps(script)
    def inner(*args, **kwargs):
        """Mock run a script before running it for real."""
        from mock import Mock
        from .genie import mock_gen
        code = script.__name__ + "("
        code += ", ".join(args)
        for k in kwargs:
            code += ", " + k + "=" + kwargs[k]
        code += ")"
        mock_gen.reset_mock()
        logging.getLogger().disabled = True
        try:
            eval(code,  # pylint: disable=eval-used
                 {"gen": mock_gen, "logging": Mock()},
                 {script.__name__: script})
        finally:
            logging.getLogger().disabled = False
        calls = mock_gen.mock_calls
        time = sum([wait_time(call) for call in calls])
        logging.info(pretty_print_time(time))
        script(*args, **kwargs)
    return inner
