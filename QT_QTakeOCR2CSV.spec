# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
extra_datas = [
    ('paddleocr/det', 'paddleocr/det'),
    ('paddleocr/rec', 'paddleocr/rec'),
    ('paddleocr/cls', 'paddleocr/cls'),
]
a = Analysis(
    ['QT_QTakeOCR2CSV.py'],
    pathex=['/opt/miniconda3/envs/qvh/lib/python3.11/site-packages/paddleocr','/opt/miniconda3/envs/qvh/lib/python3.11/site-packages/paddle/libs'],
    binaries=[('/opt/miniconda3/envs/qvh/lib/python3.11/site-packages/paddle/libs','.')],
    datas=extra_datas,
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
    name='QT_QTakeOCR2CSV',
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
    icon=['logo.ico'],
)
app = BUNDLE(
    exe,
    name='QT_QTakeOCR2CSV.app',
    icon='logo.ico',
    bundle_identifier=None,
)
