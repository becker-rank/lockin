from machine import ADC, Pin
import time
import config
import function


def init():   #initialize ldrA and ldrB
    global ldrA, ldrB
    ldrA = ADC(Pin(config.PIN_LDRA))
    ldrB = ADC(Pin(config.PIN_LDRB))


def acquire(p, pwm_ctrl, pwm_dist, t_ref):    #acquisiton
    function.begin_block(t_ref)  
    warmup_steps = config.WARMUP_PERIODS * config.POINTS   #number of steps before actually measuring.
    total_steps = warmup_steps + p.n * config.POINTS
    quarter = config.POINTS // 4
    deadline = t_ref

    for step in range(total_steps):
        while time.ticks_diff(time.ticks_us(), deadline) < 0:  #wait until t_ref to start the block.
            pass

        function.generate_ctrl(pwm_ctrl, step)
        function.generate_dist(pwm_dist, step)


        #After stabilization measure for 0, 90, 180,270,
        if (step >= warmup_steps) and ((step % quarter) == 0):
            index = (step - warmup_steps) // quarter
            p.raw_a[index] = ldrA.read_u16()
            p.raw_b[index] = ldrB.read_u16()

        # In order to NOT send to lockin measures that were too late.
        if time.ticks_diff(time.ticks_us(), deadline) > config.MAX_DELAY_US:
            return False

        deadline = time.ticks_add(deadline, config.STEP_US)

    return True