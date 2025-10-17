# Project Structure

```
LCSC2KiCAD/
├── README.md                 # Main documentation
├── QUICKSTART.md            # Quick start guide for users
├── requirements.txt         # Python dependencies
├── examples.py              # Example usage scripts
├── .gitignore              # Git ignore patterns
│
├── LCSC Importer.py        # ⭐ Main KiCad plugin file (must be in plugins folder)
│
└── lcsc2kicad/             # Core conversion package
    ├── __init__.py         # Package initialization
    ├── __main__.py         # Command-line interface entry point
    ├── api.py              # LCSC/EasyEDA API client
    ├── converter.py        # Main conversion orchestrator
    ├── utils.py            # Utility functions
    ├── icon.png            # Plugin toolbar icon
    │
    ├── parsers/            # Data parsers (EasyEDA → Internal format)
    │   ├── __init__.py
    │   ├── symbol_parser.py      # Parse symbol data
    │   ├── footprint_parser.py   # Parse footprint data
    │   └── model_3d_parser.py    # Parse 3D model data
    │
    ├── exporters/          # Data exporters (Internal format → KiCad)
    │   ├── __init__.py
    │   ├── symbol_exporter.py    # Export to .kicad_sym format
    │   ├── footprint_exporter.py # Export to .kicad_mod format
    │   └── model_3d_exporter.py  # Export to .wrl/.step format
    │
    └── tests/              # Test modules
        ├── __init__.py
        └── test_basic.py   # Basic functionality tests
```

## Key Files

### User-Facing Files

- **LCSC Importer.py** - The main plugin file that KiCad loads. This provides the GUI interface.
- **README.md** - Complete documentation with installation instructions.
- **QUICKSTART.md** - Quick start guide for first-time users.
- **examples.py** - Example scripts showing programmatic usage.

### Core Package (lcsc2kicad/)

- **__main__.py** - Command-line interface for standalone usage
- **api.py** - Handles all communication with LCSC/EasyEDA APIs
- **converter.py** - Orchestrates the conversion process
- **utils.py** - Helper functions (logging, file operations, etc.)

### Parsers (lcsc2kicad/parsers/)

Parse EasyEDA JSON data into an intermediate format:
- **symbol_parser.py** - Parses symbol shapes, pins, graphics
- **footprint_parser.py** - Parses footprint pads, tracks, shapes
- **model_3d_parser.py** - Handles 3D model downloads and parsing

### Exporters (lcsc2kicad/exporters/)

Export intermediate format to KiCad files:
- **symbol_exporter.py** - Generates .kicad_sym files (KiCad 6+ format)
- **footprint_exporter.py** - Generates .kicad_mod files
- **model_3d_exporter.py** - Generates .wrl (VRML) and .step files

## Data Flow

```
LCSC Part Number
       ↓
   [API Client]  ← Fetches JSON data from LCSC/EasyEDA
       ↓
   [Parsers]     ← Converts JSON to intermediate Python objects
       ↓
   [Converter]   ← Orchestrates the process
       ↓
   [Exporters]   ← Generates KiCad format files
       ↓
   KiCad Library Files (.kicad_sym, .kicad_mod, .wrl, .step)
```

## Installation Structure

When installed, the plugin creates:

```
Documents/KiCad/lcsc2kicad/
├── lcsc2kicad.kicad_sym      # Symbol library
├── lcsc2kicad.pretty/        # Footprint library folder
│   ├── Component1.kicad_mod
│   ├── Component2.kicad_mod
│   └── ...
└── lcsc2kicad.3dshapes/      # 3D models folder
    ├── Component1.wrl
    ├── Component1.step
    ├── Component2.wrl
    ├── Component2.step
    └── ...
```

## File Formats

### Symbol Library (.kicad_sym)
- KiCad 6.0+ format
- S-expression based
- Contains all symbols in one file
- Properties include: Reference, Value, Footprint, Datasheet, LCSC ID, Manufacturer

### Footprint (.kicad_mod)
- KiCad 6.0+ format
- S-expression based
- One file per footprint
- Includes pads, silkscreen, fab layer, courtyard

### 3D Models
- **.wrl** - VRML format for display in KiCad
- **.step** - STEP format for mechanical CAD export

## Dependencies

### Required
- **requests** - HTTP client for API calls
- **pydantic** - Data validation (if using advanced parsing)

### KiCad Specific
- **pcbnew** - KiCad Python module (included with KiCad)
- **wx** - wxPython GUI toolkit (included with KiCad)

## Architecture Principles

1. **Separation of Concerns**
   - API layer handles network communication
   - Parsers handle data transformation
   - Exporters handle file generation

2. **Error Handling**
   - Each layer catches and logs errors
   - Graceful degradation (e.g., continue without 3D model if unavailable)
   - User-friendly error messages

3. **Extensibility**
   - Easy to add new parsers for different data formats
   - Easy to add new exporters for different KiCad versions
   - Modular architecture allows component reuse

4. **Professional UI**
   - Clean dialog interface
   - Progress indicators
   - Informative success/error messages
   - Comprehensive logging for debugging

## Development Workflow

1. **Fetch Data** (api.py)
2. **Parse Data** (parsers/)
3. **Convert** (converter.py orchestrates)
4. **Export** (exporters/)
5. **Validate** (tests/)

## Logging

All modules use Python's logging framework:
- Plugin operations logged to `lcsc2kicad.log` in plugin directory
- Command-line operations logged to console
- DEBUG level available for troubleshooting

## Future Enhancements

Possible improvements:
- Support for KiCad 5.x format
- Batch import from BOM files
- Component search interface
- Local caching of downloaded data
- Advanced 3D model conversion
- Component preview before import
- Library management tools
