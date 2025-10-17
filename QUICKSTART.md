# Quick Start Guide

## Installation

### 1. Install Dependencies

```bash
# Windows (use KiCad Command Prompt)
pip install requests pydantic

# macOS
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/pip3 install requests pydantic

# Linux
pip3 install requests pydantic
```

### 2. Install Plugin

1. Copy all files to your KiCad plugins directory:
   - **Windows**: `C:\Users\<username>\Documents\KiCad\<version>\scripting\plugins\`
   - **macOS**: `/Users/<username>/Documents/KiCad/<version>/scripting/plugins/`
   - **Linux**: `~/.kicad/<version>/scripting/plugins/`

2. Make sure `LCSC Importer.py` is in the plugins folder (not in a subfolder)

3. Restart KiCad

## First Time Setup

### 1. Run the Plugin Once

- Open KiCad PCB Editor or Schematic Editor
- Click the LCSC icon in the toolbar
- Enter any part number (e.g., "C2040")
- This creates the library structure

### 2. Configure KiCad

**Add Environment Variable:**
1. Open KiCad
2. Go to `Preferences > Configure Paths`
3. Click "Add"
4. Name: `LCSC2KICAD`
5. Path:
   - Windows: `C:/Users/<username>/Documents/KiCad/lcsc2kicad/`
   - macOS: `/Users/<username>/Documents/KiCad/lcsc2kicad/`
   - Linux: `/home/<username>/Documents/KiCad/lcsc2kicad/`

**Add Symbol Library:**
1. Go to `Preferences > Manage Symbol Libraries`
2. Click "Add existing library to table" (folder icon)
3. Navigate to: `${LCSC2KICAD}/lcsc2kicad.kicad_sym`
4. Click OK

**Add Footprint Library:**
1. Go to `Preferences > Manage Footprint Libraries`
2. Click "Add existing library to table" (folder icon)
3. Navigate to: `${LCSC2KICAD}/lcsc2kicad.pretty`
4. Click OK

## Usage

### Import a Part

1. Click the **LCSC icon** in the toolbar
2. Enter the **LCSC part number** (e.g., C2040, C5171, R25)
3. Click **Import**
4. Wait for confirmation

### Find Your Part

**In Schematic Editor:**
1. Press `A` to add a symbol
2. Search for your part name or LCSC ID
3. Place the symbol

**In PCB Editor:**
1. When updating PCB from schematic, footprints are automatically assigned
2. Or manually assign footprint from `lcsc2kicad` library

## Common Part Numbers to Test

- **C2040** - 100nF ceramic capacitor (0603)
- **C25804** - 10uF ceramic capacitor (0805)
- **R25** - 10K resistor (0603)
- **C5171** - 22pF ceramic capacitor (0603)

## Troubleshooting

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

## Log Files

Check these log files for troubleshooting:
- Plugin log: `<plugin_folder>/lcsc2kicad.log`
- Conversion details logged during import

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

## Support

- Check `README.md` for detailed documentation
- Review `examples.py` for programmatic usage
- Check log files for error details

## Tips

1. **Import frequently used parts first** to build your library
2. **Use descriptive names** when components have generic names
3. **Check footprints** after import to ensure they match your PCB requirements
4. **3D models** may not be available for all components
5. **Keep your library organized** by periodically reviewing imported parts

## Next Steps

- Import your BOM parts one by one
- Organize your custom library structure
- Share your library with your team
- Contribute improvements to the project!

Happy designing! 🎉
