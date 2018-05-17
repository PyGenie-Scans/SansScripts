Tutorial
********

.. highlight:: python
   :linenothreshold: 10

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


Boilerplate setup
=================

The commands below are for creating a simple testing system in the
tutorial.  This merely guarantees that the tutorial is always in sync
with the actual behaviour of the software.

>>> import logging
>>> import sys
>>> from src import *
>>> from src.genie import gen
>>> ch = logging.StreamHandler(sys.stdout)
>>> ch.setLevel(logging.DEBUG)
>>> logging.getLogger().setLevel(logging.DEBUG)
>>> logging.getLogger().addHandler(ch)

Basic examples
==============

The simplest possible measurement that

First, we'll just do a simple measurement on the main detector for 600
frames.

>>> measure("Sample Name", frames=600)
Setup Larmor for event
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0

The `measure` command is the primary entry point for all types of SANS
measurement.  We can pass it a sample changer position if we wish to
measure at a specific location.

>>> measure("Sample Name", "AT", uamps=5)
Moving to sample changer position AT
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0

A couple of things changed with this new command.  First, I've
measured for 5 µamps instead of the 600 frames we did before.  The
measure command will take and of the time commands that genie_python's
`waitfor` command will accept, though `uamps`, `frames`, and `seconds`
will almost always be the ones which are needed.  Secondly, we've
passed sample position AT in as the position parameter and the
instrument has dutifully moved into position AT before starting the
measurement.  Finally, you'll notice that there is no message about
putting the instrument in event mode.  Since we were already in event
mode, the instrument didn't perform the redundant step.

>>> measure("Sample Name", CoarseZ=25, uamps=5, thickness=2.0, trans=True)
Moving CoarseZ to 25
Setup Larmor for transmission
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=2.0

Here we are directly setting the moving the CoarseZ motor on the
sample stack to our desired position, instead of just picking a
position for the sample changer.  We have also recorded that this run
is on a 2 mm sample, unlike our previous 1mm runs.  Finally, the
instrument has converted into transmission mode, setting the
appropriate wiring tables and moving the m4 monitor into the beam.

>>> measure("Sample Name", "CT", SampleX=10, uamps=5)
Moving to sample changer position CT
Moving SampleX to 10
Setup Larmor for event
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0

We can combine a sample changer position with motor movements.  This
is useful for custom mounting that may not perfectly align with the
sample changer positions.  Alternately, since *any* block can be set
in the measure command, this can also be used to set temperatures and
other sample environment parameters.

>>> def weird_place():
...   gen.cset(Translation=100)
...   gen.cset(CoarseZ=-75)
>>> measure("Sample Name", weird_place, uamps=10)
Moving to position weird_place
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0

Finally, if the experiment requires a large number of custom
positions, they can be set independently in their own functions.
Measure can then move to that position as though it were a standard
sample changer position.


Automated script checking
=========================

    This module includes a decorator `user_script` that can be added
    to the front of any user function.  This will allow the scripting
    system to scan the script for common problems before it is run,
    ensuring that problems are noticed immediately and not at one in
    the morning.  All that's required of the user is putting
    `@user_script` on the line before any functions that they define.

    >>> @user_script
    ... def trial():
    ...     measure("Test1", "BT", uamps=30)
    ...     measure("Test2", "VT", uamps=30)
    ...     measure("Test1", "BT", trans=True, uanps=10)
    ...     measure("Test2", "VT", trans=True, uamps=10)
    >>> trial()
    Traceback (most recent call last):
    ...
    RuntimeError: Position VT does not exist

    What may not be immediately obvious from reading is that this
    error message occurs instantly, not forty five minutes
    into the run after the first measurement has already been
    performed.  Fixing the "VT" positions to "CT" then gives:

    >>> @user_script
    ... def trial():
    ...     measure("Test1", "BT", uamps=30)
    ...     measure("Test2", "TT", uamps=30)
    ...     measure("Test1", "BT", trans=True, uanps=10)
    ...     measure("Test2", "TT", trans=True, uamps=10)
    >>> trial()
    Traceback (most recent call last):
	...
    RuntimeError: Unknown Block uanps

    Again, an easy typo to make at midnight that normally would not be
    found until two in the morning.

    >>> @user_script
    ... def trial():
    ...     measure("Test1", "BT", uamps=30)
    ...     measure("Test2", "TT", uamps=30)
    ...     measure("Test1", "BT", trans=True, uamps=10)
    ...     measure("Test2", "TT", trans=True, uamps=10)
    >>> trial() #doctest:+ELLIPSIS
    The script should finish in 2.0 hours
    ...
    Thickness=1.0

    Once the script has been validated, which should happen nearly
    instantly, the program will print an estimate of the time needed
    for the script and the approximate time of completion (not shown).
    It will then run the script for real.

Under the hood
==============

>>> gen.reset_mock()
>>> measure("Test", "BT", uamps=15)
Moving to sample changer position BT
Setup Larmor for event
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0

This command returns no result, but should cause a large number of
actions to be run through genie-python.  We can verify those actions
through the mock genie object that's created when the actual
genie-python isn't found.

>>> print(gen.mock_calls)
[call.get_runstate(),
 call.cset(SamplePos='BT'),
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
 call.change(title='Test_SANS'),
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
>>> measure("Test" "CT", uamps=15, thickness=2.0)
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=2.0
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
>>> measure("Test" "CT", trans=True, uamps=3)
Setup Larmor for transmission
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0
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
