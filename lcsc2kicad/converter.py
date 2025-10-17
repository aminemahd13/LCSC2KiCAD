"""
Main converter class for transforming LCSC data to KiCad format
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional

from lcsc2kicad.api import LCSCApi
from lcsc2kicad.parsers.symbol_parser import SymbolParser
from lcsc2kicad.parsers.footprint_parser import FootprintParser
from lcsc2kicad.parsers.model_3d_parser import Model3DParser
from lcsc2kicad.exporters.symbol_exporter import SymbolExporter
from lcsc2kicad.exporters.footprint_exporter import FootprintExporter
from lcsc2kicad.exporters.model_3d_exporter import Model3DExporter
from lcsc2kicad.utils import sanitize_name


class ComponentConverter:
    """Handles conversion of LCSC components to KiCad format"""
    
    def __init__(self, cad_data: Dict, output_base: str, overwrite: bool = False):
        """
        Initialize converter
        
        Args:
            cad_data: Component CAD data from API
            output_base: Base path for output files (without extension)
            overwrite: Whether to overwrite existing files
        """
        self.cad_data = cad_data
        self.output_base = output_base
        self.overwrite = overwrite
        self.api = LCSCApi()
        
        # Extract component info
        self.component_name = sanitize_name(
            cad_data.get("title", "Unknown")
        )
        self.lcsc_id = cad_data.get("lcsc", "")
        
        logging.info(f"Initializing converter for {self.component_name} ({self.lcsc_id})")
    
    def convert_symbol(self) -> bool:
        """
        Convert and export symbol
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logging.info(f"Converting symbol for {self.component_name}")
            
            if "dataStr" not in self.cad_data:
                logging.error("No symbol data in CAD data")
                return False
            
            # Parse symbol data
            parser = SymbolParser(self.cad_data)
            symbol_data = parser.parse()
            
            if not symbol_data:
                logging.error("Failed to parse symbol data")
                return False
            
            # Export to KiCad format
            exporter = SymbolExporter(symbol_data, self.component_name, self.lcsc_id)
            symbol_lib_path = f"{self.output_base}.kicad_sym"
            
            success = exporter.export(symbol_lib_path, overwrite=self.overwrite)
            
            if success:
                logging.info(f"Symbol exported to {symbol_lib_path}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error converting symbol: {e}", exc_info=True)
            return False
    
    def convert_footprint(self) -> bool:
        """
        Convert and export footprint (with optional 3D model)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logging.info(f"Converting footprint for {self.component_name}")
            
            if "packageDetail" not in self.cad_data:
                logging.error("No footprint data in CAD data")
                return False
            
            # Parse footprint data
            parser = FootprintParser(self.cad_data)
            footprint_data = parser.parse()
            
            if not footprint_data:
                logging.error("Failed to parse footprint data")
                return False
            
            # Try to parse and export 3D model
            model_data = None
            if "shapes" in footprint_data:
                model_parser = Model3DParser(self.api)
                model_data = model_parser.parse_from_footprint(footprint_data["shapes"])
                
                if model_data:
                    # Export 3D model files
                    model_dir = f"{self.output_base}.3dshapes"
                    model_exporter = Model3DExporter(model_data, self.component_name)
                    if model_exporter.export(model_dir, overwrite=self.overwrite):
                        logging.info(f"3D model exported successfully")
                        # Add model reference to footprint data
                        # Use relative path or environment variable
                        base_name = os.path.basename(self.output_base)
                        footprint_data["model_3d"] = {
                            "path": f"${{LCSC2KICAD}}/{base_name}.3dshapes",
                            "name": self.component_name.replace(" ", "_"),
                            "transform": model_data.get("transform", {}),
                        }
            
            # Export to KiCad format
            exporter = FootprintExporter(footprint_data, self.component_name)
            footprint_dir = f"{self.output_base}.pretty"
            
            success = exporter.export(footprint_dir, overwrite=self.overwrite)
            
            if success:
                logging.info(f"Footprint exported to {footprint_dir}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error converting footprint: {e}", exc_info=True)
            return False
    
    def convert_3d_model(self) -> bool:
        """
        Convert and export 3D model (standalone)
        
        Note: 3D models are normally exported with footprints.
        This method is for standalone 3D model export.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logging.info(f"Converting 3D model for {self.component_name}")
            
            # Check if 3D model data exists
            if "packageDetail" not in self.cad_data:
                logging.warning("No package data for 3D model")
                return False
            
            package_detail = self.cad_data["packageDetail"]
            
            if "dataStr" not in package_detail:
                logging.warning("No 3D model data available")
                return False
            
            data_str = package_detail["dataStr"]
            if isinstance(data_str, str):
                import json
                data_str = json.loads(data_str)
            
            shapes = data_str.get("shape", [])
            
            # Parse 3D model data from shapes
            parser = Model3DParser(self.api)
            model_data = parser.parse_from_footprint(shapes)
            
            if not model_data:
                logging.warning("No 3D model available for this component")
                return True  # Not an error, just no model available
            
            # Export to KiCad format
            exporter = Model3DExporter(model_data, self.component_name)
            model_dir = f"{self.output_base}.3dshapes"
            
            success = exporter.export(model_dir, overwrite=self.overwrite)
            
            if success:
                logging.info(f"3D model exported to {model_dir}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error converting 3D model: {e}", exc_info=True)
            return False
