# -*- coding: utf-8 -*-
"""
Force Map

Created by Allen Tao at 2022/5/11 17:15
"""
import math

_FORCE_MAP = {
    20: [10, 19, 25, 30, 36, 40, 44, 48, 51, 54, 57, 60, 63, 66, 69, 72, 74, 76, 78, 80],
    30: [14, 20, 24, 28, 32, 35, 38, 41, 44, 47, 50, 52, 55, 57, 60, 62, 65, 67, 69, 72],
    50: [14, 20, 24, 28, 32, 35, 39, 42, 44, 48, 50, 53, 55, 58, 60, 63, 65, 68, 70, 72],
    65: [13, 20, 26, 31, 37, 41, 44, 48, 53, 56, 58, 61, 64, 67, 70, 73, 76, 79, 82, 85],
}


def get_force(deg, dis):
    """传入角度、距离，获取力度
    Note that: 1<=dis<=20
    """
    dis_left, integer = dis % 1, math.floor(dis)
    base_force = _FORCE_MAP[deg][integer-1]
    if integer<20:
        extra_force = (_FORCE_MAP[deg][integer] - base_force)*dis_left
    else:
        extra_force = 0
    return base_force + extra_force
