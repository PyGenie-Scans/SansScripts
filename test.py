import Instrument
from genie import gen

Instrument.measure_changer("BT", title="test", sanstrans="TRANS", uamps=3)
Instrument.measure_changer("BT", title="test", sanstrans="SANS", uamps=15)
Instrument.measure_changer("BT", title="test", sanstrans="SANS", uamps=15)

print(gen.mock_calls)
