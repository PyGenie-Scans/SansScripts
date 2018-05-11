try:
    import genie_python.genie as gen
except ImportError:
    import mock
    gen = mock.Mock()
    gen._state = "SETUP"

    def begin():
        gen._state = "RUNNING"

    def end():
        gen._state = "SETUP"

    gen.begin.side_effect = begin
    gen.end.side_effect = end
    gen.get_runstate.side_effect = lambda: gen._state

    gen.get_sample_pars.return_value = {
        "GEOMETRY": "Flat Plate",
        "WIDTH": 10,
        "HEIGHT": 10,
        "THICKNESS": 1}
