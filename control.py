"""ALTERAR, ADICIONAR CONTROLE PI."""
import config
from function import saturate


def control(p):
    """Altera a amplitude da modulação a ser usada no próximo bloco."""
    if config.CONTROL_ENABLED:
        error = config.r - p.amp_mean
        maximum = min(config.Dmean, 100.0 - config.Dmean)
        config.DampCtrl = saturate(config.D0 + config.Kp * error, 0.0, maximum)