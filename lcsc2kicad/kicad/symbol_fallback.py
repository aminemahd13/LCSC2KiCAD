"""
Fallback symbol generator for components without EasyEDA symbol data
Creates a simple generic symbol based on footprint information
"""

import logging
import math
from typing import Dict, List, Optional

from lcsc2kicad.kicad.parameters_kicad_symbol import (
    KiSymbol,
    KiSymbolInfo,
    KiSymbolPin,
    KiSymbolRectangle,
    KiPinType,
    KiPinStyle,
    KicadVersion,
)


def extract_pin_count_from_footprint(footprint_name: str) -> Optional[int]:
    """
    Extract pin count from footprint name
    
    Examples:
        "FBGA-256_L17.0-W17.0-R16-C16-P1.00-BL" -> 256
        "LQFN-56_L7.0-W7.0-P0.4-EP" -> 56
        "QFP-100" -> 100
        
    Args:
        footprint_name: Footprint name string
        
    Returns:
        Pin count or None if not found
    """
    import re
    
    # Try to find pattern like "FBGA-256", "LQFN-56", "QFP-100"
    match = re.search(r'-(\d+)(?:_|$)', footprint_name)
    if match:
        return int(match.group(1))
    
    # Try to find pin count in description
    match = re.search(r'(\d+)[-_]?(?:pin|Pin|PIN)', footprint_name)
    if match:
        return int(match.group(1))
    
    return None


