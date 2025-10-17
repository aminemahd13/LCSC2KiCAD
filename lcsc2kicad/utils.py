"""
Utility functions for LCSC to KiCad converter
"""

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logger(log_level: int = logging.INFO, log_file: Optional[str] = None):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    root_log = logging.getLogger()
    root_log.setLevel(log_level)
    
    # Clear existing handlers
    root_log.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    root_log.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(funcName)s] %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        root_log.addHandler(file_handler)


def create_library_structure(base_path: Path) -> None:
    """
    Create the directory structure for KiCad libraries
    
    Args:
        base_path: Base directory path
    """
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (base_path / "lcsc2kicad.pretty").mkdir(exist_ok=True)  # Footprints
    (base_path / "lcsc2kicad.3dshapes").mkdir(exist_ok=True)  # 3D models
    
    # Create symbol library file if it doesn't exist
    symbol_lib = base_path / "lcsc2kicad.kicad_sym"
    if not symbol_lib.exists():
        with open(symbol_lib, "w", encoding="utf-8") as f:
            f.write(
                "(kicad_symbol_lib\n"
                "  (version 20211014)\n"
                "  (generator lcsc2kicad)\n"
                ")\n"
            )
    
    logging.info(f"Library structure created at: {base_path}")


def sanitize_name(name: str) -> str:
    """
    Sanitize component name for file system
    
    Args:
        name: Original name
        
    Returns:
        Sanitized name
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    
    # Remove leading/trailing spaces
    name = name.strip()
    
    # Replace multiple spaces with single underscore
    name = " ".join(name.split())
    name = name.replace(" ", "_")
    
    return name


def convert_to_mm(value: float) -> float:
    """
    Convert EasyEDA units to millimeters
    
    Args:
        value: Value in EasyEDA units
        
    Returns:
        Value in millimeters
    """
    return float(value) * 10 * 0.0254


def mm_to_mil(value: float) -> float:
    """
    Convert millimeters to mils
    
    Args:
        value: Value in millimeters
        
    Returns:
        Value in mils
    """
    return value / 0.0254


def ensure_directory_exists(file_path: str) -> None:
    """
    Ensure the directory for a file path exists
    
    Args:
        file_path: Full file path
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
