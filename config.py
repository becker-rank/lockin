#pins, parameters, classes, ...


#PINS
PIN_CTRL = 14   #Control led: gpio14
PIN_DIST = 12   #Disturbance led: gpio12
PIN_RESULT = 10 #Result from ldr measure: gpio10
PIN_LDRA = 26
PIN_LDRB = 27
VREF = 3.3


#FREQUENCY
FREQ_PWM = 20_000    #PWM frequency (not the same as duty cicle!)
FREQ_CTRL = 100      #Control duty cicle frequency
FREQ_DIST = 0.2      #Disturbance duty cicle
POINTS = 40
PERIOD = int(round(1_000_000 / FREQ_CTRL))  #Period of control duty cicle in microsec (us)
STEP_US = PERIOD // POINTS  #time between each step
DIST_PERIOD = int(round(1_000_000 / FREQ_DIST))
DIST_STEP_US = DIST_PERIOD // POINTS


#control, disturbance and aquisition variables
N = 10  #numero de aquisicoes/periodos
Dmean = 50.0    #mean duty cicle for both leds
DampCtrl = 20.0 #control duty cicle amplitude [30,70]
DampDist = 0.0 #amplitude for disturbance duty cicle
WARMUP_PERIODS = 100 #number of duty cicle periods before each block
MAX_DELAY_US = 100  #maximum time in us of delay for each aquisition
MAX_FAILURES = 5    #maximum number of failures before program is aborted
MAX_BLOCKS = 0      #maximum number of valid blocks. For =0 there is no limit
LOG_RAW = True # export va,vb, vd if true

  

class lockinParameters:
    def __init__(self):
        """Class for storing the lockin parameters"""
        self.amp = self.phi = self.i = self.q = 0.0
        self.a = [0, 0, 0, 0]
        self.b = [0, 0, 0, 0]
        self.ta = [0, 0, 0, 0]
        self.tb = [0, 0, 0, 0]
        self.n = N
        self.raw_a = array('H', [0] * (4 * N))
        self.raw_b = array('H', [0] * (4 * N))
        self.raw_ta = array('i', [0] * (4 * N))
        self.raw_tb = array('i', [0] * (4 * N))
        self.i_cycles = array('f', [0.0] * N)
        self.q_cycles = array('f', [0.0] * N)
        self.amp_cycles = array('f', [0.0] * N)
        self.phi_cycles = array('f', [0.0] * N)
        self.i_mean = self.q_mean = self.amp_mean = 0.0
        self.phi_mean = self.std_amp_cycles = float('nan')
        self.valid = False
        self.max_delay_us = self.max_ab_us = self.clip_count = 0
        self.time_s = 0.0
        self.damp_ctrl = DampCtrl
        self.damp_dist = DampDist


