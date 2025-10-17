"""
Symbol parser for converting EasyEDA symbol data to internal format
"""

import logging
import json
from typing import Dict, List, Optional, Any

from lcsc2kicad.utils import convert_to_mm


class SymbolParser:
    """Parse EasyEDA symbol data"""
    
    def __init__(self, cad_data: Dict):
        """
        Initialize parser
        
        Args:
            cad_data: Component CAD data from API
        """
        self.cad_data = cad_data
        self.symbol_data = None
    
    def parse(self) -> Optional[Dict]:
        """
        Parse symbol data from EasyEDA format
        
        Returns:
            Parsed symbol data or None if failed
        """
        try:
            if "dataStr" not in self.cad_data:
                logging.error("No dataStr in CAD data")
                return None
            
            data_str = self.cad_data["dataStr"]
            
            # Handle both dict and string formats
            if isinstance(data_str, str):
                try:
                    data_str = json.loads(data_str)
                except json.JSONDecodeError:
                    logging.error("Failed to parse dataStr as JSON")
                    return None
            
            if "head" not in data_str:
                logging.error("No head in symbol data")
                return None
            
            head = data_str["head"]
            c_para = head.get("c_para", {})
            
            # Extract component info
            symbol_info = {
                "name": c_para.get("name", self.cad_data.get("title", "Unknown")),
                "prefix": c_para.get("pre", "U"),
                "package": c_para.get("package", ""),
                "manufacturer": self.cad_data.get("manufacturer", ""),
                "datasheet": self.cad_data.get("datasheet", ""),
                "lcsc_id": self.cad_data.get("lcsc", ""),
                "description": self.cad_data.get("description", ""),
            }
            
            # Parse shape data
            shapes = data_str.get("shape", [])
            
            pins = []
            rectangles = []
            circles = []
            polylines = []
            texts = []
            
            for shape in shapes:
                if not isinstance(shape, str):
                    continue
                
                parts = shape.split("~")
                if not parts:
                    continue
                
                shape_type = parts[0]
                
                try:
                    if shape_type == "P":  # Pin
                        pin = self._parse_pin(parts)
                        if pin:
                            pins.append(pin)
                    elif shape_type == "R":  # Rectangle
                        rect = self._parse_rectangle(parts)
                        if rect:
                            rectangles.append(rect)
                    elif shape_type == "C":  # Circle
                        circle = self._parse_circle(parts)
                        if circle:
                            circles.append(circle)
                    elif shape_type == "PL":  # Polyline
                        polyline = self._parse_polyline(parts)
                        if polyline:
                            polylines.append(polyline)
                    elif shape_type == "T":  # Text
                        text = self._parse_text(parts)
                        if text:
                            texts.append(text)
                except Exception as e:
                    logging.warning(f"Failed to parse shape {shape_type}: {e}")
                    continue
            
            return {
                "info": symbol_info,
                "pins": pins,
                "rectangles": rectangles,
                "circles": circles,
                "polylines": polylines,
                "texts": texts,
            }
            
        except Exception as e:
            logging.error(f"Error parsing symbol: {e}", exc_info=True)
            return None
    
    def _parse_pin(self, parts: List[str]) -> Optional[Dict]:
        """Parse pin data"""
        try:
            if len(parts) < 10:
                return None
            
            # Pin format: P~show/hide~type~x~y~rotation~number~...
            pin_data = {
                "is_displayed": parts[1] == "show" if len(parts) > 1 else True,
                "type": parts[2] if len(parts) > 2 else "0",
                "pos_x": float(parts[4]) if len(parts) > 4 else 0,
                "pos_y": float(parts[5]) if len(parts) > 5 else 0,
                "rotation": int(float(parts[6])) if len(parts) > 6 else 0,
                "number": parts[7] if len(parts) > 7 else "1",
                "name": parts[8] if len(parts) > 8 else "",
            }
            
            return pin_data
            
        except Exception as e:
            logging.warning(f"Error parsing pin: {e}")
            return None
    
    def _parse_rectangle(self, parts: List[str]) -> Optional[Dict]:
        """Parse rectangle data"""
        try:
            if len(parts) < 6:
                return None
            
            return {
                "x": float(parts[1]),
                "y": float(parts[2]),
                "width": float(parts[3]),
                "height": float(parts[4]),
                "stroke_width": float(parts[5]) if len(parts) > 5 else 1.0,
            }
            
        except Exception as e:
            logging.warning(f"Error parsing rectangle: {e}")
            return None
    
    def _parse_circle(self, parts: List[str]) -> Optional[Dict]:
        """Parse circle data"""
        try:
            if len(parts) < 4:
                return None
            
            return {
                "center_x": float(parts[1]),
                "center_y": float(parts[2]),
                "radius": float(parts[3]),
                "stroke_width": float(parts[4]) if len(parts) > 4 else 1.0,
            }
            
        except Exception as e:
            logging.warning(f"Error parsing circle: {e}")
            return None
    
    def _parse_polyline(self, parts: List[str]) -> Optional[Dict]:
        """Parse polyline data"""
        try:
            if len(parts) < 3:
                return None
            
            # Parse points
            points_str = parts[1]
            points = []
            
            coords = points_str.split()
            for i in range(0, len(coords) - 1, 2):
                try:
                    points.append((float(coords[i]), float(coords[i + 1])))
                except (ValueError, IndexError):
                    continue
            
            return {
                "points": points,
                "stroke_width": float(parts[2]) if len(parts) > 2 else 1.0,
            }
            
        except Exception as e:
            logging.warning(f"Error parsing polyline: {e}")
            return None
    
    def _parse_text(self, parts: List[str]) -> Optional[Dict]:
        """Parse text data"""
        try:
            if len(parts) < 5:
                return None
            
            return {
                "text": parts[1],
                "x": float(parts[2]),
                "y": float(parts[3]),
                "rotation": int(float(parts[4])) if len(parts) > 4 else 0,
                "size": float(parts[5]) if len(parts) > 5 else 1.0,
            }
            
        except Exception as e:
            logging.warning(f"Error parsing text: {e}")
            return None
