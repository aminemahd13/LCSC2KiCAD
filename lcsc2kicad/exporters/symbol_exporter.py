"""
Symbol exporter for KiCad format (KiCad 6.0+)
Uses new architecture from easyeda_importer and export_kicad_symbol
"""

import logging
import os
from pathlib import Path
from typing import Dict

from lcsc2kicad.easyeda.easyeda_importer_symbol import EasyedaSymbolImporter
from lcsc2kicad.kicad.export_kicad_symbol import ExporterSymbolKicad
from lcsc2kicad.kicad.parameters_kicad_symbol import KicadVersion
from lcsc2kicad.kicad.symbol_fallback import create_fallback_symbol_from_cad_data


class SymbolExporter:
    """Export symbols to KiCad format"""
    
    def __init__(self, symbol_data: Dict, component_name: str, lcsc_id: str):
        """
        Initialize exporter
        
        Args:
            symbol_data: CAD data dict (should have "dataStr" field from API)
            component_name: Component name
            lcsc_id: LCSC part number
        """
        self.cad_data = symbol_data
        self.component_name = component_name
        self.lcsc_id = lcsc_id
        self.library_name = None
    
    def export(self, lib_path: str, overwrite: bool = True) -> bool:
        """
        Export symbol to KiCad library
        
        Args:
            lib_path: Path to .kicad_sym library file
            overwrite: Whether to overwrite existing symbol (default: True)
            
        Returns:
            True if successful
        """
        try:
            # Extract library name from path for footprint reference
            self.library_name = Path(lib_path).stem
            
            logging.info(f"Exporting symbol {self.component_name} to {lib_path}")
            
            # Import EasyEDA symbol structure from cad_data
            importer = EasyedaSymbolImporter()
            ee_symbol = importer.extract_easyeda_data(
                easyeda_symbol=self.cad_data,  # Pass full cad_data dict
                name=self.component_name,
                lcsc_id=self.lcsc_id
            )
            
            # Check if symbol has any content
            if (not ee_symbol.pins and not ee_symbol.rectangles and 
                not ee_symbol.circles and not ee_symbol.polygons):
                logging.warning(
                    f"Symbol {self.component_name} has no graphical elements in EasyEDA data."
                )
                logging.info(f"Creating fallback symbol for {self.component_name}")
                
                # Create fallback symbol
                from lcsc2kicad.kicad.symbol_fallback import create_fallback_symbol_from_cad_data
                fallback_symbol = create_fallback_symbol_from_cad_data(
                    cad_data=self.cad_data,
                    component_name=self.component_name,
                    lcsc_id=self.lcsc_id
                )
                
                # Use fallback for export
                symbol_content = fallback_symbol.export(kicad_version=KicadVersion.v6)
                
                # Add library prefix to footprint
                if fallback_symbol.info.package:
                    symbol_content = symbol_content.replace(
                        f'"{fallback_symbol.info.package}"',
                        f'"{self.library_name}:{fallback_symbol.info.package}"'
                    )
            else:
                # Convert to KiCad format (normal path)
                exporter = ExporterSymbolKicad(
                    symbol=ee_symbol,
                    kicad_version=KicadVersion.v6
                )
                symbol_content = exporter.export(footprint_lib_name=self.library_name)
            
            # Read existing library
            if os.path.exists(lib_path):
                with open(lib_path, "r", encoding="utf-8") as f:
                    lib_content = f.read()
                
                # Check if symbol already exists
                symbol_id = self.component_name.replace(" ", "_")
                if f'(symbol "{symbol_id}"' in lib_content:
                    if not overwrite:
                        logging.warning(f"Symbol {symbol_id} already exists, skipping")
                        return True
                    else:
                        # Remove existing symbol
                        lib_content = self._remove_existing_symbol(lib_content, symbol_id)
            else:
                # Create new library file
                lib_content = "(kicad_symbol_lib\n  (version 20211014)\n  (generator lcsc2kicad)\n)\n"
            
            # Insert symbol before closing parenthesis
            insert_pos = lib_content.rfind(")")
            if insert_pos == -1:
                logging.error("Invalid library format")
                return False
            
            new_content = (
                lib_content[:insert_pos] +
                symbol_content +
                lib_content[insert_pos:]
            )
            
            # Write back to file
            with open(lib_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            logging.info(f"Successfully exported symbol {self.component_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting symbol: {e}", exc_info=True)
            return False
    
    def _remove_existing_symbol(self, content: str, symbol_id: str) -> str:
        """Remove existing symbol from library"""
        # Find symbol start
        start_marker = f'  (symbol "{symbol_id}"'
        start = content.find(start_marker)
        
        if start == -1:
            return content
        
        # Find matching closing parenthesis
        level = 0
        pos = start
        while pos < len(content):
            if content[pos] == '(':
                level += 1
            elif content[pos] == ')':
                level -= 1
                if level == 0:
                    # Found the end
                    return content[:start] + content[pos+1:]
            pos += 1
        
        return content

