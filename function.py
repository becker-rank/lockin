import math
import time
import config


def saturate(value, minimum, maximum):
    return min(maximum, max(minimum, value))


def percent_to_u16(percent):
    return int(saturate(percent, 0.0, 100.0) * 65535 / 100)


def init():
    """Calculates sine table, initiates time reference"""
    global _sine, _last_ref, _dist_start_us
    _sine = [math.sin(2 * math.pi * k / config.POINTS)    #_sine array holds POINTSth values of sin between [0,2pi]
             for k in range(config.POINTS)]
    _last_ref = time.ticks_us()
    _dist_start_us = 0
    refresh_tables()


def refresh_tables():
    """Calculates the duty cicles, using the sine table"""
    global _ctrl, _dist    #both arrays with POINTS-th elements
    _ctrl = [percent_to_u16(config.Dmean + config.DampCtrl * s) for s in _sine]
    _dist = [percent_to_u16(config.Dmean + config.DampDist * s) for s in _sine]


def begin_block(t_ref):
    """Since FREQ_CTRL >> FREQ_DIST there is a need to maintain the disturbance
    led cicle ininterrupted from one acquisiton to another. This function does that."""
    global _last_ref, _dist_start_us    #_dist_start_us holds the current position of the disturbance signal in the sine.
    elapsed = time.ticks_diff(t_ref, _last_ref)
    _dist_start_us = (_dist_start_us + elapsed) % config.DIST_PERIOD   #updates the 'clock pointer'
    _last_ref = t_ref    #_last_ref receives the current block start time.


def generate_ctrl(pwm_ctrl, step):
    pwm_ctrl.duty_u16(_ctrl[step % config.POINTS])


def generate_dist(pwm_dist, step):
    elapsed_us = _dist_start_us + step * config.STEP_US
    index = (elapsed_us // config.DIST_STEP_US) % config.POINTS
    pwm_dist.duty_u16(_dist[index])