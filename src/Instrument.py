"""The baseline for loading a scanning instrument

This module automatically detects the instrument it is being run on
and automatically loads the correct submodule.  The primary useage
method for this entire project is:

>   from SansScriping.Instrument import *

"""

from abc import ABCMeta, abstractmethod, abstractproperty
from functools import wraps
from logging import info, warning
from time import ctime

from six import add_metaclass
from genie import gen


def needs_setup(f):
    @wraps(f)
    def with_setup(*args, **kwargs):
        if gen.get_runstate() != "SETUP":
            raise RuntimeError("Cannot start a measuremnt in a measurement")
        return f(*args, **kwargs)
    return with_setup


@add_metaclass(ABCMeta)
class ScanningInstrument(object):
    """The base class for scanning measurement instruments."""

    _dae_mode = None
    title_footer = ""

    @abstractproperty
    def _poslist(self):
        """The list of named positions that the instrument can run through in
        the sample changer"""
        return []

    @abstractmethod
    def setup_dae_scanning(self):
        """Set the wiring tables for a scan"""
        pass

    @abstractmethod
    def setup_dae_nr(self):
        """Set the wiring tables for a neutron
        reflectivity measurement"""
        pass

    @abstractmethod
    def setup_dae_nrscanning(self):
        """Set the wiring tables for performing
        scans during neutron reflectivity"""
        pass

    @abstractmethod
    def setup_dae_event(self):
        """Set the wiring tables for event mode"""
        pass

    @abstractmethod
    def setup_dae_histogram(self):
        """Set the wiring tables for histogram mode"""
        pass

    @abstractmethod
    def setup_dae_event_fastsave(self):
        """Event mode with reduced detector histogram binning to decrease
        filesize."""
        pass

    @abstractmethod
    def setup_dae_transmission(self):
        """Set the wiring tables for a transmission measurement"""
        pass

    @abstractmethod
    def setup_dae_monotest(self):
        pass

    @abstractmethod
    def setup_dae_tshift(self):
        pass

    @abstractmethod
    def setup_dae_diffraction(self):
        pass

    @abstractmethod
    def setup_dae_polarised(self):
        pass

    @abstractmethod
    def setup_dae_bsalignment(self):
        """Configure wiring tables for beamstop alignment."""
        pass

    @abstractmethod
    def setup_dae_monitorsonly(self):
        pass

    @abstractmethod
    def setup_dae_resonantimaging(self):
        pass

    @abstractmethod
    def setup_dae_resonantimaging_choppers(self):
        pass

    @abstractmethod
    def setup_dae_4periods(self):
        pass

    @abstractmethod
    def _configure_sans_custom(self, size, mode):
        """The specific actions required by the instrument
        to run a SANS measurement (e.g. remove the monitor
        from the beam)"""
        pass

    @abstractmethod
    def _configure_trans_custom(self, size):
        """The specific actions required by the instrument
        to run a transmission measurement measurement (e.g.
        put the monitor in the beam"""
        pass

    @staticmethod
    @abstractmethod
    def set_aperature(size):
        """Set the beam aperature to the desired size
        Parameters
        ----------
        size : str
          The aperature size.  e.g. "Small" or "Medium"
          A blank string (the default value) results in
          the aperature not being changed.
          """

        pass

    def configure_sans(self, size="", mode='event'):
        """Setup to the instrument for a SANS measurement

        Parameters
        ----------
        size : str
          The aperature size.  e.g. "Small" or "Medium"
          A blank string (the default value) results in
          the aperature not being changed
        mode : str
          Whether to run the instrument in "event" or
          "histogram" mode.  Event mode is the default.
        """
        # setup to run in histogram or event mode
        self.title_footer = "_SANS"
        if mode.upper() == 'HISTOGRAM':
            self.setup_dae_histogram()
        else:
            self.setup_dae_event()
        self.set_aperature(size)
        self._configure_sans_custom(size, mode)

    def configure_trans(self, size=""):
        """Setup the instrument for a transmission measurement

        Parameters
        ----------
        size : str
          The aperature size.  e.g. "Small" or "Medium"
          A blank string (the default value) results in
          the aperature not being changed"""
        self.title_footer = "_TRANS"
        self.setup_dae_transmission()
        gen.waitfor_move()
        self.set_aperature(size)
        self._configure_trans_custom(self)

    def check_move_pos(self, pos):
        """Check whether the position is valid and return True or False"""
        if pos.upper() not in self._poslist:
            warning("Error in script, position {} does not exist".format(pos))
            return False
        return True

    def _measure(self, title, thickness, sanstrans, **kwargs):
        if sanstrans.upper() == 'TRANS':
            self.configure_trans()
        elif sanstrans.upper() == 'SANS':
            self.configure_sans()
        else:
            warning("Unknown measurement mode {}".format(sanstrans))
        gen.waitfor_move()
        gen.change_sample_par("Thick", thickness)
        info("Using the following Sample Parameters")
        self.printsamplepars()
        gen.change(title=title+self.title_footer)
        gen.begin()
        gen.waitfor(**kwargs)
        gen.end()

    @needs_setup
    def measure_changer(self, pos="", title="", thickness=1.0, sanstrans='',
                        **kwargs):
        """Measure SANS or TRANS at a given sample changer position If no
        position is given the sample stack will not move.  Accepts any
        of the waitfor keyword arguments to specify the length of the
        measurement.

        Parameters
        ==========
        pos = ""
          Sample changer position.  If blank, then the position isn't moved.
        title = ""
          title of the measurement
        thickness = 1.0
          The thickness of the sample in mm
        sanstrans = ''
          Whether to perform a 'SANS' measurement or a 'TRANS' measurement

        Returns
        =======
        None

        """
        # Check if a changer move is valid and if so move there if not
        # do nothing Make sure we only have 1 period just in case. If
        # more are needed write another function
        if pos:
            pos = pos.upper()
            if pos != "NONE" and self.check_move_pos(pos=pos):
                info("Moving to position "+pos+" "+ctime())
                gen.cset(SamplePos=pos)
        self._measure(title, thickness, sanstrans, **kwargs)

    @needs_setup
    def measure(self, xpos=None, ypos=None, coarsezpos=None, finezpos=None,
                title="", thickness=1.0, sanstrans='SANS', **kwargs):
        """Measure SANS or TRANS at a given sample stack position

        If no position is given the sample stack will not move Make
        sure we only have 1 period just in case. If more are needed
        write another function.

        Parameters
        ==========
        xpos
          X position of sample
        ypos
          y position of sample
        coarsezpos
          z position of sample on coarse motor
        finezpos
          z position of sample on fine motor
        title
          Measurement title
        thickness
          sample thickness in mm
        sanstrans
          whether to perform a sans or a trans measurement

        """
        move = {}
        if xpos is not None:
            gen.cset(SampleX=xpos)
            move["x"] = xpos
        if ypos is not None:
            gen.cset(Translation=ypos)
            move["y"] = ypos
        if coarsezpos is not None:
            gen.cset(CoarseZ=coarsezpos)
            move["CoarseZ"] = coarsezpos
        if finezpos is not None:
            gen.cset(FineZ=finezpos)
            move["FineZ"] = finezpos
        if move:
            positions = [str(k)+": "+str(move[k]) for k in move]
            info("Moving to position "+", ".join(positions))
            gen.waitfor_move()
        self._measure(title, thickness, sanstrans, **kwargs)

    @staticmethod
    def printsamplepars():
        """Display the basic sample parameters on the console."""
        pars = gen.get_sample_pars()
        for par in ["Geometry", "Width", "Height", "Thickness"]:
            info("{}={}".format(par, pars[par.upper()]))
