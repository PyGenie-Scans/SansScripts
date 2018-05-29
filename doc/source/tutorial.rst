Tutorial
********

.. highlight:: python
   :linenothreshold: 20

.. py:currentmodule:: src.Instrument

Boilerplate setup
=================

The commands below are for creating a simple testing system in the
tutorial.  This merely guarantees that the tutorial is always in sync
with the actual behaviour of the software.  The tutorial proper begins
in the next section.

>>> import logging
>>> import sys
>>> ch = logging.StreamHandler(sys.stdout)
>>> ch.setLevel(logging.DEBUG)
>>> logging.getLogger().setLevel(logging.DEBUG)
>>> logging.getLogger().addHandler(ch)

Basic examples
==============

First, we'll just do a simple measurement on the main detector for 600
frames.

>>> from src import *
>>> from src.genie import gen
>>> measure("Sample Name", frames=600)
Setup Larmor for event
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring Sample Name_SANS for 600 frames

The :py:meth:`ScanningInstrument.measure` command is the primary entry
point for all types of SANS measurement.  We can pass it a sample
changer position if we wish to measure at a specific location.

>>> measure("Sample Name", "QT", aperature="Medium", uamps=5)
Moving to sample changer position QT
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring Sample Name_SANS for 5 uamps

A couple of things changed with this new command.

1. I've measured for 5 µamps instead of the 600 frames we did before.
   The measure command will take and of the time commands that
   genie_python's ``waitfor`` command will accept, though ``uamps``,
   ``frames``, and ``seconds`` will almost always be the ones which
   are needed.

2. We've passed sample position QT in as the position parameter and
   the instrument has dutifully moved into position QT before starting
   the measurement.

#. We specified the beam size.  The individual beamlines will have the
   opportunity to decide their own aperature settings, but they should
   hopefully reach a consensus on the names.

#. You'll notice that there is no message about putting the instrument
   in event mode.  Since we were already in event mode, the instrument
   didn't perform the redundant step.

>>> measure("Sample Name", CoarseZ=25, uamps=5, thickness=2.0, trans=True)
Setup Larmor for transmission
Moving CoarseZ to 25
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=2.0
Measuring Sample Name_TRANS for 5 uamps

Here we are directly setting the CoarseZ motor on the sample stack to
our desired position, instead of just picking a position for the
sample changer.  We have also recorded that this run is on a 2 mm
sample, unlike our previous 1 mm runs.  Finally, the instrument has
converted into transmission mode, setting the appropriate wiring
tables and moving the M4 monitor into the beam.

>>> measure("Sample Name", "CT", SampleX=10, Julabo1_SP=35, uamps=5)
Setup Larmor for event
Moving to sample changer position CT
Moving Julabo1_SP to 35
Moving SampleX to 10
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring Sample Name_SANS for 5 uamps

We can combine a sample changer position with motor movements.  This
is useful for custom mounting that may not perfectly align with the
sample changer positions.  Alternately, since any block can be set
within the measure command, it is also possible to set temperatures
and other beam-line parameters for a measurement.

>>> def weird_place():
...   gen.cset(Translation=100)
...   gen.cset(CoarseZ=-75)
>>> measure("Sample Name", weird_place, Julabo1_SP=37, uamps=10)
Moving to position weird_place
Moving Julabo1_SP to 37
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring Sample Name_SANS for 10 uamps

Finally, if the experiment requires a large number of custom
positions, they can be set independently in their own functions.
Measure can then move to that position as though it were a standard
sample changer position.  It's still possible to override or amend
these custom positions with measurement specific values, as we have
done above with the Julabo temperature again.

>>> set_default_dae(setup_dae_bsalignment)
>>> measure("Beam stop", frames=300)
Setup Larmor for bsalignment
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring Beam stop_SANS for 300 frames

The default DAE mode for all SANS measurements is event mode.  This
can be overridden with the
:py:meth:`ScanningInstrument.set_default_dae` function, which will
assign a new default SANS method.  This new event mode will be used
for all future SANS measurements.  For brevity, the
:py:meth:`ScanningInstrument.set_default_dae` will also take a string
argument.  The first line can also be run as

>>> set_default_dae("bsalignment")

>>> measure("Beam stop", dae="event", frames=300)
Setup Larmor for event
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring Beam stop_SANS for 300 frames

The :py:meth:`ScanningInstrument.measure` function also has a ``dae``
keyword parameter that is automatically passed to
:py:meth:`setup_default_dae`.  The above example puts the instrument
back into event mode.

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
...     measure("Test2", "CT", uamps=30)
...     measure("Test1", "BT", trans=True, uanps=10)
...     measure("Test2", "CT", trans=True, uamps=10)
>>> trial()
Traceback (most recent call last):
...
RuntimeError: Unknown Block uanps

Again, an easy typo to make at midnight that normally would not be
found until two in the morning.

>>> @user_script
... def trial():
...     measure("Test1", "BT", uamps=30)
...     measure("Test2", "CT", uamps=30)
...     measure("Test1", "BT", trans=True, uamps=10)
...     measure("Test2", "CT", trans=True, uamps=10)
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

.. py:currentmodule:: src.Instrument

The :py:meth:`ScanningInstrument.measure_file` function allows the
user to define everything in a CSV file with excel and then run it
through python.

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
single run with the parameters given in the columns of that row.  If
an argument is left blank, then the keyword's default value is used.
The boolean values ``True`` and ``False`` are case insensitive, but all other
strings retain their case.

.. csv-table:: bad_julabo.csv
  :file: ../../tests/bad_julabo.csv
  :header-rows: 1

