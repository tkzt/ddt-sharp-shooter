# -*- coding: utf-8 -*-
"""
py2app setup

Created by Allen Tao at 2022/5/13 16:46
"""
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'iconfile': 'assets/logo.ico',
    'packages': ['pynput', 'ddddocr', 'screeninfo', 'PIL'],
    'plist': {
        'CFBundleName': 'DSS',
        'CFBundleDisplayName': 'DDT Sharp Shooter',
        'CFBundleGetInfoString': "一个 DDT 小工具",
        'CFBundleIdentifier': "com.boring-plans.dss",
        'CFBundleVersion': "SMZG 2.0.1",
        'CFBundleShortVersionString': "2.0.1",
        'NSHumanReadableCopyright': u"© Allen Tao"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
