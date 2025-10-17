# Project Structure

```
LCSC2KiCAD/
├── README.md                 # Main documentation
├── QUICKSTART.md            # Quick start guide for users
├── requirements.txt         # Python dependencies
├── examples.py              # Example usage scripts
├── .gitignore              # Git ignore patterns
│
├── LCSC Importer.py        # Main KiCad plugin file (must be in plugins folder)
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


# Installation Structure

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
