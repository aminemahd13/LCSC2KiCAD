"""
KiCad Symbol Exporter - Based on reference implementation
Converts EasyEDA symbol structures to KiCad format
"""

import logging
from typing import Callable, List, Union

from lcsc2kicad.easyeda.parameters_easyeda_symbol import *
from lcsc2kicad.kicad.parameters_kicad_symbol import *


# Pin type mapping
ee_pin_type_to_ki_pin_type = {
    EasyedaPinType.unspecified: KiPinType.unspecified,
    EasyedaPinType._input: KiPinType._input,
    EasyedaPinType.output: KiPinType.output,
    EasyedaPinType.bidirectional: KiPinType.bidirectional,
    EasyedaPinType.power: KiPinType.power_in,
}


def px_to_mm(dim: Union[int, float]) -> float:
    """Convert EasyEDA pixels to KiCad millimeters"""
    # EasyEDA: 10px = 1mil, 1mil = 0.0254mm
    return round(float(dim) * 10 * 0.0254, 2)


def convert_ee_pins(
    ee_pins: List[EeSymbolPin], ee_bbox: EeSymbolBbox, kicad_version: KicadVersion
) -> List[KiSymbolPin]:
    """
    Convert EasyEDA pins to KiCad pins
    
    Args:
        ee_pins: List of EasyEDA pins
        ee_bbox: Symbol bounding box for coordinate transformation
        kicad_version: Target KiCad version
        
    Returns:
        List of KiCad pins
    """
    to_ki: Callable = px_to_mm
    kicad_pins = []
    
    for ee_pin in ee_pins:
        try:
            # Extract pin length from path (e.g., "M0,0h-20" means 20 units left)
            pin_length = abs(int(float(ee_pin.pin_path.path.split("h")[-1])))
            
            ki_pin = KiSymbolPin(
                name=ee_pin.name.text.replace(" ", ""),
                number=ee_pin.settings.spice_pin_number.replace(" ", ""),
                style=KiPinStyle.line,
                length=to_ki(pin_length),
                type=ee_pin_type_to_ki_pin_type.get(
                    ee_pin.settings.type, KiPinType.passive
                ),
                orientation=ee_pin.settings.rotation,
                pos_x=to_ki(int(ee_pin.settings.pos_x) - int(ee_bbox.x)),
                pos_y=-to_ki(int(ee_pin.settings.pos_y) - int(ee_bbox.y)),
            )
            
            # Check for special pin styles
            if ee_pin.dot.is_displayed and ee_pin.clock.is_displayed:
                ki_pin.style = KiPinStyle.inverted_clock
            elif ee_pin.dot.is_displayed:
                ki_pin.style = KiPinStyle.inverted
            elif ee_pin.clock.is_displayed:
                ki_pin.style = KiPinStyle.clock
            
            kicad_pins.append(ki_pin)
        except Exception as e:
            logging.warning(f"Error converting pin: {e}")
    
    return kicad_pins


def convert_ee_rectangles(
    ee_rectangles: List[EeSymbolRectangle],
    ee_bbox: EeSymbolBbox,
    kicad_version: KicadVersion,
) -> List[KiSymbolRectangle]:
    """
    Convert EasyEDA rectangles to KiCad rectangles
    
    Args:
        ee_rectangles: List of EasyEDA rectangles
        ee_bbox: Symbol bounding box
        kicad_version: Target KiCad version
        
    Returns:
        List of KiCad rectangles
    """
    to_ki: Callable = px_to_mm
    kicad_rectangles = []
    
    for ee_rectangle in ee_rectangles:
        try:
            ki_rectangle = KiSymbolRectangle(
                pos_x0=to_ki(int(float(ee_rectangle.pos_x)) - int(ee_bbox.x)),
                pos_y0=-to_ki(int(float(ee_rectangle.pos_y)) - int(ee_bbox.y)),
            )
            ki_rectangle.pos_x1 = to_ki(int(float(ee_rectangle.width))) + ki_rectangle.pos_x0
            ki_rectangle.pos_y1 = -to_ki(int(float(ee_rectangle.height))) + ki_rectangle.pos_y0
            
            kicad_rectangles.append(ki_rectangle)
        except Exception as e:
            logging.warning(f"Error converting rectangle: {e}")
    
    return kicad_rectangles


