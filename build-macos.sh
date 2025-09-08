#!/bin/bash

# XTTS-GTK macOS Build Script
# This script builds a macOS DMG for XTTS-GTK

set -e

echo "🔨 Building XTTS-GTK for macOS..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the project root."
    exit 1
fi

# Check if logo exists
if [ ! -f "logo.png" ]; then
    echo "❌ Error: logo.png not found. Please ensure the logo file exists."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist build __pycache__
rm -rf macos_build
rm -f xtts-gtk-macos.dmg

# Install PyInstaller if not available
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Set environment variables for GTK
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:/usr/local/lib:$DYLD_LIBRARY_PATH"
export GI_TYPELIB_PATH="/opt/homebrew/lib/girepository-1.0:/usr/local/lib/girepository-1.0:$GI_TYPELIB_PATH"

# Build with PyInstaller
echo "🏗️  Building app bundle with PyInstaller..."
if [ -f "xtts-gtk.spec" ]; then
    echo "Using spec file..."
    pyinstaller xtts-gtk.spec
else
    echo "Using command line build..."
    pyinstaller main.py --name xtts-gtk --onefile --windowed --clean \
        --hidden-import gi.repository.Gtk \
        --hidden-import gi.repository.GObject \
        --hidden-import gi.repository.GLib \
        --hidden-import gi.repository.Gdk \
        --hidden-import gi.repository.Gio \
        --collect-all gi
fi

# Check if build was successful
if [ ! -d "dist/xtts-gtk.app" ]; then
    echo "❌ Build failed: app bundle not found"
    exit 1
fi

echo "✅ App bundle built successfully!"

# Copy icon to the app bundle
echo "🎨 Setting up app icon..."
mkdir -p "dist/xtts-gtk.app/Contents/Resources"
cp "logo.png" "dist/xtts-gtk.app/Contents/Resources/"

# Try to create proper macOS icon if tools are available
if command -v sips >/dev/null 2>&1 && command -v iconutil >/dev/null 2>&1; then
    echo "Creating macOS iconset..."
    mkdir -p "xtts-gtk.iconset"
    sips -z 16 16     "logo.png" --out "xtts-gtk.iconset/icon_16x16.png"
    sips -z 32 32     "logo.png" --out "xtts-gtk.iconset/icon_16x16@2x.png"
    sips -z 32 32     "logo.png" --out "xtts-gtk.iconset/icon_32x32.png"
    sips -z 64 64     "logo.png" --out "xtts-gtk.iconset/icon_32x32@2x.png"
    sips -z 128 128   "logo.png" --out "xtts-gtk.iconset/icon_128x128.png"
    sips -z 256 256   "logo.png" --out "xtts-gtk.iconset/icon_128x128@2x.png"
    sips -z 256 256   "logo.png" --out "xtts-gtk.iconset/icon_256x256.png"
    sips -z 512 512   "logo.png" --out "xtts-gtk.iconset/icon_256x256@2x.png"
    sips -z 512 512   "logo.png" --out "xtts-gtk.iconset/icon_512x512.png"
    sips -z 1024 1024 "logo.png" --out "xtts-gtk.iconset/icon_512x512@2x.png"

    echo "Converting to icns format..."
    iconutil -c icns "xtts-gtk.iconset"
    cp "xtts-gtk.icns" "dist/xtts-gtk.app/Contents/Resources/"
    ICON_FILE="xtts-gtk.icns"

    # Cleanup temporary icon files
    rm -rf "xtts-gtk.iconset"
    rm -f "xtts-gtk.icns"
else
    echo "sips/iconutil not available, using PNG icon directly"
    cp "logo.png" "dist/xtts-gtk.app/Contents/Resources/"
    ICON_FILE="logo.png"
fi

# Update Info.plist to include icon file
if [ -f "dist/xtts-gtk.app/Contents/Info.plist" ]; then
    defaults write "$(pwd)/dist/xtts-gtk.app/Contents/Info" CFBundleIconFile "$ICON_FILE"
else
    echo "Warning: Info.plist not found, skipping icon configuration"
fi

# Create DMG
echo "📦 Creating DMG file..."
mkdir -p macos_build
cp -r dist/xtts-gtk.app macos_build/

echo "Creating disk image..."
if hdiutil create -volname "XTTS-GTK" -srcfolder "macos_build" -ov -format UDZO "xtts-gtk-macos.dmg"; then
    echo "✅ DMG creation successful"
+else
+    echo "❌ DMG creation failed"
+    ls -la macos_build/
+    exit 1
+fi
+
+# Check if DMG was created
+if [ ! -f "xtts-gtk-macos.dmg" ]; then
+    echo "❌ DMG file not found"
+    exit 1
+fi
+
+echo "✅ DMG created successfully!"
+echo ""
+echo "📋 Build Summary:"
+echo "   App Bundle: dist/xtts-gtk.app"
+echo "   DMG: xtts-gtk-macos.dmg"
+echo ""
+echo "🚀 To install:"
+echo "   1. Open xtts-gtk-macos.dmg"
+echo "   2. Drag XTTS-GTK to Applications"
+echo "   3. Run from Applications or Launchpad"
+echo ""
+echo "🧹 Cleaning up..."
+rm -rf macos_build
+
+echo "🎉 Build complete!"
