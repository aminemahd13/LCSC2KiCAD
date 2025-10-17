"""
EasyEDA Symbol Importer - Based on reference implementation
Parses EasyEDA JSON symbol data into structured format
"""

import logging
from typing import Dict
from lcsc2kicad.easyeda.parameters_easyeda_symbol import *


def add_easyeda_pin(pin_data: str, ee_symbol: EeSymbol):
    """Parse pin data with ^^ delimited segments"""
    try:
        segments = pin_data.split("^^")
        if len(segments) < 7:
            logging.warning(f"Pin data has insufficient segments: {len(segments)}")
            return
        
        ee_segments = [seg.split("~") for seg in segments]
        
        # Segment 0: Pin settings
        pin_settings = EeSymbolPinSettings(
            **dict(zip(EeSymbolPinSettings.model_fields.keys(), ee_segments[0][1:]))
        )
        
        # Segment 1: Pin dot (start position)
        pin_dot = EeSymbolPinDot(
            dot_x=float(ee_segments[1][0]) if ee_segments[1][0] else 0,
            dot_y=float(ee_segments[1][1]) if len(ee_segments[1]) > 1 and ee_segments[1][1] else 0
        )
        
        # Segment 2: Pin path
        pin_path = EeSymbolPinPath(
            path=ee_segments[2][0] if ee_segments[2] else "",
            color=ee_segments[2][1] if len(ee_segments[2]) > 1 else "#000000"
        )
        
        # Segment 3: Pin name
        pin_name = EeSymbolPinName(
            **dict(zip(EeSymbolPinName.model_fields.keys(), ee_segments[3][:]))
        )
        
        # Segment 5: Inversion dot
        pin_dot_bis = EeSymbolPinDotBis(
            is_displayed=ee_segments[5][0] if len(ee_segments) > 5 and ee_segments[5] else "hide",
            circle_x=float(ee_segments[5][1]) if len(ee_segments) > 5 and len(ee_segments[5]) > 1 and ee_segments[5][1] else 0,
            circle_y=float(ee_segments[5][2]) if len(ee_segments) > 5 and len(ee_segments[5]) > 2 and ee_segments[5][2] else 0,
        )
        
        # Segment 6: Clock indicator
        pin_clock = EeSymbolPinClock(
            is_displayed=ee_segments[6][0] if len(ee_segments) > 6 and ee_segments[6] else "hide",
            path=ee_segments[6][1] if len(ee_segments) > 6 and len(ee_segments[6]) > 1 else ""
        )
        
        ee_symbol.pins.append(
            EeSymbolPin(
                settings=pin_settings,
                pin_dot=pin_dot,
                pin_path=pin_path,
                name=pin_name,
                dot=pin_dot_bis,
                clock=pin_clock,
            )
        )
    except Exception as e:
        logging.warning(f"Error parsing pin: {e}")


def add_easyeda_rectangle(rectangle_data: str, ee_symbol: EeSymbol):
    """Parse rectangle data"""
    try:
        fields = rectangle_data.split("~")[1:]
        ee_symbol.rectangles.append(
            EeSymbolRectangle(
                **dict(zip(EeSymbolRectangle.model_fields.keys(), fields))
            )
        )
    except Exception as e:
        logging.warning(f"Error parsing rectangle: {e}")


def add_easyeda_circle(circle_data: str, ee_symbol: EeSymbol):
    """Parse circle data"""
    try:
        fields = circle_data.split("~")[1:]
        ee_symbol.circles.append(
            EeSymbolCircle(
                **dict(zip(EeSymbolCircle.model_fields.keys(), fields))
            )
        )
    except Exception as e:
        logging.warning(f"Error parsing circle: {e}")


def add_easyeda_ellipse(ellipse_data: str, ee_symbol: EeSymbol):
    """Parse ellipse data"""
    try:
        fields = ellipse_data.split("~")[1:]
        ee_symbol.ellipses.append(
            EeSymbolEllipse(
                **dict(zip(EeSymbolEllipse.model_fields.keys(), fields))
            )
        )
    except Exception as e:
        logging.warning(f"Error parsing ellipse: {e}")


