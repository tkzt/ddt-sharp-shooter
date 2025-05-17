# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('C:\\Projects\\ddt-sharp-shooter\\.venv\\Lib\\site-packages\\onnxruntime\\capi\\onnxruntime_providers_shared.dll','onnxruntime\\capi'),
        ('C:\\Projects\\ddt-sharp-shooter\\.venv\\Lib\\site-packages\\ddddocr\\common.onnx','ddddocr'),
        ('C:\\Projects\\ddt-sharp-shooter\\.venv\\Lib\\site-packages\\ddddocr\\common_old.onnx','ddddocr'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dss',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/logo.icns'],
)
app = BUNDLE(
    exe,
    name='dss.app',
    icon='./assets/logo.icns',
    bundle_identifier=None,
)
