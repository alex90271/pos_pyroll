# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['chip_payroll.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates/', 'templates/'),
        ('assets/', 'assets/'),
        ('data/tip_pools.json', 'data/'),
        ('data/settings_v3.json', 'data/'),
    ],
    hiddenimports=[
        'babel.numbers',
        'dbfread',
        'tkcalendar',
        'pandastable',
        'jinja2.ext',
        'pkg_resources',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'flask'],  # Exclude unused heavy packages
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
    name='chip_payroll',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Remove debug symbols for smaller size
    upx=True,
    upx_exclude=['api-ms-*'],  # Exclude incompatible binaries from UPX
    runtime_tmpdir='_internal',  # Use proper cache location
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/pyroll_ico.ico'],  # Fixed path separator for cross-platform
)
