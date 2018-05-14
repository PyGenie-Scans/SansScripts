import logging
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

    gen._sample_pars = {
        "GEOMETRY": "Flat Plate",
        "WIDTH": 10,
        "HEIGHT": 10,
        "THICKNESS": 1}
    gen.get_sample_pars.side_effect = lambda: gen._sample_pars

    def change_sample_pars(key, value):
        if key.upper() == "THICK":
            gen._sample_pars["THICKNESS"] = value
    gen.change_sample_par.side_effect = change_sample_pars