def create_fallback_symbol(
    component_name: str,
    lcsc_id: str,
    package: str = "",
    manufacturer: str = "",
    datasheet: str = "",
    prefix: str = "U",
    pin_count: Optional[int] = None,
    pad_numbers: Optional[List[str]] = None,
) -> KiSymbol:
    """
    Create a generic fallback symbol for components without symbol data
    
    Creates a rectangular IC symbol with pins distributed on sides:
    - Top: VCC/VDD power pins
    - Bottom: GND pins  
    - Left/Right: I/O pins distributed evenly
    
    Args:
        component_name: Component name
        lcsc_id: LCSC part number
        package: Package/footprint name
        manufacturer: Manufacturer name
        datasheet: Datasheet URL
        prefix: Reference prefix (default: U)
        pin_count: Number of pins (extracted from package if not provided)
        pad_numbers: Actual pad numbers from footprint (e.g., ['A1', 'B1', 'J14'])
        
    Returns:
        KiSymbol structure with generic symbol
    """
    # Use pad_numbers if provided, otherwise generate sequential numbers
    if pad_numbers:
        pin_count = len(pad_numbers)
        logging.info(f"Creating fallback symbol for {component_name} with {pin_count} pins using footprint pad numbers")
    else:
        # Extract pin count from package name if not provided
        if pin_count is None and package:
            pin_count = extract_pin_count_from_footprint(package)
        
        if pin_count is None:
            logging.warning(f"Could not determine pin count for {component_name}, using 8 pins")
            pin_count = 8
        
        # Generate sequential pin numbers
        pad_numbers = [str(i + 1) for i in range(pin_count)]
        logging.info(f"Creating fallback symbol for {component_name} with {pin_count} sequential pins")
    
    # Create symbol info
    ki_info = KiSymbolInfo(
        name=component_name,
        prefix=prefix,
        package=package,
        manufacturer=manufacturer,
        datasheet=datasheet,
        lcsc_id=lcsc_id,
        jlc_id="",
    )
    
    # Calculate symbol dimensions based on pin count
    # More pins = larger rectangle
    pin_spacing = 2.54  # Standard 100mil spacing
    
    # Calculate how many pins will be on each side
    if pin_count <= 8:
        # Small DIP-style: pins on left and right only
        pins_per_vertical_side = (pin_count + 1) // 2
        pins_per_horizontal_side = 0
    else:
        # Large IC: distribute on all 4 sides
        pins_per_horizontal_side = max(2, int(pin_count * 0.1))
        pins_per_vertical_side = (pin_count - 2 * pins_per_horizontal_side) // 2
    
    # Calculate rectangle size based on actual pin distribution
    # Height needs to fit all vertical pins with good margins
    height = max(10.16, (pins_per_vertical_side) * pin_spacing + 10.16)
    
    # Width needs to fit all horizontal pins with good margins
    width = max(12.7, (pins_per_horizontal_side) * pin_spacing + 10.16)
    
    # For large ICs, ensure rectangle proportions match pin distribution
    # Don't force square - keep natural shape
    if pin_count > 50:
        # Only expand the smaller dimension slightly, maintain rectangular shape
        min_dim = max(height, width) * 0.5  # Minimum dimension is 50% of max
        height = max(height, min_dim)
        width = max(width, min_dim)
    
    # Create rectangle body
    rectangles = [
        KiSymbolRectangle(
            pos_x0=-width / 2,
            pos_y0=height / 2,
            pos_x1=width / 2,
            pos_y1=-height / 2,
        )
    ]
    
    # Create pins using actual pad numbers
    # Pin orientations point OUTWARD from the rectangle:
    # - Left side: orientation=180 (points left, away from rectangle)
    # - Right side: orientation=0 (points right, away from rectangle)
    # - Top side: orientation=90 (points up, away from rectangle)
    # - Bottom side: orientation=270 (points down, away from rectangle)
    pins = []
    pin_idx = 0  # Index into pad_numbers list
    
    if pin_count <= 8:
        # Small IC: Simple dual inline package (DIP style)
        pins_left = (pin_count + 1) // 2
        pins_right = pin_count - pins_left
        
        for i in range(pins_left):
            y_pos = height / 2 - (i + 1) * pin_spacing - 2.54
            pad_num = pad_numbers[pin_idx] if pin_idx < len(pad_numbers) else str(pin_idx + 1)
            pins.append(
                KiSymbolPin(
                    name=f"Pin_{pad_num}",
                    number=pad_num,  # Use actual pad number from footprint
                    type=KiPinType.passive,
                    style=KiPinStyle.line,
                    length=2.54,
                    orientation=180,  # Points LEFT (outward from left side)
                    pos_x=-width / 2 - 2.54,  # Position at left edge of rectangle
                    pos_y=y_pos,
                )
            )
            pin_idx += 1
        
        for i in range(pins_right):
            y_pos = height / 2 - (i + 1) * pin_spacing - 2.54
            pad_num = pad_numbers[pin_idx] if pin_idx < len(pad_numbers) else str(pin_idx + 1)
            pins.append(
                KiSymbolPin(
                    name=f"Pin_{pad_num}",
                    number=pad_num,  # Use actual pad number from footprint
                    type=KiPinType.passive,
                    style=KiPinStyle.line,
                    length=2.54,
                    orientation=0,  # Points RIGHT (outward from right side)
                    pos_x=width / 2 + 2.54,  # Position at right edge of rectangle
                    pos_y=y_pos,
                )
            )
            pin_idx += 1
    
    else:
        # Large IC: Distribute pins on all four sides
        # Allocate pins: 40% left/right, 10% top/bottom
        pins_horizontal = max(2, int(pin_count * 0.1))
        pins_vertical = (pin_count - 2 * pins_horizontal) // 2
        
        # Left side pins - distribute within rectangle height
        # Calculate span needed and ensure it fits within rectangle
        vertical_span = (pins_vertical - 1) * pin_spacing
        start_y = min(vertical_span / 2, height / 2 - 5.08)  # Keep margin from edges
        
        for i in range(pins_vertical):
            if pin_idx >= len(pad_numbers):
                break
            y_pos = start_y - i * pin_spacing
            pad_num = pad_numbers[pin_idx]
            pins.append(
                KiSymbolPin(
                    name=f"Pin_{pad_num}",
                    number=pad_num,  # Use actual pad number from footprint
                    type=KiPinType.passive,
                    style=KiPinStyle.line,
                    length=2.54,
                    orientation=180,  # Points LEFT (outward from left side)
                    pos_x=-width / 2 - 2.54,  # Position at left edge of rectangle
                    pos_y=y_pos,
                )
            )
            pin_idx += 1
        
        # Bottom pins - distribute within rectangle width
        horizontal_span = (pins_horizontal - 1) * pin_spacing
        x_start = -min(horizontal_span / 2, width / 2 - 5.08)  # Keep margin from edges
        
        for i in range(pins_horizontal):
            if pin_idx >= len(pad_numbers):
                break
            x_pos = x_start + i * pin_spacing
            pad_num = pad_numbers[pin_idx]
            pins.append(
                KiSymbolPin(
                    name=f"Pin_{pad_num}",
                    number=pad_num,  # Use actual pad number from footprint
                    type=KiPinType.passive,
                    style=KiPinStyle.line,
                    length=2.54,
                    orientation=270,  # Points DOWN (outward from bottom side)
                    pos_x=x_pos,
                    pos_y=-height / 2 - 2.54,  # Position at bottom edge of rectangle
                )
            )
            pin_idx += 1
        
        # Right side pins - start from top with proper margin
        for i in range(pins_vertical):
            if pin_idx >= len(pad_numbers):
                break
            y_pos = start_y - i * pin_spacing
            pad_num = pad_numbers[pin_idx]
            pins.append(
                KiSymbolPin(
                    name=f"Pin_{pad_num}",
                    number=pad_num,  # Use actual pad number from footprint
                    type=KiPinType.passive,
                    style=KiPinStyle.line,
                    length=2.54,
                    orientation=0,  # Points RIGHT (outward from right side)
                    pos_x=width / 2 + 2.54,  # Position at right edge of rectangle
                    pos_y=y_pos,
                )
            )
            pin_idx += 1
        
        # Top pins - distribute within rectangle width
        remaining_pins = pin_count - pin_idx
        if remaining_pins > 0:
            horizontal_span = (remaining_pins - 1) * pin_spacing
            x_start = -min(horizontal_span / 2, width / 2 - 5.08)  # Keep margin from edges
            
            for i in range(remaining_pins):
                if pin_idx >= len(pad_numbers):
                    break
                x_pos = x_start + i * pin_spacing
                pad_num = pad_numbers[pin_idx]
                pins.append(
                    KiSymbolPin(
                        name=f"Pin_{pad_num}",
                        number=pad_num,  # Use actual pad number from footprint
                        type=KiPinType.passive,
                        style=KiPinStyle.line,
                        length=2.54,
                        orientation=90,  # Points UP (outward from top side)
                        pos_x=x_pos,
                        pos_y=height / 2 - 2.54,  # Position at top edge of rectangle
                    )
                )
                pin_idx += 1
    
    # Create symbol
    ki_symbol = KiSymbol(
        info=ki_info,
        pins=pins,
        rectangles=rectangles,
        circles=[],
        polygons=[],
        arcs=[],
    )
    
    return ki_symbol


