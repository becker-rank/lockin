"""Conversão do duty e geração dos dois LEDs por tabelas senoidais."""
import math
import time
import config


def saturate(value, minimum, maximum):
    return min(maximum, max(minimum, value))


def percent_to_u16(percent):
    return int(saturate(percent, 0.0, 100.0) * 65535 / 100)


def init():
    """Calcula o seno uma vez e inicia a referência da perturbação."""
    global _sine, _last_ref, _dist_start_us
    _sine = [math.sin(2 * math.pi * k / config.POINTS)
             for k in range(config.POINTS)]
    _last_ref = time.ticks_us()
    _dist_start_us = 0
    refresh_tables()


def refresh_tables():
    """Recalcula os duties entre blocos, após uma mudança do controle."""
    global _ctrl, _dist
    _ctrl = [percent_to_u16(config.Dmean + config.DampCtrl * s) for s in _sine]
    _dist = [percent_to_u16(config.Dmean + config.DampDist * s) for s in _sine]


def begin_block(t_ref):
    """Mantém a fase da perturbação entre blocos de aquisição."""
    global _last_ref, _dist_start_us
    elapsed = time.ticks_diff(t_ref, _last_ref)
    _dist_start_us = (_dist_start_us + elapsed) % config.DIST_PERIOD
    _last_ref = t_ref


def generate_ctrl(pwm_ctrl, step):
    pwm_ctrl.duty_u16(_ctrl[step % config.POINTS])


def generate_dist(pwm_dist, step):
    elapsed_us = _dist_start_us + step * config.STEP_US
    index = (elapsed_us // config.DIST_STEP_US) % config.POINTS
    pwm_dist.duty_u16(_dist[index])