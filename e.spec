# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for E language interpreter
# Build with:  pyinstaller e.spec --clean --noconfirm

import sys
from pathlib import Path

block_cipher = None

# Path to the project root (where this .spec file lives)
ROOT = Path(SPECPATH).resolve()

a = Analysis(
    [str(ROOT / 'e.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Bundle the entire src/ tree so the interpreter can import its modules
        (str(ROOT / 'src'), 'src'),
    ],
    hiddenimports=[
        'src.lexer',
        'src.parser',
        'src.interpreter',
        'src.environment',
        'src.ast_nodes',
        'src.tokens',
        'src.errors',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='e',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                # don't compress; some AVs flag UPX-packed exes
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,             # E is a CLI language, keep the console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / 'e.ico'),
)
