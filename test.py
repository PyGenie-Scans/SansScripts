from src import *
from src.genie import gen

measure_changer("BT", title="test", sanstrans="TRANS", uamps=3)
measure_changer("BT", title="test", sanstrans="SANS", uamps=15)
measure_changer("BT", title="test", sanstrans="SANS", uamps=15)

print(gen.mock_calls)
