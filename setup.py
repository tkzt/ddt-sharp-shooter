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
    'packages': ['pynput'],
    'plist': {
        'CFBundleName': "DSS",
        'CFBundleGetInfoString': "DDT 小工具",
        'CFBundleIdentifier': "Boring Plans",
        'CFBundleShortVersionString': "v1.0.2",
        'NSHumanReadableCopyright': "©️ Allen Tao",
        'Localization native development region': 'China'
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