def convert_ee_circles(
    ee_circles: List[EeSymbolCircle], ee_bbox: EeSymbolBbox, kicad_version: KicadVersion
) -> List[KiSymbolCircle]:
    """
    Convert EasyEDA circles to KiCad circles
    
    Args:
        ee_circles: List of EasyEDA circles
        ee_bbox: Symbol bounding box
        kicad_version: Target KiCad version
        
    Returns:
        List of KiCad circles
    """
    to_ki: Callable = px_to_mm
    kicad_circles = []
    
    for ee_circle in ee_circles:
        try:
            kicad_circles.append(
                KiSymbolCircle(
                    pos_x=to_ki(int(float(ee_circle.center_x)) - int(ee_bbox.x)),
                    pos_y=-to_ki(int(float(ee_circle.center_y)) - int(ee_bbox.y)),
                    radius=to_ki(float(ee_circle.radius)),
                    background_filling=ee_circle.fill_color,
                )
            )
        except Exception as e:
            logging.warning(f"Error converting circle: {e}")
    
    return kicad_circles


def convert_ee_ellipses(
    ee_ellipses: List[EeSymbolEllipse],
    ee_bbox: EeSymbolBbox,
    kicad_version: KicadVersion,
) -> List[KiSymbolCircle]:
    """
    Convert EasyEDA ellipses to KiCad circles (only if radius_x == radius_y)
    
    Args:
        ee_ellipses: List of EasyEDA ellipses
        ee_bbox: Symbol bounding box
        kicad_version: Target KiCad version
        
    Returns:
        List of KiCad circles (ellipses with equal radii)
    """
    to_ki: Callable = px_to_mm
    kicad_circles = []
    
    for ee_ellipse in ee_ellipses:
        try:
            if float(ee_ellipse.radius_x) == float(ee_ellipse.radius_y):
                kicad_circles.append(
                    KiSymbolCircle(
                        pos_x=to_ki(int(float(ee_ellipse.center_x)) - int(ee_bbox.x)),
                        pos_y=-to_ki(int(float(ee_ellipse.center_y)) - int(ee_bbox.y)),
                        radius=to_ki(float(ee_ellipse.radius_x)),
                        background_filling=ee_ellipse.fill_color,
                    )
                )
        except Exception as e:
            logging.warning(f"Error converting ellipse: {e}")
    
    return kicad_circles


def convert_ee_polylines(
    ee_polylines: List[Union[EeSymbolPolyline, EeSymbolPolygon]],
    ee_bbox: EeSymbolBbox,
    kicad_version: KicadVersion,
) -> List[KiSymbolPolygon]:
    """
    Convert EasyEDA polylines/polygons to KiCad polylines
    
    Args:
        ee_polylines: List of EasyEDA polylines or polygons
        ee_bbox: Symbol bounding box
        kicad_version: Target KiCad version
        
    Returns:
        List of KiCad polygons
    """
    to_ki: Callable = px_to_mm
    kicad_polygons = []
    
    for ee_polyline in ee_polylines:
        try:
            raw_pts = ee_polyline.points.split(" ")
            
            x_points = [
                to_ki(int(float(raw_pts[i])) - int(ee_bbox.x))
                for i in range(0, len(raw_pts), 2)
                if raw_pts[i]
            ]
            y_points = [
                -to_ki(int(float(raw_pts[i])) - int(ee_bbox.y))
                for i in range(1, len(raw_pts), 2)
                if raw_pts[i]
            ]
            
            if isinstance(ee_polyline, EeSymbolPolygon) or ee_polyline.fill_color:
                is_closed = True
            else:
                is_closed = False
            
            kicad_polygons.append(
                KiSymbolPolygon(
                    points=[[x_points[i], y_points[i]] for i in range(len(x_points))],
                    points_number=len(x_points),
                    is_closed=is_closed,
                )
            )
        except Exception as e:
            logging.warning(f"Error converting polyline: {e}")
    
    return kicad_polygons


