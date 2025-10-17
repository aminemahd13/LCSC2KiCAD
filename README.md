# LCSC to KiCad Importer

A KiCad plugin that allows you to easily import parts (symbols, footprints, and 3D models) from the LCSC library directly into KiCad.

## Key Features

- **Seamless Import**: Quickly import LCSC parts by entering their part number (e.g., C2040)
- **Complete Package**: Import symbols, footprints, and 3D models in one click.
- **Direct Access**: Integrated into the toolbar for easy access within the PCB editor.
- **Auto-Generate symbols** : For components with no predefined symbols in the LCSC library.
- **Auto-Save**: Imported parts are stored in `/Documents/KiCad/lcsc2kicad`, ready for use.


## Installation

### Windows

1. **Clone or Download** this repository

2. **Move Files** to your KiCad plugins directory:
   ```
   C:\Users\<your_username>\Documents\KiCad\<version>\scripting\plugins\
   ```

3. **Ensure Structure**: Make sure `LCSC Importer.py` is not inside any subfolder, it must be in the plugins folder

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

1. Click the LCSC icon in the toolbar in the PCB Editor
2. Enter the LCSC part number (e.g., C2040, C5171)
3. Click Enter
4. The plugin will download and import the symbol, footprint, and 3D model
5. Find your part in the symbol/footprint libraries

## Command Line Usage

You can also use the converter from command line:

```bash
# Full import (symbol, footprint, 3D model)
python -m lcsc2kicad --lcsc_id C2040 --full

# Symbol only
python -m lcsc2kicad --lcsc_id C2040 --symbol

# Custom output location
python -m lcsc2kicad --lcsc_id C2040 --full --output ./my_library/parts

# See all options
python -m lcsc2kicad --help
```


## Troubleshooting

### Missing Dependencies
If you see an error about missing modules, install dependencies as described in Installation section.

### API Connection Issues
- Ensure you have an active internet connection
- Check if the LCSC part number is correct
- Some parts may not have CAD data available

### "Missing dependencies" error
- Install requests and pydantic using pip (see Installation)
- Make sure to use the correct Python version (KiCad's Python)

### "Symbol not found" error
- Make sure you added the symbol library in KiCad preferences
- Check that the environment variable `LCSC2KICAD` is correctly set
- Try restarting KiCad

### "API connection failed" error
- Check your internet connection
- Verify the LCSC part number is correct
- Try again later (API might be temporarily unavailable)

### Plugin doesn't appear in toolbar
- Make sure `LCSC Importer.py` is directly in the plugins folder
- Check `lcsc2kicad.log` for errors
- Try reinstalling the plugin


### Errors
- Open a new issue if the troubleshooting steps above do not work.

