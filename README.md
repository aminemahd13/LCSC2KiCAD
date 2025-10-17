# LCSC to KiCad Importer

A professional KiCad plugin that allows you to easily import parts (symbols, footprints, and 3D models) from the LCSC library directly into KiCad.

## Key Features

- **Seamless Import**: Quickly import LCSC parts by entering their part number (e.g., C2040)
- **Complete Package**: Import symbols, footprints, and 3D models in one click
- **Direct Access**: Integrated into the toolbar for easy access within the PCB editor
- **Auto-Save**: Imported parts are stored in `/Documents/KiCad/lcsc2kicad`, ready for use
- **Professional Grade**: Clean UI with proper error handling and logging

## Installation

### Windows

1. **Clone or Download** this repository

2. **Move Files** to your KiCad plugins directory:
   ```
   C:\Users\<your_username>\Documents\KiCad\<version>\scripting\plugins\
   ```

3. **Ensure Structure**: Make sure `LCSC Importer.py` is not inside any subfolder

4. **Install Dependencies** (if prompted):
   Open KiCad Command Prompt (found in Start Menu under KiCad folder) and run:
   ```
   pip install requests pydantic
   ```

### macOS

1. **Clone or Download** this repository

2. **Move Files** to:
   ```
   /Users/<USER>/Documents/KiCad/<version>/scripting/plugins/
   ```

3. **Install Dependencies**:
   ```bash
   /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/pip3 install requests pydantic
   ```

### Linux

1. **Clone or Download** this repository

2. **Move Files** to:
   ```
   ~/.kicad/<version>/scripting/plugins/
   ```

3. **Install Dependencies**:
   ```bash
   pip3 install requests pydantic
   ```

## Configuration

After running the plugin for the first time:

1. **Add Environment Variable**:
   - Go to: `Preferences > Configure Paths`
   - Add variable `LCSC2KICAD`:
     - Windows: `C:/Users/<username>/Documents/KiCad/lcsc2kicad/`
     - macOS: `/Users/<username>/Documents/KiCad/lcsc2kicad/`
     - Linux: `/home/<username>/Documents/KiCad/lcsc2kicad/`

2. **Add Symbol Library**:
   - Go to: `Preferences > Manage Symbol Libraries`
   - Add global library `lcsc2kicad`: `${LCSC2KICAD}/lcsc2kicad.kicad_sym`

3. **Add Footprint Library**:
   - Go to: `Preferences > Manage Footprint Libraries`
   - Add global library `lcsc2kicad`: `${LCSC2KICAD}/lcsc2kicad.pretty`

## Usage

1. Click the LCSC icon in the toolbar (PCB Editor or Schematic Editor)
2. Enter the LCSC part number (e.g., C2040, C5171)
3. Click OK
4. The plugin will download and import the symbol, footprint, and 3D model
5. Find your part in the symbol/footprint libraries

## Troubleshooting

### Missing Dependencies
If you see an error about missing modules, install dependencies as described in Installation section.

### API Connection Issues
- Ensure you have an active internet connection
- Check if the LCSC part number is correct
- Some parts may not have CAD data available

### Library Not Found
Make sure you've completed the Configuration steps above.