def convert_ee_polygons(
    ee_polygons: List[EeSymbolPolygon],
    ee_bbox: EeSymbolBbox,
    kicad_version: KicadVersion,
) -> List[KiSymbolPolygon]:
    """Convert EasyEDA polygons (wrapper for convert_ee_polylines)"""
    return convert_ee_polylines(
        ee_polylines=ee_polygons, ee_bbox=ee_bbox, kicad_version=kicad_version
    )


def convert_to_kicad(ee_symbol: EeSymbol, kicad_version: KicadVersion) -> KiSymbol:
    """
    Convert complete EasyEDA symbol to KiCad symbol
    
    Args:
        ee_symbol: Parsed EasyEDA symbol
        kicad_version: Target KiCad version
        
    Returns:
        KiCad symbol structure
    """
    ki_info = KiSymbolInfo(
        name=ee_symbol.info.name,
        prefix=ee_symbol.info.prefix.replace("?", ""),
        package=ee_symbol.info.package,
        manufacturer=ee_symbol.info.manufacturer,
        datasheet=ee_symbol.info.datasheet,
        lcsc_id=ee_symbol.info.lcsc_id,
        jlc_id=ee_symbol.info.jlc_id,
    )
    
    kicad_symbol = KiSymbol(
        info=ki_info,
        pins=convert_ee_pins(
            ee_pins=ee_symbol.pins, ee_bbox=ee_symbol.bbox, kicad_version=kicad_version
        ),
        rectangles=convert_ee_rectangles(
            ee_rectangles=ee_symbol.rectangles,
            ee_bbox=ee_symbol.bbox,
            kicad_version=kicad_version,
        ),
        circles=convert_ee_circles(
            ee_circles=ee_symbol.circles,
            ee_bbox=ee_symbol.bbox,
            kicad_version=kicad_version,
        ),
    )
    
    # Add circles from ellipses
    kicad_symbol.circles += convert_ee_ellipses(
        ee_ellipses=ee_symbol.ellipses,
        ee_bbox=ee_symbol.bbox,
        kicad_version=kicad_version,
    )
    
    # Add polygons
    kicad_symbol.polygons += convert_ee_polylines(
        ee_polylines=ee_symbol.polylines,
        ee_bbox=ee_symbol.bbox,
        kicad_version=kicad_version,
    )
    kicad_symbol.polygons += convert_ee_polygons(
        ee_polygons=ee_symbol.polygons,
        ee_bbox=ee_symbol.bbox,
        kicad_version=kicad_version,
    )
    
    return kicad_symbol


def tune_footprint_ref_path(ki_symbol: KiSymbol, footprint_lib_name: str):
    """Add library name prefix to footprint reference"""
    if ki_symbol.info.package:
        ki_symbol.info.package = f"{footprint_lib_name}:{ki_symbol.info.package}"


class ExporterSymbolKicad:
    """Export EasyEDA symbol to KiCad format"""
    
    def __init__(self, symbol: EeSymbol, kicad_version: KicadVersion):
        """
        Initialize exporter
        
        Args:
            symbol: Parsed EasyEDA symbol
            kicad_version: Target KiCad version
        """
        self.input: EeSymbol = symbol
        self.version = kicad_version
        self.output = convert_to_kicad(ee_symbol=self.input, kicad_version=kicad_version)
    
    def export(self, footprint_lib_name: str) -> str:
        """
        Export symbol to KiCad format string
        
        Args:
            footprint_lib_name: Name of footprint library for reference
            
        Returns:
            KiCad symbol as formatted string
        """
        tune_footprint_ref_path(
            ki_symbol=self.output,
            footprint_lib_name=footprint_lib_name,
        )
        return self.output.export(kicad_version=self.version)
