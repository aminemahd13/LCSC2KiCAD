"""
Symbol exporter for KiCad format (KiCad 6.0+)
"""

import logging
import os
from pathlib import Path
from typing import Dict, List


class SymbolExporter:
    """Export symbols to KiCad format"""
    
    def __init__(self, symbol_data: Dict, component_name: str, lcsc_id: str):
        """
        Initialize exporter
        
        Args:
            symbol_data: Parsed symbol data
            component_name: Component name
            lcsc_id: LCSC part number
        """
        self.symbol_data = symbol_data
        self.component_name = component_name
        self.lcsc_id = lcsc_id
        self.info = symbol_data.get("info", {})
    
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
            logging.info(f"Exporting symbol to {lib_path}")
            
            # Generate symbol data in KiCad format
            symbol_content = self._generate_kicad_symbol()
            
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
    
    def _generate_kicad_symbol(self) -> str:
        """Generate KiCad symbol format"""
        symbol_id = self.component_name.replace(" ", "_")
        
        # Generate properties
        properties = self._generate_properties()
        
        # Generate pins
        pins = self._generate_pins()
        
        # Generate graphics
        graphics = self._generate_graphics()
        
        symbol = f"""  (symbol "{symbol_id}"
    (in_bom yes)
    (on_board yes)
{properties}
    (symbol "{symbol_id}_0_1"
{graphics}
{pins}
    )
  )
"""
        return symbol
    
    def _generate_properties(self) -> str:
        """Generate symbol properties"""
        props = []
        
        # Reference
        prefix = self.info.get("prefix", "U")
        props.append(f'    (property "Reference" "{prefix}"')
        props.append('      (id 0)')
        props.append('      (at 0 5.08 0)')
        props.append('      (effects (font (size 1.27 1.27)))')
        props.append('    )')
        
        # Value
        props.append(f'    (property "Value" "{self.component_name}"')
        props.append('      (id 1)')
        props.append('      (at 0 -5.08 0)')
        props.append('      (effects (font (size 1.27 1.27)))')
        props.append('    )')
        
        # Footprint
        if self.info.get("package"):
            props.append(f'    (property "Footprint" "{self.info["package"]}"')
            props.append('      (id 2)')
            props.append('      (at 0 -7.62 0)')
            props.append('      (effects (font (size 1.27 1.27)) hide)')
            props.append('    )')
        
        # Datasheet
        if self.info.get("datasheet"):
            props.append(f'    (property "Datasheet" "{self.info["datasheet"]}"')
            props.append('      (id 3)')
            props.append('      (at 0 -10.16 0)')
            props.append('      (effects (font (size 1.27 1.27)) hide)')
            props.append('    )')
        
        # LCSC Part
        if self.lcsc_id:
            props.append(f'    (property "LCSC" "{self.lcsc_id}"')
            props.append('      (id 4)')
            props.append('      (at 0 -12.7 0)')
            props.append('      (effects (font (size 1.27 1.27)) hide)')
            props.append('    )')
        
        # Manufacturer
        if self.info.get("manufacturer"):
            props.append(f'    (property "Manufacturer" "{self.info["manufacturer"]}"')
            props.append('      (id 5)')
            props.append('      (at 0 -15.24 0)')
            props.append('      (effects (font (size 1.27 1.27)) hide)')
            props.append('    )')
        
        return "\n".join(props)
    
    def _generate_pins(self) -> str:
        """Generate pin definitions"""
        pins = []
        pin_data = self.symbol_data.get("pins", [])
        
        for i, pin in enumerate(pin_data):
            pin_num = pin.get("number", str(i + 1))
            pin_name = pin.get("name", f"Pin_{pin_num}")
            pin_type = self._map_pin_type(pin.get("type", "0"))
            
            # Calculate position (convert from EasyEDA units)
            x = (pin.get("pos_x", 0) - 100) * 0.0254
            y = -(pin.get("pos_y", 0) - 100) * 0.0254
            
            # Determine orientation
            rotation = pin.get("rotation", 0)
            if rotation == 0:
                angle = 0
            elif rotation == 90:
                angle = 270
            elif rotation == 180:
                angle = 180
            else:
                angle = 90
            
            pins.append(f'      (pin {pin_type} line')
            pins.append(f'        (at {x:.2f} {y:.2f} {angle})')
            pins.append(f'        (length 2.54)')
            pins.append(f'        (name "{pin_name}" (effects (font (size 1.27 1.27))))')
            pins.append(f'        (number "{pin_num}" (effects (font (size 1.27 1.27))))')
            pins.append(f'      )')
        
        return "\n".join(pins)
    
    def _generate_graphics(self) -> str:
        """Generate graphic elements"""
        graphics = []
        
        # Rectangle (body)
        rectangles = self.symbol_data.get("rectangles", [])
        for rect in rectangles:
            x = (rect.get("x", 0) - 100) * 0.0254
            y = -(rect.get("y", 0) - 100) * 0.0254
            w = rect.get("width", 100) * 0.0254
            h = rect.get("height", 100) * 0.0254
            
            graphics.append(f'      (rectangle')
            graphics.append(f'        (start {x:.2f} {y:.2f})')
            graphics.append(f'        (end {x+w:.2f} {y-h:.2f})')
            graphics.append(f'        (stroke (width 0.254) (type default) (color 0 0 0 0))')
            graphics.append(f'        (fill (type background))')
            graphics.append(f'      )')
        
        # Circles
        circles = self.symbol_data.get("circles", [])
        for circle in circles:
            cx = (circle.get("center_x", 0) - 100) * 0.0254
            cy = -(circle.get("center_y", 0) - 100) * 0.0254
            r = circle.get("radius", 50) * 0.0254
            
            graphics.append(f'      (circle')
            graphics.append(f'        (center {cx:.2f} {cy:.2f})')
            graphics.append(f'        (radius {r:.2f})')
            graphics.append(f'        (stroke (width 0.254) (type default) (color 0 0 0 0))')
            graphics.append(f'        (fill (type none))')
            graphics.append(f'      )')
        
        # Polylines
        polylines = self.symbol_data.get("polylines", [])
        for polyline in polylines:
            points = polyline.get("points", [])
            if len(points) < 2:
                continue
            
            graphics.append(f'      (polyline')
            graphics.append(f'        (pts')
            for px, py in points:
                x = (px - 100) * 0.0254
                y = -(py - 100) * 0.0254
                graphics.append(f'          (xy {x:.2f} {y:.2f})')
            graphics.append(f'        )')
            graphics.append(f'        (stroke (width 0.254) (type default) (color 0 0 0 0))')
            graphics.append(f'        (fill (type none))')
            graphics.append(f'      )')
        
        return "\n".join(graphics)
    
    def _map_pin_type(self, pin_type: str) -> str:
        """Map EasyEDA pin type to KiCad pin type"""
        type_map = {
            "0": "unspecified",
            "1": "input",
            "2": "output",
            "3": "bidirectional",
            "4": "power_in",
        }
        return type_map.get(str(pin_type), "passive")
    
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
