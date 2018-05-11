from src import measure_changer
from src.genie import gen

measure_changer("test", "BT", trans=True, uamps=3)
measure_changer("test", "BT", uamps=15)
measure_changer("test", uamps=15)

print(gen.mock_calls)
