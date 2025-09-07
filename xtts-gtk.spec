# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# Block PyInstaller from trying to import GTK 3.0
sys.modules['gi.repository.Gtk'] = None
sys.modules['gi.repository.Gdk'] = None

# Now import gi and set version requirements
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('GioUnix', '2.0')

# Clear the modules we blocked so they can be properly imported with correct versions
if 'gi.repository.Gtk' in sys.modules:
    del sys.modules['gi.repository.Gtk']
if 'gi.repository.Gdk' in sys.modules:
    del sys.modules['gi.repository.Gdk']

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.png', '.')],
    hiddenimports=[
        'gi',
        'gi.repository.Gtk',
        'gi.repository.Gdk',
        'gi.repository.GLib',
        'gi.repository.GObject',
        'gi.repository.Gio',
        'TTS',
        'torch',
        'threading',
        'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hooks/runtime_hook_gtk.py'],
    excludes=[
        'gi.repository.Gtk 3.0',
        'gi.repository.Gdk 3.0',
        'gtk-3.0',
        'gdk-3.0',
        'gi.repository.Gtk 2.0',
        'gi.repository.Gdk 2.0',
        'gtk-2.0',
        'gdk-2.0',
        'gi.overrides.Gtk',
        'gi.overrides.Gdk',
    ],
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
    name='xtts-gtk',
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
    icon='logo.png' if os.path.exists('logo.png') else None,
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='xtts-gtk.app',
        icon='logo.png' if os.path.exists('logo.png') else None,
        bundle_identifier='org.remy.xtts-gtk',
        info_plist={
            'CFBundleName': 'XTTS-GTK',
            'CFBundleDisplayName': 'XTTS-GTK',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': 'True',
        },
    )
