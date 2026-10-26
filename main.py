from machine import Pin, PWM
import math
import time
import config
import function
import acquisition
import lockin
import control


def main():
    function.init()    #sine table and time ref
    acquisition.init()   #initializes ldrA and ldrB
    p = config.lockinParameters()   #object p contains lockin variables
    pwm_ctrl = PWM(Pin(config.PIN_CTRL), freq=config.FREQ_PWM, duty_u16=0)
    pwm_dist = PWM(Pin(config.PIN_DIST), freq=config.FREQ_PWM, duty_u16=0)
    count, mean_amp, m2_amp = 0, 0.0, 0.0

    try:
        while True:
            function.refresh_tables()  #calculates duty cicle table
            t_ref = time.ticks_add(time.ticks_us(), 2_000)  #t_ref: time to start acquisiton block

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
        print("programa interrompido")
        for pwm, pin in ((pwm_ctrl, config.PIN_CTRL), (pwm_dist, config.PIN_DIST)):
            pwm.duty_u16(0)
            pwm.deinit() #
            Pin(pin, Pin.OUT, value=0)
