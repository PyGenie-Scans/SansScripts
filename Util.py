from functools import wraps
import logging
from logging import info, warning

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
    
    This decorator was designed to work on subclasses of the ScanningInstrument class.
    The following functionality is added into the class
    
    1) If the wiring tables are already in the correct state, the function
    returns immediately without taking any other actions
    2) If the wiring tables are in a different state, the change to the wiring
    tables is printed to the prompt before performing the actual change
    
    #1 of the above is the most important, as it allows the wiring tables to
    be set on any function call without worrying about wasting time reloading
    an existing configuration
    
    Please note that this decorator assumes that the title of the method begins with
    "setup_dae_", followed by the new of the state of the wiring table.
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        request = f.__name__[10:]
        if request == self._dae_mode:
            return
        info("Setup {} for {}".format(type(self).__name__, request.replace("_"," ")))
        f(self, *args, **kwargs)
        self._dae_mode = request
    return wrapper
