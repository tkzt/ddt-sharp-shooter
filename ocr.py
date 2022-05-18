# -*- coding: utf-8 -*-
"""


Created by Allen Tao at 2022/5/16 00:49
"""
import ddddocr
import re


def recognize_digits(image: bytes):
    ocr = ddddocr.DdddOcr(show_ad=False)
    result = ocr.classification(image)
    return wash_digits(result)


def wash_digits(digits: str):
    washed = digits \
        .replace('g', '9').replace('q', '9') \
        .replace('l', '1').replace('i', '1') \
        .replace('z', '2') \
        .replace('o', '0')
    return re.sub(r'\D', '0', washed)