>>> measure_file("tests/bad_julabo.csv") #doctest:+ELLIPSIS
Traceback (most recent call last):
...
RuntimeError: Unknown Block Julabo

.. py:currentmodule:: src.Util

Each CSV file is run through the :py:func:`user_script`
function defined `above`__, so the script will be checked for errors before being run.
In the example above, the user set the column header to "Julabo", but
the actual block name is "Julabo1_SP".

__ `Automated script checking`_

If we fix the script file

.. csv-table:: good_julabo.csv
  :file: ../../tests/good_julabo.csv
  :header-rows: 1

>>> measure_file("tests/good_julabo.csv") #doctest:+ELLIPSIS
The script should finish in 0.5 hours
...
Measuring Sample2_TRANS for 10 uamps

The scan then runs as normal.

>>> measure_file("tests/good_julabo.csv", forever=True) # doctest: +SKIP

If the users are leaving and you want to ensure that the script keeps
taking data until they return, the ``forever`` flag causes the
instrument to repeatedly cycle through the script until there is a
manual intervention at the keyboard.  The output is not shown above
because there is infinite output.

>>> from __future__ import print_function
>>> convert_file("tests/good_julabo.csv")
>>> with open("tests/good_julabo.csv.py", "r") as infile:
...     for line in infile:
...         print line,
@user_script
def good_julabo():
    measure(title=Sample1,uamps=10,pos=AT,thickness=1)
    measure(title=Sample2,uamps=10,pos=BT,thickness=1,trans=True,Julabo1_SP=7)

When the user is ready to take the next step into full python
scripting, the CSV file can be turned into a python source file that
performs identical work.  This file can then be edited and customised
to the user's desires.


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
Thick=1.0
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
Thick=1.0
Measuring Sample_TRANS for 100 frames
>>> detector_on(True)
Waiting For Detector To Power Up (180s)
True

If the detector needs to run in a special configuration (e.g. due to
electrical problems), the detector state can be locked.  This will
prevent attempts to turn the detector on and off and will bypass any
checks for the detector state:

>>> detector_lock()
False
>>> detector_on(False)
Waiting For Detector To Power Down (60s)
False
>>> detector_lock(True)
True
>>> measure("Sample", frames=100)
Setup Larmor for event
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring Sample_SANS for 100 frames
>>> detector_on(True)
Traceback (most recent call last):
...
RuntimeError: The instrument scientist has locked the detector state
>>> detector_lock(False)
False
>>> detector_on(True)
Waiting For Detector To Power Up (180s)
True

Custom Running Modes
====================

Some modes may be much more complicated than a simple sans
measurement.  For example, a SESANS measurement needs to setup the DAE
for two periods, manage the flipper state, and switch between those
periods.  From the user's perspective, this is all handled in the same
manner as a normal measurement.

>>> set_default_dae(setup_dae_sesans)
>>> measure("SESANS Test", frames=6000)
Setup Larmor for sesans
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring SESANS Test_SESANS for 6000 frames
Flipper On
Flipper Off
Flipper On
Flipper Off
Flipper On
Flipper Off

.. py:currentmodule:: src.Larmor

In this example, the instrument scientist has written two functions
:py:meth:`Larmor._begin_sesans` and :py:meth:`Larmor._waitfor_sesans`
which handle the SESANS specific nature of the measurement.

>>> measure("SESANS Test", u=1500, d=1500, uamps=10)
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring SESANS Test_SESANS for 10 uamps
Flipper On
Flipper Off
Flipper On
Flipper Off
Flipper On
Flipper Off

These custom mode also allow more default parameters to be added onto
:py:meth:`ScanningInstrument.measure`.  In this instance, the ``u``
and ``d`` parameters set the number of frames in the up and down
states.


Under the hood
==============

>>> gen.reset_mock()
>>> measure("Test", "BT", dae="event", aperature="Medium", uamps=15)
Setup Larmor for event
Moving to sample changer position BT
Using the following Sample Parameters
Geometry=Flat Plate
Width=10
Height=10
Thick=1.0
Measuring Test_SANS for 15 uamps

This command returns no result, but should cause a large number of
actions to be run through genie-python.  We can verify those actions
through the mock genie object that's created when the actual
genie-python isn't found.

>>> print(gen.mock_calls)
[call.get_runstate(),
 call.get_pv('IN:LARMOR:CAEN:hv0:0:8:status'),
 call.get_pv('IN:LARMOR:CAEN:hv0:0:9:status'),
 call.get_pv('IN:LARMOR:CAEN:hv0:0:10:status'),
 call.get_pv('IN:LARMOR:CAEN:hv0:0:11:status'),
 call.set_pv('IN:LARMOR:PARS:SAMPLE:MEAS:TYPE', 'sesans'),
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
 call.cset(m4trans=200.0),
 call.cset(a1hgap=20.0, a1vgap=20.0, s1hgap=14.0, s1vgap=14.0),
 call.cset(SamplePos='BT'),
 call.waitfor_move(),
 call.change_sample_par('Thick', 1.0),
 call.get_sample_pars(),
 call.change(title='Test_SANS'),
 call.begin(),
 call.waitfor(uamps=15),
 call.end()]

That's quite a few commands, so it's worth running through them.

:2: Ensure that the instrument is ready to start a measurement
:3-6: Check that the detector is on
:7: Check that the detector is on
:8-19: Put the instrument in event mode
:20: Move the M4 transmission monitor out of the beam
:21: Set the upstream slits
:22: Move the sample into position
:23: Let motors finish moving.
:24: Set the sample thickness
:25: Print and log the sample parameters
:26: Set the sample title
:27: Start the measurement.
:28: Wait the requested time
:29: Stop the measurement.
