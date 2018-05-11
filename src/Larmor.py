from Instrument import ScanningInstrument
from Util import dae_setter
from genie import gen

class Larmor(ScanningInstrument):
    _poslist = ['AB','BB','CB','DB','EB','FB','GB','HB','IB','JB','KB','LB','MB','NB','OB','PB','QB','RB','SB','TB'
        ,'AT','BT','CT','DT','ET','FT','GT','HT','IT','JT','KT','LT','MT','NT','OT','PT','QT','RT','ST','TT'
        ,'1CB','2CB','3CB','4CB','5CB','6CB','7CB','8CB','9CB','10CB','11CB','12CB','13CB','14CB'
        ,'1CT','2CT','3CT','4CT','5CT','6CT','7CT','8CT','9CT','10CT','11CT','12CT','13CT','14CT'
        ,'1WB','2WB','3WB','4WB','5WB','6WB','7WB','8WB','9WB','10WB','11WB','12WB','13WB','14WB'
        ,'1WT','2WT','3WT','4WT','5WT','6WT','7WT','8WT','9WT','10WT','11WT','12WT','13WT','14WT']

    @staticmethod
    def _generic_scan(
            detector="C:\Instrument\Settings\Tables\detector.dat",
            spectra="C:\Instrument\Settings\Tables\spectra_1To1.dat",
            wiring="C:\Instrument\Settings\Tables\wiring.dat",
            tcbs=[]):
        gen.change(nperiods=1)
        gen.change_start()
        gen.change_tables(detector=detector)
        gen.change_tables(spectra=spectra)
        gen.change_tables(wiring=wiring)
        for tcb in tcbs:
            gen.change_tcb(**tcb)
        gen.change_finish()

    @staticmethod
    def _set_choppers(lrange):
        # now set the chopper phasing to the defaults
        # T0 phase checked for November 2015 cycle 
        # Running at 5Hz and centering the dip from the T0 at 50ms by setting phase to 48.4ms does not stop the fast flash 
        # Setting the T0 phase to 0 (50ms) does
        if lrange==0:
            #This is for 0.9-13.25
            gen.cset(T0Phase=0)
            gen.cset(TargetDiskPhase=2750)
            gen.cset(InstrumentDiskPhase=2450)
        else:
            #This is for 0.65-12.95
            gen.cset(TargetDiskPhase=1900)
            gen.cset(InstrumentDiskPhase=1600)
    
    @dae_setter
    def setup_dae_scanning(self):
        self._generic_scan(
            spectra="C:\Instrument\Settings\Tables\spectra_scanning_80.dat",
            tcbs=[{"low":5.0,"high":100000.0,"step":100.0,"trange":1,"log":0}])

    @dae_setter
    def setup_dae_nr(self):
        self._generic_scan(
            spectra="C:\Instrument\Settings\Tables\spectra_nrscanning.dat",
            tcbs=[{"low":5.0,"high":100000.0,"step":100.0,"trange":1,"log":0}])

    @dae_setter
    def setup_dae_nrscanning(self):
        self._generic_scan(
            spectra="U:\Users\Masks\spectra_scanning_auto.dat",
            tcbs=[{"low":5.0,"high":100000.0,"step":100.0,"trange":1,"log":0}])

    @dae_setter
    def setup_dae_event(self,step=100.0,lrange=0):
        # Normal event mode with full detector binning
        self._generic_scan(
            wiring="C:\Instrument\Settings\Tables\wiring_event.dat",
            tcbs=[{"low":5.0,"high":100000.0,"step":step,"trange":1,"log":0},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0},
                  {"low":5.0,"high":100000.0,"step":2.0,"trange":1,"log":0,"regime":2}])
        self._set_choppers(lrange)

    @dae_setter
    def setup_dae_event_fastsave(self,step=100.0,lrange=0):
        # Event mode with reduced detector histogram binning to decrease filesize
        # This currently breaks mantid nexus read
        print "setup larmor event fastsave"
        self._generic_scan(
            wiring="C:\Instrument\Settings\Tables\wiring_event_fastsave.dat",
            # change to log binning to reduce number of detector bins by a factor of 10 to decrease write time
            tcbs=[{"low":5.0,"high":100000.0,"step":0.1,"trange":1,"log":1},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0},
                  {"low":5.0,"high":100000.0,"step":2.0,"trange":1,"log":0,"regime":2},
                  # 3rd time regime for monitors to allow flexible binning of detector to reduce file size
                  # and decrease file write time
                  {"low":5.0,"high":100000.0,"step":100.0,"trange":1,"log":0,"regime":3},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0,"regime":3}])
        self._set_choppers(lrange)

    @dae_setter
    def setup_dae_histogram(self,lrange=0):
        print "setup larmor normal"
        gen.change_sync('isis')
        self._generic_scan(
            tcbs=[{"low":5.0,"high":100000.0,"step":100.0,"trange":1,"log":0},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0}])
        self._set_choppers(lrange)

    @dae_setter
    def setup_dae_transmission(self,lrange=0):
        print "setup larmor transmission"
        gen.change_sync('isis')
        self._generic_scan(
            "C:\Instrument\Settings\Tables\detector_monitors_only.dat",
            "C:\Instrument\Settings\Tables\spectra_monitors_only.dat",
            "C:\Instrument\Settings\Tables\wiring_monitors_only.dat",
            [{"low":5.0,"high":100000.0,"step":100.0,"trange":1,"log":0},
             {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0}])
        self._set_choppers(lrange)

    @dae_setter
    def setup_dae_monotest(self):
        print "setup larmor monotest"
        self._generic_scan(
            tcbs=[{"low":5.0,"high":100000.0,"step":100.0,"trange":1,"log":0},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0}])
        gen.cset(T0Phase=0)
        gen.set_pv("IN:LARMOR:MK3CHOPR_01:CH2:DIR:SP","CW")
        gen.cset(TargetDiskPhase=8200)
        gen.set_pv("IN:LARMOR:MK3CHOPR_01:CH3:DIR:SP","CCW")
        gen.cset(InstrumentDiskPhase=77650)

    @dae_setter
    def setup_dae_tshift(self,tlowdet=5.0,thighdet=100000.0,tlowmon=5.0,thighmon=100000.0):
        #setup to allow m1 to count as normal but to shift the rest of the detectors
        # in order to allow counting over the frame
        print "setup larmor tshift"
        self._generic_scan(
            wiring="C:\Instrument\Settings\Tables\wiring_tshift.dat",
            tcbs=[{"low":tlowdet,"high":thighdet,"step":100.0,"trange":1,"log":0},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0},
                  {"low":tlowmon,"high":thighmon,"step":20.0,"trange":1,"log":0,"regime":3}])

    @dae_setter
    def setup_dae_diffraction(self):
        print "setup larmor normal"
        self._generic_scan(
            tcbs=[{"low":5.0,"high":100000.0,"step":0.01,"trange":1,"log":1},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0}])

    @dae_setter
    def setup_dae_polarised(self):
        print "setup larmor polarised"
        self._generic_scan(
            tcbs=[{"low":5.0,"high":100000.0,"step":100.0,"trange":1},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0}])

    @dae_setter
    def setup_dae_bsalignment(self):
        print "setup larmor beamstop alignment"
        self._generic_scan(
            tcbs=[{"low":1000.0,"high":100000.0,"step":99000.0,"trange":1,"log":0},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0}])

    @dae_setter
    def setup_dae_monitorsonly(self):
        print "setup larmor monitors only"
        self._generic_scan(
            spectra="C:\Instrument\Settings\Tables\spectra_phase1.dat",
            tcbs=[{"low":5.0,"high":100000.0,"step":20.0,"trange":1,"log":0},
                  {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0}])

    @dae_setter
    def setup_dae_resonantimaging(self):
        print "setup larmor monitors only"
        self._generic_scan(
            "C:\Instrument\Settings\Tables\detector_monitors_only.dat",
            "C:\Instrument\Settings\Tables\spectra_monitors_only.dat",
            "C:\Instrument\Settings\Tables\wiring_monitors_only.dat",
            [{"low":5.0,"high":1500.0,"step":0.256,"trange":1,"log":0},
             {"low":1500.0,"high":100000.0,"step":100.0,"trange":2,"log":0}])

    @dae_setter
    def setup_dae_resonantimaging_choppers(self):
        print "Setting Chopper phases"
        gen.cset(T0Phase=49200)
        gen.cset(TargetDiskPhase=0)
        gen.cset(InstrumentDiskPhase=0)

    @dae_setter
    def setup_dae_4periods(self):
        print "setup larmor for 4 Period mode"
        self._generic_scan(
            "C:\Instrument\Settings\Tables\detector.dat",
            "C:\Instrument\Settings\Tables\spectra_4To1.dat",
            "C:\Instrument\Settings\Tables\wiring.dat",
            [{"low":5.0,"high":100000.0,"step":100.0,"trange":1,"log":0},
             {"low":0.0,"high":0.0,"step":0.0,"trange":2,"log":0}])

    @staticmethod
    def set_aperature(size):
        if size.upper=="MEDIUM":
            gen.cset(a1hgap=20.0,a1vgap=20.0,s1hgap=14.0,s1vgap=14.0)
        else:
            #Leave the slits alone
            pass
        gen.waitfor_move()

    def _configure_sans_custom(self, size="",mode='event'):
        # move the transmission monitor out
        gen.cset(m4trans=200.0)
        gen.waitfor_move()
        
    def _configure_trans_custom(self, size=""):
        # move the transmission monitor out
        gen.cset(m4trans=0.0)
        gen.waitfor_move()

    ######## Instrument Specific Scripts ########
    @staticmethod
    def FOMin():
        #gen.cset(pol_trans=0,pol_arc=-1.6)
        # Convert to angle instead of mm
        gen.cset(pol_trans=0,pol_arc=-0.084)

    @staticmethod
    def ShortPolariserin():
        #gen.cset(pol_trans=-100,pol_arc=-1.3)
        # Convert to angle instead of mm
        gen.cset(pol_trans=-100,pol_arc=-0.069)

    @staticmethod
    def LongPolariserin():
        #gen.cset(pol_trans=100,pol_arc=-1.3)
        # Convert to angle instead of mm
        gen.cset(pol_trans=100,pol_arc=-0.069)

    @staticmethod
    def BSInOut(InOut="IN"):
        #move beamstop in or out. The default is to move in
        if(InOut.upper()=="OUT"):
            cset(BSY=200.0,BSZ=0.0)
        else:
            cset(BSY=88.5,BSZ=353.0)

    #def Analyserin():
        # Set the analyser so that the wavelength cut off is at approx 1.6 Ang
        #cset(An_Trans=0,An_Deg=-1.0)

    @staticmethod
    def homecoarsejaws():
        print "Homing Coarse Jaws"
        gen.cset(cjhgap=40,cjvgap=40)
        gen.waitfor_move()
        # home north and west
        gen.set_pv("IN:LARMOR:MOT:JAWS1:JN:MTR.HOMR","1")
        gen.set_pv("IN:LARMOR:MOT:JAWS1:JW:MTR.HOMR","1")
        gen.waitfor_move()
        gen.set_pv("IN:LARMOR:MOT:JAWS1:JN:MTR.VAL","20")
        gen.set_pv("IN:LARMOR:MOT:JAWS1:JW:MTR.VAL","20")
        # home south and east
        gen.set_pv("IN:LARMOR:MOT:JAWS1:JS:MTR.HOMR","1")
        gen.set_pv("IN:LARMOR:MOT:JAWS1:JE:MTR.HOMR","1")
        gen.waitfor_move()
        gen.set_pv("IN:LARMOR:MOT:JAWS1:JS:MTR.VAL","20")
        gen.set_pv("IN:LARMOR:MOT:JAWS1:JE:MTR.VAL","20")
        gen.waitfor_move()

    @staticmethod
    def homea1():
        print "Homing a1"
        gen.cset(a1hgap=40,a1vgap=40)
        gen.waitfor_move()
        # home north and west
        gen.set_pv("IN:LARMOR:MOT:JAWS2:JN:MTR.HOMR","1")
        gen.set_pv("IN:LARMOR:MOT:JAWS2:JW:MTR.HOMR","1")
        gen.waitfor_move()
        gen.set_pv("IN:LARMOR:MOT:JAWS2:JN:MTR.VAL","20")
        gen.set_pv("IN:LARMOR:MOT:JAWS2:JW:MTR.VAL","20")
        # home south and east
        gen.set_pv("IN:LARMOR:MOT:JAWS2:JS:MTR.HOMR","1")
        gen.set_pv("IN:LARMOR:MOT:JAWS2:JE:MTR.HOMR","1")
        gen.waitfor_move()
        gen.set_pv("IN:LARMOR:MOT:JAWS2:JS:MTR.VAL","20")
        gen.set_pv("IN:LARMOR:MOT:JAWS2:JE:MTR.VAL","20")
        gen.waitfor_move()

    @staticmethod
    def homes1():
        print "Homing s1"
        gen.cset(s1hgap=40,s1vgap=40)
        gen.waitfor_move()
        # home north and west
        gen.set_pv("IN:LARMOR:MOT:JAWS3:JN:MTR.HOMR","1")
        gen.set_pv("IN:LARMOR:MOT:JAWS3:JW:MTR.HOMR","1")
        gen.waitfor_move()
        gen.set_pv("IN:LARMOR:MOT:JAWS3:JN:MTR.VAL","20")
        gen.set_pv("IN:LARMOR:MOT:JAWS3:JW:MTR.VAL","20")
        # home south and east
        gen.set_pv("IN:LARMOR:MOT:JAWS3:JS:MTR.HOMR","1")
        gen.set_pv("IN:LARMOR:MOT:JAWS3:JE:MTR.HOMR","1")
        gen.waitfor_move()
        gen.set_pv("IN:LARMOR:MOT:JAWS3:JS:MTR.VAL","20")
        gen.set_pv("IN:LARMOR:MOT:JAWS3:JE:MTR.VAL","20")
        gen.waitfor_move()

    @staticmethod
    def homes2():
        print "Homing s2"

    @staticmethod
    def detectoronoff(onoff=0,delay=1):
        if(onoff==1):
            gen.set_pv("IN:LARMOR:CAEN:hv0:0:8:pwonoff","On")
            gen.set_pv("IN:LARMOR:CAEN:hv0:0:9:pwonoff","On")
            gen.set_pv("IN:LARMOR:CAEN:hv0:0:10:pwonoff","On")
            gen.set_pv("IN:LARMOR:CAEN:hv0:0:11:pwonoff","On")
        else:
            gen.set_pv("IN:LARMOR:CAEN:hv0:0:8:pwonoff","Off")
            gen.set_pv("IN:LARMOR:CAEN:hv0:0:9:pwonoff","Off")
            gen.set_pv("IN:LARMOR:CAEN:hv0:0:10:pwonoff","Off")
            gen.set_pv("IN:LARMOR:CAEN:hv0:0:11:pwonoff","Off")
        # wait for 3 minutes for ramp up 60s to ranmp down
        if(delay==1):
            if(onoff==1):
                print "Waiting For Detector To Power Up (180s)"
                sleep(180)
            else:
                print "Waiting For Detector To Power Down (60s)"
                sleep(60)
                

    @staticmethod
    def movebench(angle=0.0,delaydet=1):
        print "Turning Detector Off"
        detectoronoff(onoff=0,delay=delaydet)
        a1=0
        a1+=gen.get_pv("IN:LARMOR:CAEN:hv0:0:8:status")
        a1+=gen.get_pv("IN:LARMOR:CAEN:hv0:0:9:status")
        a1+=gen.get_pv("IN:LARMOR:CAEN:hv0:0:10:status")
        a1+=gen.get_pv("IN:LARMOR:CAEN:hv0:0:11:status")
        if(a1>0):
            print "The detector is not turned off"
            print "Not attempting Move"
            return
        else:
            print "The detector is off"
           
        if(angle >= 0.0):
            gen.cset(benchlift=1)
            print "Lifting Bench (20s)"
            sleep(20)
            a1=gen.get_pv("IN:LARMOR:BENCH:STATUS")

            if(a1==1):
                print "Rotating Bench"
                gen.cset(bench_rot=angle)
                gen.waitfor_move()
                print "Lowering Bench (20s)"
                gen.cset(benchlift=0)
                sleep(20)
            else:
                print "Bench failed to lift"
                print "Move not attempted"
        #turn the detector back on
        print "Turning Detector Back on"
        detectoronoff(onoff=1,delay=delaydet)

    @staticmethod
    def rotatebench(angle=0.0,delaydet=1):
        a1=0
        a1+=gen.get_pv("IN:LARMOR:CAEN:hv0:0:8:status")
        a1+=gen.get_pv("IN:LARMOR:CAEN:hv0:0:9:status")
        a1+=gen.get_pv("IN:LARMOR:CAEN:hv0:0:10:status")
        a1+=gen.get_pv("IN:LARMOR:CAEN:hv0:0:11:status")
        if(a1>0):
            print "The detector is not turned off"
            print "Not attempting Move"
            return
        else:
            print "The detector is off"
           
        if(angle >= -0.5):
            gen.cset(benchlift=1)
            print "Lifting Bench (20s)"
            sleep(20)
            a1=gen.get_pv("IN:LARMOR:BENCH:STATUS")

            if(a1==1):
                print "Rotating Bench"
                gen.cset(bench_rot=angle)
                gen.waitfor_move()
                print "Lowering Bench (20s)"
                gen.cset(benchlift=0)
                sleep(20)
            else:
                print "Bench failed to lift"
                print "Move not attempted"

    @staticmethod
    def setup_pi_rotation():
        gen.set_pv("IN:LARMOR:SDTEST_01:P2:COMM","*IDN?")
        time.sleep(1)
        gen.set_pv("IN:LARMOR:SDTEST_01:P2:COMM","ERR?")
        time.sleep(1)
        gen.set_pv("IN:LARMOR:SDTEST_01:P2:COMM","SVO 1 1")
        time.sleep(1)
        gen.set_pv("IN:LARMOR:SDTEST_01:P2:COMM","RON 1 1")
        time.sleep(1)
        gen.set_pv("IN:LARMOR:SDTEST_01:P2:COMM","VEL 1 180")
        time.sleep(1)
        gen.set_pv("IN:LARMOR:SDTEST_01:P2:COMM","ACC 1 90")
        time.sleep(1)
        gen.set_pv("IN:LARMOR:SDTEST_01:P2:COMM","DEC 1 90")

    @staticmethod
    def home_pi_rotation():
        gen.set_pv("IN:LARMOR:SDTEST_01:P2:COMM","FRF 1")
