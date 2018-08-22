"""This is the instrument implementation for the Zoom beamline."""
from logging import info
from .Instrument import ScanningInstrument
from .Util import dae_setter
from .genie import gen


class Zoom(ScanningInstrument):
    """This class handles the Zoom beamline"""

    _poslist = ['AB', 'BB', 'CB', 'DB', 'EB', 'FB', 'GB', 'HB', 'IB', 'JB',
                'KB', 'LB', 'MB', 'NB', 'OB', 'PB', 'QB', 'RB', 'SB', 'TB',
                'AT', 'BT', 'CT', 'DT', 'ET', 'FT', 'GT', 'HT', 'IT', 'JT',
                'KT', 'LT', 'MT', 'NT', 'OT', 'PT', 'QT', 'RT', 'ST', 'TT',
                '1CB', '2CB', '3CB', '4CB', '5CB', '6CB', '7CB',
                '8CB', '9CB', '10CB', '11CB', '12CB', '13CB', '14CB',
                '1CT', '2CT', '3CT', '4CT', '5CT', '6CT', '7CT',
                '8CT', '9CT', '10CT', '11CT', '12CT', '13CT', '14CT',
                '1WB', '2WB', '3WB', '4WB', '5WB', '6WB', '7WB',
                '8WB', '9WB', '10WB', '11WB', '12WB', '13WB', '14WB',
                '1WT', '2WT', '3WT', '4WT', '5WT', '6WT', '7WT',
                '8WT', '9WT', '10WT', '11WT', '12WT', '13WT', '14WT']

    def set_measurement_type(self, value):
        gen.set_pv("IN:ZOOM:PARS:SAMPLE:MEAS:TYPE", value)

    def set_measurement_label(self, value):
        gen.set_pv("IN:ZOOM:PARS:SAMPLE:MEAS:LABEL", value)

    def set_measurement_id(self, value):
        gen.set_pv("IN:ZOOM:PARS:SAMPLE:MEAS:ID", value)

    def setup_dae_scanning(self):
        raise NotImplemented("Scanning tables not yet set")

    def setup_dae_nr(self):
        raise NotImplemented("Neutron reflectivity tables not yet set")

    def setup_dae_nrscanning(self):
        raise NotImplemented(
            "Neutron reflectivity scanning tables not yet set")

    def setup_dae_event(self):
        raise NotImplemented("Event mode tables not yet set")

    def setup_dae_histogram(self):
        raise NotImplemented("Histogram mode tables not yet set")

    def setup_dae_transmission(self):
        raise NotImplemented("Transmission tables not yet set")

    def setup_dae_bsalignment(self):
        raise NotImplemented("Beam Stop Alignment tables not yet set")

    def set_aperature(size):
        raise NotImplemented("Aperature setting hasn't been written")

    def _detector_is_on():
        raise NotImplemented("Detector testing hasn't been written")

    def _detector_turn_on():
        raise NotImplemented("Detector toggling hasn't been written")

    def _detector_turn_off():
        raise NotImplemented("Detector toggling hasn't been written")
