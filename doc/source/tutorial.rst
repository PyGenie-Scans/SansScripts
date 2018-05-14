Tutorial
********

.. highlight:: python
   :linenothreshold: 5

Design Goals
============

We desire the following traits in the scripting system

Universality
------------

A script written on one beamline should be able to run on *any*
beamline, as long as the relevant physical hardware is in place.

User simplicity
---------------

The user should be able to perform measurements with a minimum of fuss or boilerplate

Composability
-------------

The user should be able to combine the building blocks from this
system and create more complicated scripts from them.  Since the
underlying blocks are beamline independent, the final script should be
similarly portable.


Examples
========

>>> from src import *
>>> from src.genie import gen

First, we'll do a simple measurement on the sample changer

>>> measure_changer("Test" "BT", uamps=15)

This command returns no result, but should cause a large number of
actions to be run through genie-python.  We can verify those actions
through the mock genie object that's created when the actual
genie-python isn't found.

>>> print(gen.mock_calls)
[call.get_runstate(),
 call.change(nperiods=1),
 call.change_start(),
 call.change_tables(detector='C:\\Instrument\\Settings\\Tables\\detector.dat'),
 call.change_tables(spectra='C:\\Instrument\\Settings\\Tables\\spectra_1To1.dat'),
 call.change_tables(wiring='C:\\Instrument\\Settings\\Tables\\wiring_event.dat'),
 call.change_tcb(high=100000.0, log=0, low=5.0, step=100.0, trange=1),
 call.change_tcb(high=0.0, log=0, low=0.0, step=0.0, trange=2),
 call.change_tcb(high=100000.0, log=0, low=5.0, regime=2, step=2.0, trange=1),
 call.change_finish(),
 call.cset(T0Phase=0),
 call.cset(TargetDiskPhase=2750),
 call.cset(InstrumentDiskPhase=2450),
 call.waitfor_move(),
 call.cset(m4trans=200.0),
 call.waitfor_move(),
 call.waitfor_move(),
 call.change_sample_par('Thick', 1.0),
 call.get_sample_pars(),
 call.change(title='TestBT_SANS'),
 call.begin(),
 call.waitfor(uamps=15),
 call.end()]

That's quite a few commands, so it's worth running through them.

  2-15
    Put the instrument in event mode
  16-18
    Move the M4 transmission monitor out of the beam
  19
    Set the sample thickness
  20
    Print and log the sample parameters
  21
    Set the sample title
  22
    Start the measurement.
  23
    Wait the requested time
  24
    Stop the measurement.

The
first thirteen lines put the instrument into event mode for taking a
sans measurement and set the chopper to the correct value.  The next
three lines move the M4 transmission monitor out of the beam.  The
sample's thickness is then set and the sample parameters logged.
After setting the title, the script finally takes a measurement.

We can then repeat the measurement on a different sample position.

>>> gen.reset_mock()
>>> measure_changer("Test" "CT", uamps=15, thickness=2.0)
>>> print(gen.mock_calls)
[call.get_runstate(),
 call.waitfor_move(),
 call.cset(m4trans=200.0),
 call.waitfor_move(),
 call.waitfor_move(),
 call.change_sample_par('Thick', 2.0),
 call.get_sample_pars(),
 call.change(title='TestCT_SANS'),
 call.begin(),
 call.waitfor(uamps=15),
 call.end()]

Notice that far fewer commands are being run now.  This is because
we've already set the instrument in event mode and mode, so those bits
are not re-run until the wiring tables change.  To see that, we'll
take a transmission measurement.

>>> gen.reset_mock()
>>> measure_changer("Test" "CT", trans=True, uamps=3)
>>> print(gen.mock_calls)
[call.get_runstate(),
 call.change_sync('isis'),
 call.change(nperiods=1),
 call.change_start(),
 call.change_tables(detector='C:\\Instrument\\Settings\\Tables\\detector_monitors_only.dat'),
 call.change_tables(spectra='C:\\Instrument\\Settings\\Tables\\spectra_monitors_only.dat'),
 call.change_tables(wiring='C:\\Instrument\\Settings\\Tables\\wiring_monitors_only.dat'),
 call.change_tcb(high=100000.0, log=0, low=5.0, step=100.0, trange=1),
 call.change_tcb(high=0.0, log=0, low=0.0, step=0.0, trange=2),
 call.change_finish(),
 call.cset(T0Phase=0),
 call.cset(TargetDiskPhase=2750),
 call.cset(InstrumentDiskPhase=2450),
 call.waitfor_move(),
 call.waitfor_move(),
 call.cset(m4trans=0.0),
 call.waitfor_move(),
 call.waitfor_move(),
 call.change_sample_par('Thick', 1.0),
 call.get_sample_pars(),
 call.change(title='TestCT_TRANS'),
 call.begin(),
 call.waitfor(uamps=3),
 call.end()]

You can see that a different set of monitor only wiring tables are
loaded, plus the M4 monitor is now moved back into the beam.  Finally,
"TRANS" is appened onto the run name, instead of the "SANS" that was
used before.