def add_easyeda_arc(arc_data: str, ee_symbol: EeSymbol):
    """Parse arc data"""
    try:
        fields = arc_data.split("~")[1:]
        ee_symbol.arcs.append(
            EeSymbolArc(**dict(zip(EeSymbolArc.model_fields.keys(), fields)))
        )
    except Exception as e:
        logging.warning(f"Error parsing arc: {e}")


def add_easyeda_polyline(polyline_data: str, ee_symbol: EeSymbol):
    """Parse polyline data"""
    try:
        fields = polyline_data.split("~")[1:]
        ee_symbol.polylines.append(
            EeSymbolPolyline(
                **dict(zip(EeSymbolPolyline.model_fields.keys(), fields))
            )
        )
    except Exception as e:
        logging.warning(f"Error parsing polyline: {e}")


def add_easyeda_polygon(polygon_data: str, ee_symbol: EeSymbol):
    """Parse polygon data"""
    try:
        fields = polygon_data.split("~")[1:]
        ee_symbol.polygons.append(
            EeSymbolPolygon(
                **dict(zip(EeSymbolPolygon.model_fields.keys(), fields))
            )
        )
    except Exception as e:
        logging.warning(f"Error parsing polygon: {e}")


def add_easyeda_path(path_data: str, ee_symbol: EeSymbol):
    """Parse SVG path data"""
    try:
        fields = path_data.split("~")[1:]
        ee_symbol.paths.append(
            EeSymbolPath(**dict(zip(EeSymbolPath.model_fields.keys(), fields)))
        )
    except Exception as e:
        logging.warning(f"Error parsing path: {e}")


# Handler mapping for EasyEDA shape types
easyeda_handlers = {
    "P": add_easyeda_pin,
    "R": add_easyeda_rectangle,
    "C": add_easyeda_circle,
    "E": add_easyeda_ellipse,
    "A": add_easyeda_arc,
    "PL": add_easyeda_polyline,
    "PG": add_easyeda_polygon,
    "PATH": add_easyeda_path,
}


class EasyedaSymbolImporter:
    """Import and parse EasyEDA symbol data"""
    
    def extract_easyeda_data(
        self, easyeda_symbol: dict, name: str = None, lcsc_id: str = None
    ) -> EeSymbol:
        """
        Extract and parse all symbol data
        
        Args:
            easyeda_symbol: Full CAD data dict from API (has "dataStr" field)
            name: Optional override for component name
            lcsc_id: Optional override for LCSC ID
            
        Returns:
            Parsed EeSymbol structure
        """
        # Extract nested data
        data_str = easyeda_symbol.get("dataStr", {})
        if isinstance(data_str, str):
            import json
            data_str = json.loads(data_str)
        
        head = data_str.get("head", {})
        c_para = head.get("c_para", {})
        
        # Create symbol with metadata
        new_ee_symbol = EeSymbol(
            info=EeSymbolInfo(
                name=name or c_para.get("name", ""),
                prefix=c_para.get("pre", "U"),
                package=c_para.get("package", ""),
                manufacturer=c_para.get("BOM_Manufacturer", ""),
                datasheet=easyeda_symbol.get("datasheet", ""),
                lcsc_id=lcsc_id or str(easyeda_symbol.get("lcsc", "")),
                jlc_id=c_para.get("BOM_JLCPCB Part Class", ""),
            ),
            bbox=EeSymbolBbox(
                x=float(head.get("x", 0)),
                y=float(head.get("y", 0)),
            ),
        )
        
        # Parse all shapes
        shapes = data_str.get("shape", [])
        
        if not shapes:
            logging.warning(
                f"No symbol shapes found in EasyEDA data for {name or lcsc_id}. "
                f"This component may not have a symbol defined in the EasyEDA database. "
                f"You may need to create a custom symbol manually."
            )
        
        for line in shapes:
            designator = line.split("~")[0]
            
            if designator in easyeda_handlers:
                try:
                    easyeda_handlers[designator](line, new_ee_symbol)
                except Exception as e:
                    logging.warning(f"Error handling {designator}: {e}")
        
        logging.info(
            f"Parsed symbol: {len(new_ee_symbol.pins)} pins, "
            f"{len(new_ee_symbol.rectangles)} rectangles, "
            f"{len(new_ee_symbol.circles)} circles"
        )
        
        return new_ee_symbol
