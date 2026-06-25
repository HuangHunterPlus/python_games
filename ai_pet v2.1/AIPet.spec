# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Only bundle files needed for first-run training; runtime JSON files stay in DATA_DIR
datas = [
    ('brain_models/data/corpus.txt', 'brain_models/data'),
    ('brain_models/data/weights.npz', 'brain_models/data'),
]
binaries = []
hiddenimports = ['PyQt5.sip', 'pygame']

# Ensure full subpackage collection for non-Py data
for pkg in ['pet', 'renderer', 'desktop']:
    tmp_ret = collect_all(pkg)
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# brain_models modules are found via direct imports in main.py; don't collect_all
# to avoid bundling runtime JSON files from brain_models/data/


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'PyQt6', 'PySide2', 'PySide6', 'matplotlib',
              'scipy', 'PIL', 'cv2', 'pandas', 'sqlalchemy', 'requests',
              'notebook', 'jupyter'],
    noarchive=False,
    optimize=0,
)

# Strip runtime JSON files from bundled datas (they belong in DATA_DIR, not MEIPASS)
a.datas = [(name, path, kind) for name, path, kind in a.datas
           if not name.endswith('.json')]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AIPet',
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
)
