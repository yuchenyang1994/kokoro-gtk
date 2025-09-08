#!/bin/bash

# XTTS-GTK Development Setup Script
# This script sets up the development environment for XTTS-GTK

set -e

echo "🚀 Setting up XTTS-GTK development environment..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "📦 Detected Linux system"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "🍎 Detected macOS system"
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

# Install system dependencies
if [[ "$OS" == "linux" ]]; then
    echo "📥 Installing Linux system dependencies..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            libgirepository1.0-dev \
            gcc \
            libcairo2-dev \
            pkg-config \
            python3-dev \
            gir1.2-gtk-4.0 \
            libgtk-4-dev \
            libglib2.0-dev \
            gobject-introspection \
            libgirepository-1.0-1 \
            libgirepository-2.0-dev \
            gir1.2-glib-2.0 \
            libgirepository1.0-doc
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y \
            gobject-introspection-devel \
            gtk4-devel \
            glib2-devel \
            cairo-devel \
            pkg-config \
            python3-devel
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --needed \
            gobject-introspection \
            gtk4 \
            glib2 \
            cairo \
            pkg-config \
            python
    else
        echo "❌ Unsupported Linux distribution. Please install GTK4 development packages manually."
        exit 1
    fi
elif [[ "$OS" == "macos" ]]; then
    echo "📥 Installing macOS system dependencies..."
    if command -v brew &> /dev/null; then
        brew install pygobject3 gtk4 glib gobject-introspection pkg-config
    else
        echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh"
        exit 1
    fi
fi

# Check Python version
echo "🐍 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.11 or later."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "📋 Python version: $PYTHON_VERSION"

# Check if pip is available
echo "📦 Checking pip..."
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip not found. Please install pip."
    exit 1
fi

PIP_CMD="pip"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
$PIP_CMD install --upgrade pip
$PIP_CMD install -e .

# Install development dependencies
echo "🔧 Installing development dependencies..."
$PIP_CMD install pyinstaller

# Verify GTK4 installation
echo "✅ Verifying GTK4 installation..."
if [[ "$OS" == "linux" ]]; then
    pkg-config --modversion gtk4 || echo "⚠️  GTK4 pkg-config not found"
+    ls -la /usr/lib/girepository-1.0/ | grep -i gtk || echo "⚠️  GTK typelibs not found"
+elif [[ "$OS" == "macos" ]]; then
+    pkg-config --modversion gtk4 || echo "⚠️  GTK4 pkg-config not found"
+fi
+
+echo ""
+echo "🎉 Development environment setup complete!"
+echo ""
+echo "🚀 To run the application:"
+echo "   python main.py"
+echo ""
+echo "🔨 To build the application:"
+echo "   - Linux: ./build-linux.sh"
+echo "   - macOS: ./build-macos.sh"
+echo ""
+echo "📖 For more information, see README.md"
