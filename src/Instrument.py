"""The baseline for loading a scanning instrument

Each instrument will have its own module that declares a class
inheriting from ScanningInstrument.  The abstract base class is used
to ensure that the derived classes define the necessary methods to run
any generic scripts.

"""

from abc import ABCMeta, abstractmethod, abstractproperty
from logging import info, warning
from time import ctime

from six import add_metaclass
from genie import gen


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

    @staticmethod
    def _needs_setup():
        if gen.get_runstate() != "SETUP":
            raise RuntimeError("Cannot start a measuremnt in a measurement")

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

    def _measure(self, title, thickness, trans, **kwargs):
        if trans:
            self.configure_trans()
        else:
            self.configure_sans()
        gen.waitfor_move()
        gen.change_sample_par("Thick", thickness)
        info("Using the following Sample Parameters")
        self.printsamplepars()
        gen.change(title=title+self.title_footer)
        gen.begin()
        gen.waitfor(**kwargs)
        gen.end()

    def measure_changer(self, title, pos=None, thickness=1.0,
                        trans=False, **kwargs):
        """Measure SANS or TRANS at a given sample changer position. If no
        position is given the sample stack will not move.  Accepts any
        of the waitfor keyword arguments to specify the length of the
        measurement.

        Parameters
        ==========
        title : str
          title of the measurement
        pos : str
          Sample changer position.  If blank, then the position isn't moved.
        thickness : float
          The thickness of the sample in mm
        trans : bool
          Whether to perform a transmission measurement.  Sans is the default.

        Returns
        =======
        None

        """
        # Check if a changer move is valid and if so move there if not
        # do nothing Make sure we only have 1 period just in case. If
        # more are needed write another function
        self._needs_setup()
        if pos:
            pos = pos.upper()
            if self.check_move_pos(pos=pos):
                info("Moving to position "+pos+" "+ctime())
                gen.cset(SamplePos=pos)
            else:
                raise RuntimeError("Position {} does not exist.".format(pos))
        self._measure(title, thickness, trans, **kwargs)

    def measure(self, title, xpos=None, ypos=None, coarsezpos=None,
                finezpos=None, thickness=1.0, trans=False, **kwargs):
        """Measure SANS or TRANS at a given sample stack position

        If no position is given the sample stack will not move. The
        run time for the measurement can be given with the same
        keyword arguments used in waitfor.

        Parameters
        ==========
        xpos : float
          X position of sample
        ypos : float
          y position of sample
        coarsezpos : float
          z position of sample on coarse motor
        finezpos : float
          z position of sample on fine motor
        title : str
          Measurement title
        thickness : float
          sample thickness in mm
        trans : bool
          whether to perform a trans measurement.  By default, a Sans
          measurement is performed.

        """
        self._needs_setup()
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
        self._measure(title, thickness, trans, **kwargs)

    @staticmethod
    def printsamplepars():
        """Display the basic sample parameters on the console."""
        pars = gen.get_sample_pars()
        for par in ["Geometry", "Width", "Height", "Thickness"]:
            info("{}={}".format(par, pars[par.upper()]))
