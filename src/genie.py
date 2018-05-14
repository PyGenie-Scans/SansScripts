import mock
mock_gen = mock.Mock()
mock_gen._state = "SETUP"


def begin():
    mock_gen._state = "RUNNING"


def end():
    mock_gen._state = "SETUP"


mock_gen.begin.side_effect = begin
mock_gen.end.side_effect = end
mock_gen.get_runstate.side_effect = lambda: mock_gen._state

mock_gen._sample_pars = {
    "GEOMETRY": "Flat Plate",
    "WIDTH": 10,
    "HEIGHT": 10,
    "THICKNESS": 1}
mock_gen.get_sample_pars.side_effect = lambda: mock_gen._sample_pars


def change_sample_pars(key, value):
    if key.upper() == "THICK":
        mock_gen._sample_pars["THICKNESS"] = value


mock_gen.change_sample_par.side_effect = change_sample_pars

try:
    import genie_python.genie as gen
except ImportError:
    gen = mock_gen
