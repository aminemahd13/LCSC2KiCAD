"""
KiCad Symbol Parameter Structures - Based on reference implementation
"""

import itertools
import re
import textwrap
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Union


class KicadVersion(Enum):
    """KiCad version"""
    v5 = auto()
    v6 = auto()


class KiPinType(Enum):
    """Pin electrical types"""
    _input = auto()
    output = auto()
    bidirectional = auto()
    tri_state = auto()
    passive = auto()
    free = auto()
    unspecified = auto()
    power_in = auto()
    power_out = auto()
    open_collector = auto()
    open_emitter = auto()
    no_connect = auto()


class KiPinStyle(Enum):
    """Pin graphical styles"""
    line = auto()
    inverted = auto()
    clock = auto()
    inverted_clock = auto()
    input_low = auto()
    clock_low = auto()
    output_low = auto()
    edge_clock_high = auto()
    non_logic = auto()


class KiBoxFill(Enum):
    """Fill types for shapes"""
    none = auto()
    outline = auto()
    background = auto()


# Export configuration for V6
class KiExportConfigV6(Enum):
    """KiCad V6 export constants (dimensions in mm)"""
    PIN_LENGTH = 2.54
    PIN_SPACING = 2.54
    PIN_NUM_SIZE = 1.27
    PIN_NAME_SIZE = 1.27
    DEFAULT_BOX_LINE_WIDTH = 0.254
    PROPERTY_FONT_SIZE = 1.27
    FIELD_OFFSET_START = 5.08
    FIELD_OFFSET_INCREMENT = 2.54


def sanitize_fields(name: str) -> str:
    """Sanitize field names for KiCad"""
    return name.replace(" ", "_").replace("/", "_")


def apply_text_style(text: str, kicad_version: KicadVersion) -> str:
    """Apply text styling (overline for active-low signals)"""
    if text.endswith("#"):
        text = (
            f"~{{{text[:-1]}}}"
            if kicad_version == KicadVersion.v6
            else f"~{text[:-1]}~"
        )
    return text


def apply_pin_name_style(pin_name: str, kicad_version: KicadVersion) -> str:
    """Apply pin name styling"""
    return "/".join(
        apply_text_style(text=txt, kicad_version=kicad_version)
        for txt in pin_name.split("/")
    )


# ---------------- INFO HEADER ----------------
@dataclass
class KiSymbolInfo:
    """Symbol metadata and properties"""
    name: str
    prefix: str
    package: str
    manufacturer: str
    datasheet: str
    lcsc_id: str
    jlc_id: str
    y_low: Union[int, float] = 0
    y_high: Union[int, float] = 0
    
    def export_v6(self) -> List[str]:
        """Export properties in KiCad V6 format"""
        property_template = textwrap.indent(
            textwrap.dedent(
                """
                (property
                  "{key}"
                  "{value}"
                  (id {id_})
                  (at 0 {pos_y:.2f} 0)
                  (effects (font (size {font_size} {font_size}) {style}) {hide})
                )"""
            ),
            "  ",
        )
        
        field_offset_y = KiExportConfigV6.FIELD_OFFSET_START.value
        header: List[str] = [
            property_template.format(
                key="Reference",
                value=self.prefix,
                id_=0,
                pos_y=self.y_high + field_offset_y,
                font_size=KiExportConfigV6.PROPERTY_FONT_SIZE.value,
                style="",
                hide="",
            ),
            property_template.format(
                key="Value",
                value=self.name,
                id_=1,
                pos_y=self.y_low - field_offset_y,
                font_size=KiExportConfigV6.PROPERTY_FONT_SIZE.value,
                style="",
                hide="",
            ),
        ]
        
        if self.package:
            field_offset_y += KiExportConfigV6.FIELD_OFFSET_INCREMENT.value
            header.append(
                property_template.format(
                    key="Footprint",
                    value=self.package,
                    id_=2,
                    pos_y=self.y_low - field_offset_y,
                    font_size=KiExportConfigV6.PROPERTY_FONT_SIZE.value,
                    style="",
                    hide="hide",
                )
            )
        
        if self.datasheet:
            field_offset_y += KiExportConfigV6.FIELD_OFFSET_INCREMENT.value
            header.append(
                property_template.format(
                    key="Datasheet",
                    value=self.datasheet,
                    id_=3,
                    pos_y=self.y_low - field_offset_y,
                    font_size=KiExportConfigV6.PROPERTY_FONT_SIZE.value,
                    style="",
                    hide="hide",
                )
            )
        
        if self.lcsc_id:
            field_offset_y += KiExportConfigV6.FIELD_OFFSET_INCREMENT.value
            header.append(
                property_template.format(
                    key="LCSC",
                    value=self.lcsc_id,
                    id_=4,
                    pos_y=self.y_low - field_offset_y,
                    font_size=KiExportConfigV6.PROPERTY_FONT_SIZE.value,
                    style="",
                    hide="hide",
                )
            )
        
        if self.manufacturer:
            field_offset_y += KiExportConfigV6.FIELD_OFFSET_INCREMENT.value
            header.append(
                property_template.format(
                    key="Manufacturer",
                    value=self.manufacturer,
                    id_=5,
                    pos_y=self.y_low - field_offset_y,
                    font_size=KiExportConfigV6.PROPERTY_FONT_SIZE.value,
                    style="",
                    hide="hide",
                )
            )
        
        if self.jlc_id:
            field_offset_y += KiExportConfigV6.FIELD_OFFSET_INCREMENT.value
            header.append(
                property_template.format(
                    key="JLC Part",
                    value=self.jlc_id,
                    id_=6,
                    pos_y=self.y_low - field_offset_y,
                    font_size=KiExportConfigV6.PROPERTY_FONT_SIZE.value,
                    style="",
                    hide="hide",
                )
            )
        
        return header


