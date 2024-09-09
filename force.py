# the amazing reference: https://www.52pojie.cn/thread-1132459-1-1.html
import math
import numpy as np
from scipy.optimize import fsolve


def calc_force(deg: float, wind: float, dx: float, dy: float):
    r, w, g = [0.89927083, 5.8709153, -172.06527992]
    deg = deg * math.pi / 180

    def solve(f):
        vx = math.cos(deg) * f
        vy = math.sin(deg) * f

        def calc_pos(v0, _f, _r, t):
            tmp = _f - _r * v0
            ert = np.power(math.e, -_r * t)
            right = tmp * ert + _f * _r * t - tmp
            return right / (_r * _r)

        def calc_time(v0):
            def _solve(t):
                return calc_pos(v0, g, r, t) - dy

            time = fsolve(_solve, np.array([100000]))
            assert time[0] != 0
            return time[0]

        dt = calc_time(vy)
        return calc_pos(vx, w * wind, r, dt) - dx

    force = fsolve(solve, np.array([100]))
    return min(force[0], 100)
