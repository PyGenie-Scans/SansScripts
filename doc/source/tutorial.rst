Tutorial
********

.. highlight:: python
   :linenothreshold: 20

.. py:currentmodule:: src.Instrument


Design Goals
============

We desire the following traits in the scripting system

Universality
------------

A script written on one beamline should be able to run on *any*
beamline, as long as the relevant physical hardware is in place.

User simplicity
---------------

The user should be able to perform measurements with a minimum of fuss
or boilerplate.

Composability
-------------

The user should be able to combine the building blocks from this
system and create more complicated scripts from them.  Since the
underlying blocks are beamline independent, the final script should be
similarly portable.

Stability
---------

Scripting problems should be detected as quickly as possible.  Bad
scripts should fail immediately, not in the middle of the night when
there's no one there to see it.

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
Measuring Sample Name_SANS for 600 frames

The :py:meth:`ScanningInstrument.measure` command is the primary entry
point for all types of SANS measurement.  We can pass it a sample
changer position if we wish to measure at a specific location.

>>> measure("Sample Name", "AT", uamps=5)
Moving to sample changer position AT
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0
Measuring Sample Name_SANS for 5 uamps

A couple of things changed with this new command.  First, I've
measured for 5 µamps instead of the 600 frames we did before.  The
measure command will take and of the time commands that genie_python's
:py:meth:`waitfor` command will accept, though :py:attr:`uamps`, :py:attr:`frames`, and :py:attr:`seconds`
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
Measuring Sample Name_TRANS for 5 uamps

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
Measuring Sample Name_SANS for 5 uamps

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
Measuring Sample Name_SANS for 10 uamps

Finally, if the experiment requires a large number of custom
positions, they can be set independently in their own functions.
Measure can then move to that position as though it were a standard
sample changer position.

>>> setup_dae_bsalignment()
Setup Larmor for bsalignment
>>> measure("Beam stop", frames=300, dae_fixed=True)
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0
Measuring Beam stop_SANS for 300 frames
>>> measure("Beam stop", frames=300)
Setup Larmor for event
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0
Measuring Beam stop_SANS for 300 frames

By default, when taking a sans measurement, the
:py:meth:`ScanningInstrument.measure` function puts the instrument in
event mode.  Similarly, trans measurements are always in transmission
mode.  Setting the dae_fixed property to ``True`` ignores the default
mode and maintains whatever mode the instrument is currently in.

Automated script checking
=========================

.. py:currentmodule:: src.Util

This module includes a decorator :py:meth:`user_script` that can be
added to the front of any user function.  This will allow the
scripting system to scan the script for common problems before it is
run, ensuring that problems are noticed immediately and not at one in
the morning.  All that's required of the user is putting
``@user_script`` on the line before any functions that they define.

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

What may not be immediately obvious from reading is that this error
message occurs instantly, not forty five minutes into the run after
the first measurement has already been performed.  Fixing the "VT"
positions to "CT" then gives:

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
Measuring Test2_TRANS for 10 uamps

Once the script has been validated, which should happen nearly
instantly, the program will print an estimate of the time needed for
the script and the approximate time of completion (not shown).  It
will then run the script for real.

Large script handling
=====================

The :py:meth:`ScanningInstrument.measure_file` function allows the user to define everything in an
CSV file with excel and then run it through python.

For the example below, test.csv looks like

.. csv-table:: test.csv
  :file: ../../tests/test.csv
  :header-rows: 1

>>> measure_file("tests/test.csv") #doctest:+ELLIPSIS
The script should finish in 3.0 hours
...
Measuring Sample5_TRANS for 20 uamps

The particular keyword argument to the
:py:meth:`ScanningInstrument.measure` function is given in the header
on the first line of the file.  Each subsequent line represents a
single run and the value of each cell in the line is the value of that
keyword argument for the header.  If an argument is left blank, then
the keyword's default value is used.  The boolean values True and
False are case insensitive, but all other strings retain their case.

.. csv-table:: bad_julabo.csv
  :file: ../../tests/bad_julabo.csv
  :header-rows: 1

>>> measure_file("tests/bad_julabo.csv") #doctest:+ELLIPSIS
Traceback (most recent call last):
...
RuntimeError: Unknown Block Julabo

.. py:currentmodule:: src.Util

Each CSV file is run through the :py:func:`user_script`
function, so the script will be checked for errors before being run.
In the example above, the user set the column header to "Julabo", but
the actual block name is "Julabo1_SP".

If we fix the script file

.. csv-table:: good_julabo.csv
  :file: ../../tests/good_julabo.csv
  :header-rows: 1

>>> measure_file("tests/good_julabo.csv") #doctest:+ELLIPSIS
The script should finish in 0.5 hours
...
Measuring Sample2_TRANS for 10 uamps

The scan then runs as normal.

Detector Status
===============

As an obvious sanity check, it is possible to check if the detector is on.

>>> detector_on()
True

We can also power cycle the detector.

>>> detector_on(False)
Waiting For Detector To Power Down (60s)
False

If we try to start a measurement with the detector off, the detector
will be turned back on.

>>> measure("Sample", frames=100)
The detector was off.  Turning on the detector
Waiting For Detector To Power Up (180s)
Setup Larmor for event
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0
Measuring Sample_SANS for 100 frames

Performing transmission measurements does not require the detector

>>> detector_on(False)
Waiting For Detector To Power Down (60s)
False
>>> measure("Sample", trans=True, frames=100)
Setup Larmor for transmission
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thickness=1.0
Measuring Sample_TRANS for 100 frames
>>> detector_on(True)
Waiting For Detector To Power Up (180s)
True

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
Measuring Test_SANS for 15 uamps

This command returns no result, but should cause a large number of
actions to be run through genie-python.  We can verify those actions
through the mock genie object that's created when the actual
genie-python isn't found.

>>> print(gen.mock_calls)
[call.get_runstate(),
 call.get_pv('IN: LARMOR: CAEN: hv0: 0: 8: status'),
 call.get_pv('IN: LARMOR: CAEN: hv0: 0: 9: status'),
 call.get_pv('IN: LARMOR: CAEN: hv0: 0: 10: status'),
 call.get_pv('IN: LARMOR: CAEN: hv0: 0: 11: status'),
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

  2
    Ensure that the instrument is ready to start a measurement
  3-6
    Check that the detector is on
  7
    Move the sample into position
  8-20
    Put the instrument in event mode
  21-23
    Move the M4 transmission monitor out of the beam
  24
    Set the sample thickness
  25
    Print and log the sample parameters
  26
    Set the sample title
  27
    Start the measurement.
  28
    Wait the requested time
  29
    Stop the measurement.