# ---------------- PIN ----------------
@dataclass
class KiSymbolPin:
    """Pin definition"""
    name: str
    number: str
    style: KiPinStyle
    length: float
    type: KiPinType
    orientation: float
    pos_x: Union[int, float]
    pos_y: Union[int, float]
    
    def export_v6(self) -> str:
        """Export pin in KiCad V6 format"""
        return """
            (pin {pin_type} {pin_style}
              (at {x:.2f} {y:.2f} {orientation})
              (length {pin_length})
              (name "{pin_name}" (effects (font (size {name_size} {name_size}))))
              (number "{pin_num}" (effects (font (size {num_size} {num_size}))))
            )""".format(
            pin_type=self.type.name[1:]
            if self.type.name.startswith("_")
            else self.type.name,
            pin_style=self.style.name,
            x=self.pos_x,
            y=self.pos_y,
            orientation=(180 + self.orientation) % 360,
            pin_length=self.length,
            pin_name=apply_pin_name_style(
                pin_name=self.name, kicad_version=KicadVersion.v6
            ),
            name_size=KiExportConfigV6.PIN_NAME_SIZE.value,
            pin_num=self.number,
            num_size=KiExportConfigV6.PIN_NUM_SIZE.value,
        )


# ---------------- RECTANGLE ----------------
@dataclass
class KiSymbolRectangle:
    """Rectangle shape"""
    pos_x0: Union[int, float] = 0
    pos_y0: Union[int, float] = 0
    pos_x1: Union[int, float] = 0
    pos_y1: Union[int, float] = 0
    
    def export_v6(self) -> str:
        """Export rectangle in KiCad V6 format"""
        return """
            (rectangle
              (start {x0:.2f} {y0:.2f})
              (end {x1:.2f} {y1:.2f})
              (stroke (width {line_width}) (type default) (color 0 0 0 0))
              (fill (type {fill}))
            )""".format(
            x0=self.pos_x0,
            y0=self.pos_y0,
            x1=self.pos_x1,
            y1=self.pos_y1,
            line_width=KiExportConfigV6.DEFAULT_BOX_LINE_WIDTH.value,
            fill=KiBoxFill.background.name,
        )


# ---------------- POLYGON ----------------
@dataclass
class KiSymbolPolygon:
    """Polygon/polyline shape"""
    points: List[List[float]] = field(default_factory=list)
    points_number: int = 0
    is_closed: bool = False
    
    def export_v6(self) -> str:
        """Export polyline in KiCad V6 format"""
        return """
            (polyline
              (pts
                {polyline_path}
              )
              (stroke (width {line_width}) (type default) (color 0 0 0 0))
              (fill (type {fill}))
            )""".format(
            polyline_path=" ".join(
                [f"(xy {pts[0]:.2f} {pts[1]:.2f})" for pts in self.points]
            ),
            line_width=KiExportConfigV6.DEFAULT_BOX_LINE_WIDTH.value,
            fill=KiBoxFill.background.name if self.is_closed else KiBoxFill.none.name,
        )


