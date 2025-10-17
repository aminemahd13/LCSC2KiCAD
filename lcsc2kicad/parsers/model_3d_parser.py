"""
3D Model parser for converting EasyEDA 3D model data
"""

import logging
import json
from typing import Dict, Optional, List

from lcsc2kicad.api import LCSCApi


class Model3DParser:
    """Parse EasyEDA 3D model data"""
    
    def __init__(self, api: LCSCApi):
        """
        Initialize parser
        
        Args:
            api: API client for downloading models
        """
        self.api = api
    
    def parse_from_footprint(self, shape_data: List[str]) -> Optional[Dict]:
        """
        Parse 3D model data from footprint shape data
        
        Args:
            shape_data: List of shape strings from packageDetail.dataStr.shape
            
        Returns:
            Parsed model data or None if no model available
        """
        try:
            # Look for SVGNODE which contains 3D model reference
            model_info = None
            for line in shape_data:
                if line.startswith("SVGNODE~"):
                    # Extract JSON from SVGNODE
                    parts = line.split("~")
                    if len(parts) >= 2:
                        try:
                            svg_data = json.loads(parts[1])
                            if "attrs" in svg_data:
                                model_info = svg_data["attrs"]
                                break
                        except json.JSONDecodeError as e:
                            logging.warning(f"Failed to parse SVGNODE JSON: {e}")
                            continue
            
            if not model_info:
                logging.info("No SVGNODE with 3D model found in footprint")
                return None
            
            # Extract UUID and other info
            uuid = model_info.get("uuid", "")
            title = model_info.get("title", "model")
            
            if not uuid:
                logging.info("No UUID found in 3D model info")
                return None
            
            logging.info(f"Found 3D model UUID: {uuid}, title: {title}")
            
            # Download model files
            model_obj = self.api.get_3d_model_obj(uuid)
            model_step = self.api.get_3d_model_step(uuid)
            
            if not model_obj and not model_step:
                logging.warning("Failed to download 3D model files")
                return None
            
            # Parse transformation data
            c_origin = model_info.get("c_origin", "0,0").split(",")
            c_rotation = model_info.get("c_rotation", "0,0,0").split(",")
            z_value = float(model_info.get("z", 0))
            
            transform = {
                "rotation": {
                    "x": float(c_rotation[0]) if len(c_rotation) > 0 else 0,
                    "y": float(c_rotation[1]) if len(c_rotation) > 1 else 0,
                    "z": float(c_rotation[2]) if len(c_rotation) > 2 else 0,
                },
                "translation": {
                    "x": float(c_origin[0]) if len(c_origin) > 0 else 0,
                    "y": float(c_origin[1]) if len(c_origin) > 1 else 0,
                    "z": z_value,
                },
                "scale": {"x": 1, "y": 1, "z": 1},
            }
            
            return {
                "uuid": uuid,
                "title": title,
                "obj_data": model_obj,
                "step_data": model_step,
                "transform": transform,
            }
            
        except Exception as e:
            logging.error(f"Error parsing 3D model: {e}", exc_info=True)
            return None
