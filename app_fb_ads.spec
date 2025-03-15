# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_fb_ads.py'],
    pathex=['./'],
    binaries=[('dist/schedule.exe', '.'),
    ('dist/scheduler.exe','.')],

    datas=[('fb_ads_database.db', '.'),('db_connection.py', '.'),('path.py','.'),('auth.txt','.'),('uk-lon.prod.surfshark.comsurfshark_openvpn_udp.ovpn','.')],
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
    name='app_fb_ads',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)
