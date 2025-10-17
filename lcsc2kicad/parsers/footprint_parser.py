"""
Footprint parser for converting EasyEDA footprint data to internal format
"""

import logging
import json
from typing import Dict, List, Optional

from lcsc2kicad.utils import convert_to_mm


class FootprintParser:
    """Parse EasyEDA footprint data"""
    
    def __init__(self, cad_data: Dict):
        """
        Initialize parser
        
        Args:
            cad_data: Component CAD data from API
        """
        self.cad_data = cad_data
    
    def parse(self) -> Optional[Dict]:
        """
        Parse footprint data from EasyEDA format
        
        Returns:
            Parsed footprint data or None if failed
        """
        try:
            if "packageDetail" not in self.cad_data:
                logging.error("No packageDetail in CAD data")
                return None
            
            package_detail = self.cad_data["packageDetail"]
            
            if "dataStr" not in package_detail:
                logging.error("No dataStr in packageDetail")
                return None
            
            data_str = package_detail["dataStr"]
            
            # Handle both dict and string formats
            if isinstance(data_str, str):
                try:
                    data_str = json.loads(data_str)
                except json.JSONDecodeError:
                    logging.error("Failed to parse dataStr as JSON")
                    return None
            
            # Extract footprint info
            head = data_str.get("head", {})
            c_para = head.get("c_para", {})
            
            # Extract bounding box origin (critical for coordinate transformation!)
            bbox_x = float(head.get("x", 0))
            bbox_y = float(head.get("y", 0))
            
            footprint_info = {
                "name": package_detail.get("title", "Unknown_Footprint"),
                "description": package_detail.get("description", ""),
                "is_smd": self.cad_data.get("SMT", False),
                "bbox_x": bbox_x,
                "bbox_y": bbox_y,
            }
            
            # Parse shapes
            shapes = data_str.get("shape", [])
            
            pads = []
            tracks = []
            circles = []
            texts = []
            holes = []
            
            for shape in shapes:
                if not isinstance(shape, str):
                    continue
                
                parts = shape.split("~")
                if not parts:
                    continue
                
                shape_type = parts[0]
                
                try:
                    if shape_type == "PAD":
                        pad = self._parse_pad(parts)
                        if pad:
                            pads.append(pad)
                    elif shape_type == "TRACK":
                        track = self._parse_track(parts)
                        if track:
                            tracks.append(track)
                    elif shape_type == "CIRCLE":
                        circle = self._parse_circle(parts)
                        if circle:
                            circles.append(circle)
                    elif shape_type == "TEXT":
                        text = self._parse_text(parts)
                        if text:
                            texts.append(text)
                    elif shape_type == "HOLE":
                        hole = self._parse_hole(parts)
                        if hole:
                            holes.append(hole)
                except Exception as e:
                    logging.warning(f"Failed to parse footprint shape {shape_type}: {e}")
                    continue
            
            return {
                "info": footprint_info,
                "pads": pads,
                "tracks": tracks,
                "circles": circles,
                "texts": texts,
                "holes": holes,
                "shapes": shapes,  # Keep raw shapes for 3D model parsing
            }
            
        except Exception as e:
            logging.error(f"Error parsing footprint: {e}", exc_info=True)
            return None
    
    def _parse_pad(self, parts: List[str]) -> Optional[Dict]:
        """Parse pad data"""
        try:
            if len(parts) < 10:
                return None
            
            # PAD format: PAD~shape~x~y~width~height~layer~net~number~hole_radius~points~rotation~...
            # For polygon pads, parts[10] contains the polygon points string
            pad_data = {
                "shape": parts[1] if len(parts) > 1 else "RECT",
                "center_x": convert_to_mm(float(parts[2])) if len(parts) > 2 else 0,
                "center_y": convert_to_mm(float(parts[3])) if len(parts) > 3 else 0,
                "width": convert_to_mm(float(parts[4])) if len(parts) > 4 else 1.0,
                "height": convert_to_mm(float(parts[5])) if len(parts) > 5 else 1.0,
                "layer_id": int(parts[6]) if len(parts) > 6 else 1,
                "net": parts[7] if len(parts) > 7 else "",
                "number": parts[8] if len(parts) > 8 else "1",
                "hole_radius": convert_to_mm(float(parts[9])) if len(parts) > 9 else 0,
                "points": parts[10] if len(parts) > 10 else "",  # Polygon points for custom shapes
                "rotation": float(parts[11]) if len(parts) > 11 else 0,
            }
            
            return pad_data
            
        except Exception as e:
            logging.warning(f"Error parsing pad: {e}")
            return None
    
    def _parse_track(self, parts: List[str]) -> Optional[Dict]:
        """Parse track (line) data"""
        try:
            if len(parts) < 6:
                return None
            
            return {
                "start_x": convert_to_mm(float(parts[1])),
                "start_y": convert_to_mm(float(parts[2])),
                "end_x": convert_to_mm(float(parts[3])),
                "end_y": convert_to_mm(float(parts[4])),
                "width": convert_to_mm(float(parts[5])),
                "layer_id": int(parts[6]) if len(parts) > 6 else 3,
            }
            
        except Exception as e:
            logging.warning(f"Error parsing track: {e}")
            return None
    
    def _parse_circle(self, parts: List[str]) -> Optional[Dict]:
        """Parse circle data"""
        try:
            if len(parts) < 5:
                return None
            
            return {
                "center_x": convert_to_mm(float(parts[1])),
                "center_y": convert_to_mm(float(parts[2])),
                "radius": convert_to_mm(float(parts[3])),
                "width": convert_to_mm(float(parts[4])),
                "layer_id": int(parts[5]) if len(parts) > 5 else 3,
            }
            
        except Exception as e:
            logging.warning(f"Error parsing circle: {e}")
            return None
    
    def _parse_text(self, parts: List[str]) -> Optional[Dict]:
        """Parse text data"""
        try:
            if len(parts) < 5:
                return None
            
            return {
                "text": parts[1],
                "x": convert_to_mm(float(parts[2])),
                "y": convert_to_mm(float(parts[3])),
                "size": convert_to_mm(float(parts[4])),
                "layer_id": int(parts[5]) if len(parts) > 5 else 3,
                "rotation": float(parts[6]) if len(parts) > 6 else 0,
            }
            
        except Exception as e:
            logging.warning(f"Error parsing text: {e}")
            return None
    
    def _parse_hole(self, parts: List[str]) -> Optional[Dict]:
        """Parse hole data"""
        try:
            if len(parts) < 4:
                return None
            
            return {
                "x": convert_to_mm(float(parts[1])),
                "y": convert_to_mm(float(parts[2])),
                "diameter": convert_to_mm(float(parts[3])),
            }
            
        except Exception as e:
            logging.warning(f"Error parsing hole: {e}")
            return None
