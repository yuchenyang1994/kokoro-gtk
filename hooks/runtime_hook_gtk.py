# -*- coding: utf-8 -*-
"""
Runtime hook for PyInstaller to properly initialize GTK4
"""
import os
import sys

# Set environment variables to help GTK find its libraries
if sys.platform.startswith('linux'):
    # Linux: Add common GTK library paths
    library_paths = [
        '/usr/lib/x86_64-linux-gnu',
        '/usr/lib64',
        '/usr/local/lib',
    ]

    existing_paths = [path for path in library_paths if os.path.exists(path)]
    if existing_paths:
        if 'LD_LIBRARY_PATH' in os.environ:
            os.environ['LD_LIBRARY_PATH'] = ':'.join(existing_paths) + ':' + os.environ['LD_LIBRARY_PATH']
        else:
            os.environ['LD_LIBRARY_PATH'] = ':'.join(existing_paths)

    # Add typelib paths
    typelib_paths = [
        '/usr/lib/girepository-1.0',
        '/usr/lib64/girepository-1.0',
        '/usr/local/lib/girepository-1.0',
    ]

    existing_typelib_paths = [path for path in typelib_paths if os.path.exists(path)]
    if existing_typelib_paths:
        if 'GI_TYPELIB_PATH' in os.environ:
            os.environ['GI_TYPELIB_PATH'] = ':'.join(existing_typelib_paths) + ':' + os.environ['GI_TYPELIB_PATH']
        else:
            os.environ['GI_TYPELIB_PATH'] = ':'.join(existing_typelib_paths)

elif sys.platform == 'darwin':
    # macOS: Add Homebrew paths
    homebrew_paths = [
        '/opt/homebrew/lib',
        '/usr/local/lib',
    ]

    for path in homebrew_paths:
        if os.path.exists(path):
            if 'DYLD_LIBRARY_PATH' in os.environ:
                os.environ['DYLD_LIBRARY_PATH'] = f"{path}:{os.environ['DYLD_LIBRARY_PATH']}"
            else:
                os.environ['DYLD_LIBRARY_PATH'] = path

            if 'GI_TYPELIB_PATH' in os.environ:
                os.environ['GI_TYPELIB_PATH'] = f"{path}/girepository-1.0:{os.environ['GI_TYPELIB_PATH']}"
            else:
                os.environ['GI_TYPELIB_PATH'] = f"{path}/girepository-1.0"
