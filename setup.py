# -*- coding: utf-8 -*-
"""


Created by Allen Tao at 2022/5/12 19:42
"""
from setuptools import setup

APP = ['main.py']
OPTIONS = {
    'iconfile': 'logo.ico',
    'packages': ['pynput']
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
