"""Copiar este arquivo e os outros cinco módulos para a Pico W."""
from machine import Pin, PWM
import gc
import math
import time
import config
import function
import acquisition
import lockin
import control


def main():
    function.init()
    acquisition.init()
    p = config.lockinParameters()
    pwm_ctrl = PWM(Pin(config.PIN_CTRL), freq=config.FREQ_PWM, duty_u16=0)
    pwm_dist = PWM(Pin(config.PIN_DIST), freq=config.FREQ_PWM, duty_u16=0)
    count, mean_amp, m2_amp = 0, 0.0, 0.0

    try:
        while True:
            function.refresh_tables()
            gc.collect()  # Liberar memória antes do trecho temporizado.
            t_ref = time.ticks_add(time.ticks_us(), 2_000)

            if not acquisition.acquire(p, pwm_ctrl, pwm_dist, t_ref):
                print("Aquisicao atrasada; repetindo o bloco.")
                continue

            lockin.average(p, config.VREF)
            count, mean_amp, m2_amp = lockin.update_stats(
                count, mean_amp, m2_amp, p.amp_mean)
            control.control(p)

            print("Amplitude media (V):", p.amp_mean)
            print("Fase (graus):", p.phi_mean * 180 / math.pi)
            print("Desvio dos periodos (V):", p.std_amp_cycles)
            print("Desvio das medias (V):", lockin.sample_std(count, m2_amp))
    finally:
        # Desligar os dois LEDs ao interromper o programa ou ocorrer um erro.
        for pwm, pin in ((pwm_ctrl, config.PIN_CTRL), (pwm_dist, config.PIN_DIST)):
            pwm.duty_u16(0)
            pwm.deinit()
            Pin(pin, Pin.OUT, value=0)


if __name__ == '__main__':
    main()