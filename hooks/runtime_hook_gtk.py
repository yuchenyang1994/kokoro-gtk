# -*- coding: utf-8 -*-
"""
Runtime hook for PyInstaller to properly initialize GTK4 and suppress GTK3 warnings
"""
import sys
import os

# Block any attempts to import GTK 3.x modules
sys.modules['gi.repository.Gtk'] = None
sys.modules['gi.repository.Gdk'] = None

# Import gi and set up version requirements
import gi

# Set version requirements for GTK4
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('GioUnix', '2.0')

# Clear the blocked modules so they can be imported with correct versions
if 'gi.repository.Gtk' in sys.modules:
    del sys.modules['gi.repository.Gtk']
if 'gi.repository.Gdk' in sys.modules:
    del sys.modules['gi.repository.Gdk']

# Set environment variables for GTK if needed
if sys.platform == 'darwin':
    # macOS specific settings
    os.environ['GTK_DEBUG'] = 'interactive'
    os.environ['G_ENABLE_DIAGNOSTIC'] = '0'

    # Try to find GTK4 installation paths
    homebrew_paths = [
        '/opt/homebrew/lib/girepository-1.0',
        '/usr/local/lib/girepository-1.0',
    ]

    for path in homebrew_paths:
        if os.path.exists(path):
            if 'GI_TYPELIB_PATH' in os.environ:
                os.environ['GI_TYPELIB_PATH'] = f"{path}:{os.environ['GI_TYPELIB_PATH']}"
            else:
                os.environ['GI_TYPELIB_PATH'] = path

# Linux specific settings
elif sys.platform.startswith('linux'):
    # Help GTK find its typelibs
    girepository_paths = [
        '/usr/lib/girepository-1.0',
        '/usr/lib64/girepository-1.0',
        '/usr/local/lib/girepository-1.0',
    ]

    existing_paths = [path for path in girepository_paths if os.path.exists(path)]
    if existing_paths:
        if 'GI_TYPELIB_PATH' in os.environ:
            os.environ['GI_TYPELIB_PATH'] = ':'.join(existing_paths) + ':' + os.environ['GI_TYPELIB_PATH']
        else:
            os.environ['GI_TYPELIB_PATH'] = ':'.join(existing_paths)