# ---------------- CIRCLE ----------------
@dataclass
class KiSymbolCircle:
    """Circle shape"""
    pos_x: Union[int, float] = 0
    pos_y: Union[int, float] = 0
    radius: Union[int, float] = 0
    background_filling: bool = False
    
    def export_v6(self) -> str:
        """Export circle in KiCad V6 format"""
        return """
            (circle
              (center {pos_x:.2f} {pos_y:.2f})
              (radius {radius:.2f})
              (stroke (width {line_width}) (type default) (color 0 0 0 0))
              (fill (type {fill}))
            )""".format(
            pos_x=self.pos_x,
            pos_y=self.pos_y,
            radius=self.radius,
            line_width=KiExportConfigV6.DEFAULT_BOX_LINE_WIDTH.value,
            fill=KiBoxFill.background.name
            if self.background_filling
            else KiBoxFill.none.name,
        )


# ---------------- ARC ----------------
@dataclass
class KiSymbolArc:
    """Arc shape"""
    center_x: float = 0
    center_y: float = 0
    radius: float = 0
    angle_start: float = 0.0
    angle_end: float = 0.0
    start_x: float = 0
    start_y: float = 0
    middle_x: float = 0
    middle_y: float = 0
    end_x: float = 0
    end_y: float = 0
    
    def export_v6(self) -> str:
        """Export arc in KiCad V6 format"""
        return """
            (arc
              (start {start_x:.2f} {start_y:.2f})
              (mid {middle_x:.2f} {middle_y:.2f})
              (end {end_x:.2f} {end_y:.2f})
              (stroke (width {line_width}) (type default) (color 0 0 0 0))
              (fill (type {fill}))
            )""".format(
            start_x=self.start_x,
            start_y=self.start_y,
            middle_x=self.middle_x,
            middle_y=self.middle_y,
            end_x=self.end_x,
            end_y=self.end_y,
            line_width=KiExportConfigV6.DEFAULT_BOX_LINE_WIDTH.value,
            fill=KiBoxFill.background.name
            if self.angle_start == self.angle_end
            else KiBoxFill.none.name,
        )


# ---------------- SYMBOL ----------------
@dataclass
class KiSymbol:
    """Complete KiCad symbol"""
    info: KiSymbolInfo
    pins: List[KiSymbolPin] = field(default_factory=list)
    rectangles: List[KiSymbolRectangle] = field(default_factory=list)
    circles: List[KiSymbolCircle] = field(default_factory=list)
    arcs: List[KiSymbolArc] = field(default_factory=list)
    polygons: List[KiSymbolPolygon] = field(default_factory=list)
    
    def export_v6(self):
        """Export complete symbol in KiCad V6 format"""
        # Calculate y bounds from pins
        self.info.y_low = min(pin.pos_y for pin in self.pins) if self.pins else 0
        self.info.y_high = max(pin.pos_y for pin in self.pins) if self.pins else 0
        
        # Export all components
        sym_info = self.info.export_v6()
        sym_pins = [pin.export_v6() for pin in self.pins]
        sym_rectangles = [rect.export_v6() for rect in self.rectangles]
        sym_circles = [circ.export_v6() for circ in self.circles]
        sym_arcs = [arc.export_v6() for arc in self.arcs]
        sym_polygons = [poly.export_v6() for poly in self.polygons]
        
        sym_graphic_items = sym_rectangles + sym_circles + sym_arcs + sym_polygons
        
        return textwrap.indent(
            textwrap.dedent(
                """
            (symbol "{library_id}"
              (in_bom yes)
              (on_board yes)
              {symbol_properties}
              (symbol "{library_id}_0_1"
                {graphic_items}
                {pins}
              )
            )"""
            ),
            "  ",
        ).format(
            library_id=sanitize_fields(self.info.name),
            symbol_properties=textwrap.indent(
                textwrap.dedent("".join(sym_info)), "  " * 2
            ),
            graphic_items=textwrap.indent(
                textwrap.dedent("".join(sym_graphic_items)), "  " * 3
            ),
            pins=textwrap.indent(textwrap.dedent("".join(sym_pins)), "  " * 3),
        )
    
    def export(self, kicad_version: KicadVersion) -> str:
        """Export symbol (clean up extra newlines)"""
        component_data = self.export_v6()
        return re.sub(r"\n\s*\n", "\n", component_data, re.MULTILINE)
