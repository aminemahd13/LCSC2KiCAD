"""
Footprint exporter for KiCad format
"""

import logging
import os
from pathlib import Path
from typing import Dict

from lcsc2kicad.utils import convert_to_mm


class FootprintExporter:
    """Export footprints to KiCad format"""
    
    def __init__(self, footprint_data: Dict, component_name: str):
        """
        Initialize exporter
        
        Args:
            footprint_data: Parsed footprint data
            component_name: Component name
        """
        self.footprint_data = footprint_data
        self.component_name = component_name
        self.info = footprint_data.get("info", {})
    
    def export(self, footprint_dir: str, overwrite: bool = False) -> bool:
        """
        Export footprint to KiCad library
        
        Args:
            footprint_dir: Path to .pretty directory
            overwrite: Whether to overwrite existing footprint
            
        Returns:
            True if successful
        """
        try:
            logging.info(f"Exporting footprint to {footprint_dir}")
            
            # Create directory if needed
            Path(footprint_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate footprint filename
            footprint_name = self.info.get("name", self.component_name)
            footprint_name = footprint_name.replace(" ", "_")
            footprint_file = os.path.join(footprint_dir, f"{footprint_name}.kicad_mod")
            
            # Check if exists
            if os.path.exists(footprint_file) and not overwrite:
                logging.warning(f"Footprint {footprint_name} already exists, skipping")
                return True
            
            # Generate footprint content
            footprint_content = self._generate_kicad_footprint()
            
            # Write to file
            with open(footprint_file, "w", encoding="utf-8") as f:
                f.write(footprint_content)
            
            logging.info(f"Successfully exported footprint {footprint_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting footprint: {e}", exc_info=True)
            return False
    
    def _generate_kicad_footprint(self) -> str:
        """Generate KiCad footprint format"""
        footprint_name = self.info.get("name", self.component_name).replace(" ", "_")
        is_smd = self.info.get("is_smd", False)
        
        fp_type = "smd" if is_smd else "through_hole"
        
        lines = []
        lines.append(f'(footprint "{footprint_name}"')
        lines.append(f'  (version 20211014)')
        lines.append(f'  (generator lcsc2kicad)')
        lines.append(f'  (layer "F.Cu")')
        lines.append(f'  (attr {fp_type})')
        
        # Reference text
        lines.append(f'  (fp_text reference "REF**" (at 0 -3) (layer "F.SilkS")')
        lines.append(f'    (effects (font (size 1 1) (thickness 0.15)))')
        lines.append(f'  )')
        
        # Value text
        lines.append(f'  (fp_text value "{footprint_name}" (at 0 3) (layer "F.Fab")')
        lines.append(f'    (effects (font (size 1 1) (thickness 0.15)))')
        lines.append(f'  )')
        
        # Pads
        pads = self._generate_pads()
        lines.extend(pads)
        
        # Graphics (lines, circles, etc.)
        graphics = self._generate_graphics()
        lines.extend(graphics)
        
        # 3D Model reference (if available)
        model_3d = self.footprint_data.get("model_3d")
        if model_3d:
            model_ref = self._generate_3d_model_ref(model_3d)
            if model_ref:
                lines.append(model_ref)
        
        lines.append(')')
        
        return '\n'.join(lines) + '\n'
    
    def _generate_pads(self) -> list:
        """Generate pad definitions"""
        lines = []
        pads = self.footprint_data.get("pads", [])
        
        # Get bounding box origin for coordinate transformation
        bbox_x = convert_to_mm(self.info.get("bbox_x", 0))
        bbox_y = convert_to_mm(self.info.get("bbox_y", 0))
        
        for pad in pads:
            pad_num = pad.get("number", "1")
            shape_type = pad.get("shape", "RECT")
            shape = self._map_pad_shape(shape_type)
            
            # Apply bbox offset to center footprint at origin
            x = pad.get("center_x", 0) - bbox_x
            y = pad.get("center_y", 0) - bbox_y
            width = pad.get("width", 1.0)
            height = pad.get("height", 1.0)
            rotation = pad.get("rotation", 0)
            hole_radius = pad.get("hole_radius", 0)
            points = pad.get("points", "")
            
            # Determine pad type
            if hole_radius > 0:
                pad_type = "thru_hole"
                drill_size = hole_radius * 2
                drill_str = f' (drill {drill_size:.3f})'
            else:
                pad_type = "smd"
                drill_str = ""
            
            # Determine layers
            layer_id = pad.get("layer_id", 1)
            layers = self._map_pad_layers(layer_id, pad_type)
            
            # Handle custom polygon pads
            is_custom = shape == "custom" and points
            if is_custom:
                # For custom pads, use minimal base pad size
                width = 0.005
                height = 0.005
                rotation = 0  # Polygon points are absolute
                
                # Parse polygon points and apply bbox offset
                try:
                    point_list = [float(p) for p in points.split()]
                    if len(point_list) >= 4:  # Need at least 2 points (x,y pairs)
                        # Convert points to mm and apply bbox offset
                        polygon_points = []
                        for i in range(0, len(point_list), 2):
                            px = convert_to_mm(point_list[i]) - bbox_x - x
                            py = convert_to_mm(point_list[i + 1]) - bbox_y - y
                            polygon_points.append(f"(xy {px:.3f} {py:.3f})")
                        
                        polygon_str = f'\n    (zone_connect 2)\n    (options (clearance outline) (anchor rect))\n    (primitives\n      (gr_poly\n        (pts\n          {" ".join(polygon_points)}\n        )\n        (width 0.1)\n      )\n    )'
                    else:
                        is_custom = False
                        polygon_str = ""
                except:
                    is_custom = False
                    polygon_str = ""
            else:
                polygon_str = ""
            
            lines.append(f'  (pad "{pad_num}" {pad_type} {shape}')
            lines.append(f'    (at {x:.3f} {y:.3f} {rotation:.1f})')
            lines.append(f'    (size {width:.3f} {height:.3f})')
            lines.append(f'    (layers {layers}){drill_str}{polygon_str}')
            lines.append(f'  )')
        
        return lines
    
    def _generate_graphics(self) -> list:
        """Generate graphic elements"""
        lines = []
        
        # Get bounding box origin for coordinate transformation
        bbox_x = convert_to_mm(self.info.get("bbox_x", 0))
        bbox_y = convert_to_mm(self.info.get("bbox_y", 0))
        
        # Lines (tracks)
        tracks = self.footprint_data.get("tracks", [])
        for track in tracks:
            # Apply bbox offset to center footprint at origin
            start_x = track.get("start_x", 0) - bbox_x
            start_y = track.get("start_y", 0) - bbox_y
            end_x = track.get("end_x", 0) - bbox_x
            end_y = track.get("end_y", 0) - bbox_y
            width = track.get("width", 0.15)
            layer_id = track.get("layer_id", 3)
            layer = self._map_layer(layer_id)
            
            lines.append(f'  (fp_line')
            lines.append(f'    (start {start_x:.3f} {start_y:.3f})')
            lines.append(f'    (end {end_x:.3f} {end_y:.3f})')
            lines.append(f'    (stroke (width {width:.3f}) (type solid))')
            lines.append(f'    (layer "{layer}")')
            lines.append(f'  )')
        
        # Circles
        circles = self.footprint_data.get("circles", [])
        for circle in circles:
            # Apply bbox offset to center footprint at origin
            cx = circle.get("center_x", 0) - bbox_x
            cy = circle.get("center_y", 0) - bbox_y
            radius = circle.get("radius", 1.0)
            width = circle.get("width", 0.15)
            layer_id = circle.get("layer_id", 3)
            layer = self._map_layer(layer_id)
            
            lines.append(f'  (fp_circle')
            lines.append(f'    (center {cx:.3f} {cy:.3f})')
            lines.append(f'    (end {cx+radius:.3f} {cy:.3f})')
            lines.append(f'    (stroke (width {width:.3f}) (type solid))')
            lines.append(f'    (fill none)')
            lines.append(f'    (layer "{layer}")')
            lines.append(f'  )')
        
        # Texts
        texts = self.footprint_data.get("texts", [])
        for text in texts:
            text_str = text.get("text", "")
            # Apply bbox offset to center footprint at origin
            x = text.get("x", 0) - bbox_x
            y = text.get("y", 0) - bbox_y
            size = text.get("size", 1.0)
            layer_id = text.get("layer_id", 3)
            layer = self._map_layer(layer_id)
            rotation = text.get("rotation", 0)
            
            lines.append(f'  (fp_text user "{text_str}"')
            lines.append(f'    (at {x:.3f} {y:.3f} {rotation:.1f})')
            lines.append(f'    (layer "{layer}")')
            lines.append(f'    (effects (font (size {size:.3f} {size:.3f}) (thickness {size*0.15:.3f})))')
            lines.append(f'  )')
        
        return lines
    
    def _map_pad_shape(self, shape: str) -> str:
        """Map EasyEDA pad shape to KiCad"""
        shape_map = {
            "RECT": "rect",
            "ELLIPSE": "circle",
            "OVAL": "oval",
            "POLYGON": "custom",
        }
        return shape_map.get(shape, "rect")
    
    def _map_pad_layers(self, layer_id: int, pad_type: str) -> str:
        """Map layer ID to KiCad layers"""
        if pad_type == "thru_hole":
            return '"*.Cu" "*.Mask"'
        else:
            # SMD pads
            if layer_id == 1:
                return '"F.Cu" "F.Paste" "F.Mask"'
            elif layer_id == 2:
                return '"B.Cu" "B.Paste" "B.Mask"'
            else:
                return '"F.Cu" "F.Paste" "F.Mask"'
    
    def _map_layer(self, layer_id: int) -> str:
        """Map EasyEDA layer ID to KiCad layer"""
        layer_map = {
            1: "F.Cu",
            2: "B.Cu",
            3: "F.SilkS",
            4: "B.SilkS",
            5: "F.Paste",
            6: "B.Paste",
            7: "F.Mask",
            8: "B.Mask",
            10: "Edge.Cuts",
            11: "Edge.Cuts",
            12: "Cmts.User",
            13: "F.Fab",
            14: "B.Fab",
            15: "Dwgs.User",
        }
        return layer_map.get(layer_id, "F.SilkS")
    
    def _generate_3d_model_ref(self, model_3d: Dict) -> str:
        """Generate 3D model reference"""
        try:
            path = model_3d.get("path", "")
            name = model_3d.get("name", "model")
            transform = model_3d.get("transform", {})
            
            # Get bounding box origin for coordinate transformation
            bbox_x = self.info.get("bbox_x", 0)
            bbox_y = self.info.get("bbox_y", 0)
            
            # Extract transformation data
            translation = transform.get("translation", {"x": 0, "y": 0, "z": 0})
            rotation = transform.get("rotation", {"x": 0, "y": 0, "z": 0})
            scale = transform.get("scale", {"x": 1, "y": 1, "z": 1})
            
            # Apply bbox offset and convert to mm (EasyEDA uses mil)
            tx = (translation.get("x", 0) - bbox_x) * 0.254  # mil to mm
            ty = -(translation.get("y", 0) - bbox_y) * 0.254  # Invert Y
            tz = -translation.get("z", 0) * 0.254  # Invert Z
            
            # Rotation conversion (360 - angle for proper orientation)
            rx = (360 - rotation.get("x", 0)) % 360
            ry = (360 - rotation.get("y", 0)) % 360
            rz = (360 - rotation.get("z", 0)) % 360
            
            sx = scale.get("x", 1)
            sy = scale.get("y", 1)
            sz = scale.get("z", 1)
            
            lines = []
            lines.append(f'  (model "{path}/{name}.wrl"')
            lines.append(f'    (offset (xyz {tx:.4f} {ty:.4f} {tz:.4f}))')
            lines.append(f'    (scale (xyz {sx:.4f} {sy:.4f} {sz:.4f}))')
            lines.append(f'    (rotate (xyz {rx:.4f} {ry:.4f} {rz:.4f}))')
            lines.append(f'  )')
            
            return '\n'.join(lines)
            
        except Exception as e:
            logging.error(f"Error generating 3D model reference: {e}")
            return ""
