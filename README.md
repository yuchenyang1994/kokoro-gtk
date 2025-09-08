# XTTS-GTK

A modern GTK4-based desktop application for text-to-speech synthesis using XTTS models.

![Build Status](https://github.com/your-username/xtts-gtk/workflows/Build%20and%20Release/badge.svg)

## Features

- 🎤 **Multi-language Support**: Generate speech in multiple languages including Chinese and English
- 🎨 **Modern GTK4 Interface**: Clean, responsive desktop application
- 🎵 **Voice Cloning**: Use custom voice samples for personalized speech synthesis
- 💾 **History Management**: Keep track of your generated audio files
- 📁 **Flexible Output**: Choose where to save your generated audio files
- 🚀 **GPU Acceleration**: Automatic CUDA support when available

## Download

### Latest Releases

Get the latest pre-built binaries from the [Releases](https://github.com/your-username/xtts-gtk/releases) page.

#### Linux
- Download `xtts-gtk-linux-x86_64.AppImage`
- Make it executable: `chmod +x xtts-gtk-linux-x86_64.AppImage`
- Run: `./xtts-gtk-linux-x86_64.AppImage`

#### macOS
- Download `xtts-gtk-macos.dmg`
- Open the DMG and drag XTTS-GTK to your Applications folder
- Run from Applications or Launchpad

### Development Builds

Development builds are available as GitHub Actions artifacts. To access them:
1. Go to the [Actions tab](https://github.com/your-username/xtts-gtk/actions)
2. Click on the latest successful build
3. Download the artifacts at the bottom of the page

## Building from Source

### Prerequisites

- Python 3.11+
- GTK4 development libraries
- PyGObject

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 libgtk-4-dev libglib2.0-dev gobject-introspection

# Clone and install
git clone https://github.com/your-username/xtts-gtk.git
cd xtts-gtk
pip install .
python main.py
```

### macOS

```bash
# Install system dependencies
brew install pygobject3 gtk4 glib gobject-introspection pkg-config

# Clone and install
git clone https://github.com/your-username/xtts-gtk.git
cd xtts-gtk
pip install .
python main.py
```

## Usage

1. **Launch the Application**: Start XTTS-GTK from your applications menu or run the executable

2. **Enter Text**: Type or paste the text you want to convert to speech in the main text area

3. **Configure Settings**:
   - **Language**: Choose your target language (Chinese or English)
   - **Voice Sample**: Optionally select a WAV file for voice cloning
   - **Output Directory**: Choose where to save generated audio files

4. **Generate Speech**: Click "Generate Speech" and wait for the model to process your text

5. **Access History**: Generated files appear in the history panel on the left - click any item to reload the text

## Development

### Project Structure

```
xtts-gtk/
├── main.py              # Main application entry point
├── settings.py          # Application settings and configurations
├── tts_installer.py     # TTS model dependency management
├── logo.png             # Application icon
├── pyproject.toml       # Python project configuration
└── .github/
    └── workflows/
        └── build.yml    # CI/CD build configuration
```

### Building

The project uses GitHub Actions for automated building:

```bash
# Local development build
pyinstaller main.py --name xtts-gtk --onefile --noconsole

# Linux AppImage (requires appimagetool)
./build-appimage.sh

# macOS DMG (requires hdiutil)
./build-macos.sh
```

## Troubleshooting

### Linux Issues

**AppImage won't run:**
```bash
chmod +x xtts-gtk-linux-x86_64.AppImage
./xtts-gtk-linux-x86_64.AppImage
```

**GTK4 errors:**
Ensure you have GTK4 installed:
```bash
sudo apt-get install libgtk-4-dev gir1.2-gtk-4.0
```

### macOS Issues

**"App can't be opened" error:**
```bash
sudo xattr -r -d com.apple.quarantine /Applications/xtts-gtk.app
```

**GTK4 import errors:**
Ensure Homebrew paths are set:
```bash
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
```

### General Issues

**Model download fails:**
- Check internet connection
- Ensure sufficient disk space (~2GB for the model)
- Try running with proxy settings if behind a firewall

**CUDA not detected:**
- Ensure PyTorch with CUDA support is installed
- Check NVIDIA drivers are up to date
- The app will automatically fall back to CPU if CUDA is unavailable

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Coqui TTS](https://github.com/coqui-ai/TTS) for the amazing TTS models
- [GTK](https://gtk.org/) for the modern UI toolkit
- [PyGObject](https://pygobject.readthedocs.io/) for Python GTK bindings

## Support

If you encounter any issues:
1. Check the [Issues](https://github.com/your-username/xtts-gtk/issues) page
2. Create a new issue with detailed information about your problem
3. Include your operating system, Python version, and error messages