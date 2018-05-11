import src.Instrument
from src.genie import gen

src.Instrument.measure_changer("BT", title="test", sanstrans="TRANS", uamps=3)
src.Instrument.measure_changer("BT", title="test", sanstrans="SANS", uamps=15)
src.Instrument.measure_changer("BT", title="test", sanstrans="SANS", uamps=15)

print(gen.mock_calls)
