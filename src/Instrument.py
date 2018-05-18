# -*- coding: utf-8 -*-
"""The baseline for loading a scanning instrument

Each instrument will have its own module that declares a class
inheriting from ScanningInstrument.  The abstract base class is used
to ensure that the derived classes define the necessary methods to run
any generic scripts.

"""

from abc import ABCMeta, abstractmethod, abstractproperty
from logging import info, warning
from six import add_metaclass
from .genie import gen

TIMINGS = ["uamps", "frames", "seconds", "minutes", "hours"]


def sanitised_timings(kwargs):
    """Include only the keyword arguments for run timings.

    Parameters
    ----------
    kwargs : dict
      A dictionary of keyword arguments

    Returns
    -------
    dict
      Keyword arguments accepted by gen.waitfor
    """
    result = {}
    for k in TIMINGS:
        if k in kwargs:
            result[k] = kwargs[k]
    return result


@add_metaclass(ABCMeta)
class ScanningInstrument(object):
    """The base class for scanning measurement instruments."""

    _dae_mode = None
    title_footer = ""

    @staticmethod
    def _generic_scan(detector, spectra, wiring, tcbs):
        """A utility class for setting up dae states

        On its own, it's not particularly useful, but
        letting subclasses provide default parameters
        simplifies creating new dae states.
        """
        gen.change(nperiods=1)
        gen.change_start()
        gen.change_tables(detector=detector)
        gen.change_tables(spectra=spectra)
        gen.change_tables(wiring=wiring)
        for tcb in tcbs:
            gen.change_tcb(**tcb)
        gen.change_finish()

    @abstractproperty
    def _poslist(self):
        """The list of named positions that the instrument can run through in
        the sample changer"""
        return []

    @staticmethod
    def _needs_setup():
        if gen.get_runstate() != "SETUP":
            raise RuntimeError("Cannot start a measurement in a measurement")

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
    def setup_dae_polarised(self):
        """Set the wiring tables for a polarisation measurement"""
        pass

    @abstractmethod
    def setup_dae_bsalignment(self):
        """Configure wiring tables for beamstop alignment."""
        pass

    @abstractmethod
    def setup_dae_monitorsonly(self):
        """Set the wiring tables to record only the monitors"""
        pass

    def _configure_sans_custom(self, size, mode):
        """The specific actions required by the instrument
        to run a SANS measurement (e.g. remove the monitor
        from the beam)"""
        pass

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
          the aperature not being changed."""
        pass

    @staticmethod
    @abstractmethod
    def detector_is_on():
        """Is the detector currently powered?"""
        return False

    @staticmethod
    @abstractmethod
    def detector_turn_on(delay=True):
        """Power on the detector

        Parameters
        ==========
        delay : bool
          Wait for the detector to warm up before continuing
        """
        return False

    @staticmethod
    @abstractmethod
    def detector_turn_off(delay=True):
        """Remove detector power

        Parameters
        ==========
        delay : bool
          Wait for the detector to cool down before continuing
        """
        return False

    def configure_sans(self, size="", dae_fixed=False):
        """Setup to the instrument for a SANS measurement

        Parameters
        ----------
        size : str
          The aperature size.  e.g. "Small" or "Medium"
          A blank string (the default value) results in
          the aperature not being changed
        dae_fixed : bool
          If False, the DAE will be set to event mode.
          Otherwise the DAE is left alone.
        """
        # setup to run in histogram or event mode
        self.title_footer = "_SANS"
        if not dae_fixed:
            self.setup_dae_event()
        self.set_aperature(size)
        self._configure_sans_custom(size, dae_fixed)

    def configure_trans(self, size="", dae_fixed=False):
        """Setup the instrument for a transmission measurement

        Parameters
        ----------
        size : str
          The aperature size.  e.g. "Small" or "Medium"
          A blank string (the default value) results in
          the aperature not being changed
        dae_fixed : bool
          If False, the DAE will be set to event mode.
          Otherwise the DAE is left alone.
        """
        self.title_footer = "_TRANS"
        if not dae_fixed:
            self.setup_dae_transmission()
        gen.waitfor_move()
        self.set_aperature(size)
        self._configure_trans_custom(self, dae_fixed=dae_fixed)

    def check_move_pos(self, pos):
        """Check whether the position is valid and return True or False

        Parameters
        ----------
        pos : str
          The sample changer position

        """
        if pos.upper() not in self._poslist:
            warning("Error in script, position {} does not exist".format(pos))
            return False
        return True

    def _measure(self, title, thickness, trans, dae_fixed, **kwargs):
        if trans:
            self.configure_trans(dae_fixed=dae_fixed)
        else:
            self.configure_sans(dae_fixed=dae_fixed)
        gen.waitfor_move()
        gen.change_sample_par("Thick", thickness)
        info("Using the following Sample Parameters")
        self.printsamplepars()
        gen.change(title=title+self.title_footer)
        gen.begin()
        info("Measuring {title:} for {time:} {units:}".format(
            title=title+self.title_footer,
            units=list(kwargs.keys())[0],
            time=kwargs[list(kwargs.keys())[0]]))
        gen.waitfor(**kwargs)
        gen.end()

    def measure(self, title, pos=None, thickness=1.0, trans=False,
                dae_fixed=False, **kwargs):
        """Take a sample measurement.

        Parameters
        ==========
        title : str
          The title for the measurement.  This is the only required parameter.
        pos
          The sample position.  This can be a string with the name of
          a sample position or it can be a function which moves the
          detector into the desired position.  If left undefined, the
          instrument will take the measurement in its current
          position.
        thickness : float
          The thickness of the sample in millimeters.  The default is 1mm.
        trans : bool
          Whether to perform a transmission run instead of a sans run.
        dae_fixed : bool
          If True, then :py:meth:`measure` will not change the DAE mode before
          starting the measurement.  This is useful if you want to use
          a different DAE mode than the default.
        **kwargs
          This function takes two kinds of keyword arguments.  If
          given a block name, it will move that block to the given
          position.  If given a time duration, then that will be the
          duration of the run.

        Examples
        ========

        >>> measure("H2O", frames=900)

        Perform a SANS measurment in the current position on a 1 mm
        thick water sample until the proton beam has released 900
        proton pulses (approx 15 minutes).

        >>> measure("D2O", "LT", thickness=2.0, trans=True, Phi=3, uamps=10)

        Move to sample changer position LT, then adjust the CoarseZ
        motor to 38 mm.  Finally, take a transmission measurement on a
        2 mm thick deuterium sample for 10 µA hours of proton
        current. (approx 15 minutes).

        """
        self._needs_setup()
        if not self.detector_is_on() and not trans:
            warning("The detector was off.  Turning on the detector")
            self.detector_turn_on()
        moved = False
        if pos:
            if isinstance(pos, str):
                if self.check_move_pos(pos=pos):
                    info("Moving to sample changer position {}".format(pos))
                    gen.cset(SamplePos=pos)
                else:
                    raise RuntimeError(
                        "Position {} does not exist".format(pos))
            elif callable(pos):
                info("Moving to position {}".format(pos.__name__))
                pos()
            else:
                raise TypeError("Cannot understand position {}".format(pos))
        for arg in kwargs:
            if arg in TIMINGS:
                continue
            info("Moving {} to {}".format(arg, kwargs[arg]))
            gen.cset(arg, kwargs[arg])
            moved = True
        if moved:
            gen.waitfor_move()
        self._measure(title, thickness, trans, dae_fixed=dae_fixed,
                      **sanitised_timings(kwargs))

    @staticmethod
    def printsamplepars():
        """Display the basic sample parameters on the console."""
        pars = gen.get_sample_pars()
        for par in ["Geometry", "Width", "Height", "Thickness"]:
            info("{}={}".format(par, pars[par.upper()]))
