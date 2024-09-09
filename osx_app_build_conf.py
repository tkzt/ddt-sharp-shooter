from setuptools import setup

APP = ["main.py"]
DATA_FILES = []
OPTIONS = {
    "iconfile": "assets/logo.ico",
    "packages": ["pynput", "scipy"],
    "plist": {
        "CFBundleName": "DSS",
        "CFBundleDisplayName": "DDT Sharp Shooter",
        "CFBundleGetInfoString": "一个 DDT 小工具",
        "CFBundleIdentifier": "com.boring-plans.dss",
        "CFBundleVersion": "NDSGL 3.0.0",
        "CFBundleShortVersionString": "3.0.0",
        "NSHumanReadableCopyright": "© Allen Tao",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