def extract_pad_numbers_from_footprint(cad_data: Dict) -> List[str]:
    """
    Extract pad numbers from footprint data
    
    Args:
        cad_data: Component CAD data from API
        
    Returns:
        List of pad numbers (e.g., ['A1', 'A2', 'B1', ...] or ['1', '2', '3', ...])
    """
    pad_numbers = []
    
    try:
        # Get footprint data
        package_detail = cad_data.get("packageDetail", {})
        if not package_detail:
            return pad_numbers
        
        data_str = package_detail.get("dataStr", {})
        if isinstance(data_str, str):
            import json
            data_str = json.loads(data_str)
        
        shapes = data_str.get("shape", [])
        if not isinstance(shapes, list):
            return pad_numbers
        
        # Parse each shape looking for PAD entries
        for shape in shapes:
            if not isinstance(shape, str):
                continue
            
            parts = shape.split("~")
            if len(parts) > 0 and parts[0] == "PAD":
                # PAD format: PAD~shape~x~y~width~height~layer~net~number~...
                if len(parts) > 8:
                    pad_num = parts[8]
                    if pad_num:  # Skip empty pad numbers
                        pad_numbers.append(pad_num)
        
        logging.info(f"Extracted {len(pad_numbers)} pad numbers from footprint")
        if pad_numbers:
            logging.debug(f"First few pads: {pad_numbers[:10]}")
            
    except Exception as e:
        logging.warning(f"Error extracting pad numbers from footprint: {e}")
    
    return pad_numbers


def create_fallback_symbol_from_cad_data(cad_data: Dict, component_name: str, lcsc_id: str) -> KiSymbol:
    """
    Create fallback symbol from CAD data dictionary
    
    Args:
        cad_data: Component CAD data from API
        component_name: Component name
        lcsc_id: LCSC part number
        
    Returns:
        KiSymbol with fallback representation
    """
    # Extract metadata
    data_str = cad_data.get("dataStr", {})
    if isinstance(data_str, str):
        import json
        data_str = json.loads(data_str)
    
    head = data_str.get("head", {})
    c_para = head.get("c_para", {})
    
    package = c_para.get("package", "")
    manufacturer = c_para.get("BOM_Manufacturer", "")
    datasheet = cad_data.get("datasheet", "")
    prefix = c_para.get("pre", "U")
    
    # Extract actual pad numbers from footprint
    pad_numbers = extract_pad_numbers_from_footprint(cad_data)
    
    return create_fallback_symbol(
        component_name=component_name,
        lcsc_id=lcsc_id,
        package=package,
        manufacturer=manufacturer,
        datasheet=datasheet,
        prefix=prefix,
        pin_count=len(pad_numbers) if pad_numbers else None,
        pad_numbers=pad_numbers if pad_numbers else None,
    )
