"""Lock-in de quatro fases e média de I/Q em N períodos."""
import math


def lockIn(p, Vref):
    scale = Vref / 65535.0
    x0 = (p.a[0] - p.b[0]) * scale
    x90 = (p.a[1] - p.b[1]) * scale
    x180 = (p.a[2] - p.b[2]) * scale
    x270 = (p.a[3] - p.b[3]) * scale
    p.i = (x90 - x270) / 2
    p.q = (x0 - x180) / 2
    p.amp = math.sqrt(p.i * p.i + p.q * p.q)
    p.phi = math.atan2(p.q, p.i) 


def update_stats(count, mean, m2, value):
    """Atualiza média e soma dos desvios quadráticos sem guardar um histórico."""
    count += 1
    delta = value - mean
    mean += delta / count
    m2 += delta * (value - mean)
    return count, mean, m2


def sample_std(count, m2):
    """Desvio-padrão amostral; requer pelo menos duas medidas."""
    return math.sqrt(max(0.0, m2) / (count - 1)) 


def average(p, Vref):
    """Returns the mean value of p.i and p.q for p.n measures."""
    sum_i = sum_q = 0.0
    count, mean_amp, m2_amp = 0, 0.0, 0.0

    for cycle in range(p.n):
        for k in range(4):
            p.a[k] = p.raw_a[4 * cycle + k]
            p.b[k] = p.raw_b[4 * cycle + k]
        lockIn(p, Vref)
        sum_i += p.i
        sum_q += p.q
        count, mean_amp, m2_amp = update_stats(count, mean_amp, m2_amp, p.amp)

    p.i_mean = sum_i / p.n
    p.q_mean = sum_q / p.n
    p.amp_mean = math.sqrt(p.i_mean * p.i_mean + p.q_mean * p.q_mean)
    p.phi_mean = math.atan2(p.q_mean, p.i_mean) 
    p.std_amp_cycles = sample_std(count, m2_amp)