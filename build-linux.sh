#!/bin/bash

# XTTS-GTK Linux Build Script
# This script builds a Linux AppImage for XTTS-GTK

set -e

echo "🔨 Building XTTS-GTK for Linux..."

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
rm -rf AppDir
rm -f xtts-gtk-x86_64.AppImage

# Install PyInstaller if not available
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Build with PyInstaller
echo "🏗️  Building executable with PyInstaller..."
if [ -f "xtts-gtk.spec" ]; then
    echo "Using spec file..."
    pyinstaller xtts-gtk.spec
else
    echo "Using command line build..."
    pyinstaller main.py --name xtts-gtk --onefile --noconsole --clean \
        --hidden-import gi.repository.Gtk \
        --hidden-import gi.repository.GObject \
        --hidden-import gi.repository.GLib \
        --hidden-import gi.repository.Gdk \
        --collect-all gi
fi

# Check if build was successful
if [ ! -f "dist/xtts-gtk" ]; then
    echo "❌ Build failed: executable not found"
    exit 1
fi

echo "✅ Executable built successfully!"

# Create AppImage
echo "📦 Creating AppImage..."
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p AppDir/usr/share/applications

# Copy executable
cp dist/xtts-gtk AppDir/usr/bin/
chmod +x AppDir/usr/bin/xtts-gtk

# Copy icon
cp logo.png AppDir/usr/share/icons/hicolor/256x256/apps/xtts-gtk.png
cp logo.png AppDir/xtts-gtk.png

# Create AppRun script
cat > AppDir/AppRun << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/xtts-gtk" "$@"
EOF
chmod +x AppDir/AppRun

# Create desktop file
cat > AppDir/xtts-gtk.desktop << 'EOF'
[Desktop Entry]
Name=XTTS-GTK
Exec=xtts-gtk
Icon=xtts-gtk
Type=Application
Categories=AudioVideo;Audio;
Comment=Text-to-Speech Synthesis Tool
EOF

# Download appimagetool if not available
if ! command -v appimagetool &> /dev/null; then
    echo "📥 Downloading appimagetool..."
    APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    wget -q "$APPIMAGETOOL_URL" -O appimagetool
    chmod +x appimagetool
+    ./appimagetool AppDir xtts-gtk-x86_64.AppImage
+    rm appimagetool
+else
+    appimagetool AppDir xtts-gtk-x86_64.AppImage
+fi

+# Check if AppImage was created
+if [ ! -f "xtts-gtk-x86_64.AppImage" ]; then
+    echo "❌ AppImage creation failed"
+    exit 1
+fi

echo "✅ AppImage created successfully!"
+echo ""
+echo "📋 Build Summary:"
+echo "   Executable: dist/xtts-gtk"
+echo "   AppImage: xtts-gtk-x86_64.AppImage"
+echo ""
+echo "🚀 To run the AppImage:"
+echo "   chmod +x xtts-gtk-x86_64.AppImage"
+echo "   ./xtts-gtk-x86_64.AppImage"
+echo ""
+echo "🧹 Cleaning up..."
+rm -rf AppDir

echo "🎉 Build complete!"
