"""
Main entry point for LCSC to KiCad converter
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List

from lcsc2kicad import __version__
from lcsc2kicad.api import LCSCApi
from lcsc2kicad.converter import ComponentConverter
from lcsc2kicad.utils import setup_logger, create_library_structure


def get_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="Convert LCSC components to KiCad libraries"
    )
    
    parser.add_argument(
        "--lcsc_id",
        required=True,
        type=str,
        help="LCSC part number (e.g., C2040)"
    )
    
    parser.add_argument(
        "--symbol",
        action="store_true",
        help="Import symbol only"
    )
    
    parser.add_argument(
        "--footprint",
        action="store_true",
        help="Import footprint only"
    )
    
    parser.add_argument(
        "--3d",
        action="store_true",
        help="Import 3D model only"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Import symbol, footprint, and 3D model"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory path"
    )
    
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Do not overwrite existing components (default: overwrite)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    return parser


def validate_arguments(args: argparse.Namespace) -> bool:
    """
    Validate command line arguments
    
    Returns:
        True if valid, False otherwise
    """
    # Validate LCSC ID format
    if not args.lcsc_id.startswith("C"):
        logging.error("LCSC ID must start with 'C'")
        return False
    
    # Check if at least one action is specified
    if args.full:
        args.symbol = args.footprint = args.__dict__["3d"] = True
    
    if not (args.symbol or args.footprint or args.__dict__.get("3d", False)):
        logging.error("Specify at least one action: --symbol, --footprint, --3d, or --full")
        return False
    
    # Setup output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        # Default to Documents/KiCad/lcsc2kicad
        docs = Path.home() / "Documents" / "KiCad" / "lcsc2kicad"
        output_dir = docs
    
    # Create directory structure
    try:
        create_library_structure(output_dir)
        args.output = str(output_dir / "lcsc2kicad")
        logging.info(f"Using output directory: {output_dir}")
    except Exception as e:
        logging.error(f"Failed to create output directory: {e}")
        return False
    
    return True


def main(argv: List[str] = None) -> int:
    """
    Main execution function
    
    Args:
        argv: Command line arguments
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if argv is None:
        argv = sys.argv[1:]
    
    print(f"LCSC to KiCad Converter v{__version__}")
    
    # Parse arguments
    parser = get_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as err:
        return err.code
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logger(log_level)
    
    # Validate arguments
    if not validate_arguments(args):
        return 1
    
    lcsc_id = args.lcsc_id
    logging.info(f"Processing component: {lcsc_id}")
    
    # Fetch component data from API
    api = LCSCApi()
    cad_data = api.get_cad_data(lcsc_id)
    
    if not cad_data:
        logging.error(f"Failed to fetch component data for {lcsc_id}")
        print(f"Error: Could not retrieve data for part {lcsc_id}")
        print("Please check:")
        print("  - Part number is correct")
        print("  - You have internet connection")
        print("  - LCSC API is accessible")
        return 1
    
    # Convert component
    try:
        converter = ComponentConverter(
            cad_data=cad_data,
            output_base=args.output,
            overwrite=not args.no_overwrite  # Invert the flag logic
        )
        
        success = True
        
        if args.symbol:
            if not converter.convert_symbol():
                success = False
                logging.error(f"Failed to convert symbol for {lcsc_id}")
        
        if args.footprint:
            if not converter.convert_footprint():
                success = False
                logging.error(f"Failed to convert footprint for {lcsc_id}")
        
        if args.__dict__.get("3d", False):
            if not converter.convert_3d_model():
                success = False
                logging.error(f"Failed to convert 3D model for {lcsc_id}")
        
        if success:
            logging.info(f"Successfully converted {lcsc_id}")
            print(f"\nSuccessfully imported {lcsc_id}!")
            return 0
        else:
            logging.error(f"Partial failure converting {lcsc_id}")
            print(f"\nPartially imported {lcsc_id} (some components failed)")
            return 1
            
    except Exception as e:
        logging.error(f"Error converting component: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
