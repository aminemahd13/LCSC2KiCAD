"""
EasyEDA Symbol Parameter Structures - Based on reference implementation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Union
from pydantic import BaseModel, field_validator


class EasyedaPinType(Enum):
    """Pin electrical types"""
    unspecified = 0
    _input = 1
    output = 2
    bidirectional = 3
    power = 4


class EeSymbolBbox(BaseModel):
    """Symbol bounding box origin"""
    x: float
    y: float


# ---------------- PIN ----------------
class EeSymbolPinSettings(BaseModel):
    """Pin settings from first segment of P^^...^^...^^..."""
    is_displayed: bool
    type: EasyedaPinType
    spice_pin_number: str
    pos_x: float
    pos_y: float
    rotation: int
    id: str
    is_locked: bool

    @field_validator("is_displayed", mode="before")
    @classmethod
    def parse_display_field(cls, field: str) -> bool:
        return True if field == "show" else False

    @field_validator("is_locked", mode="before")
    @classmethod
    def empty_str_lock(cls, is_locked: str) -> bool:
        return bool(is_locked) if is_locked else False

    @field_validator("rotation", mode="before")
    @classmethod
    def empty_str_rotation(cls, rotation: str) -> int:
        return int(rotation) if rotation else 0

    @field_validator("type", mode="before")
    @classmethod
    def convert_pin_type(cls, field: str) -> EasyedaPinType:
        try:
            val = int(field or 0)
            return EasyedaPinType(val) if val in EasyedaPinType._value2member_map_ else EasyedaPinType.unspecified
        except:
            return EasyedaPinType.unspecified


class EeSymbolPinDot(BaseModel):
    """Pin dot position (beginning of pin line)"""
    dot_x: float
    dot_y: float


class EeSymbolPinPath(BaseModel):
    """Pin path (line direction)"""
    path: str
    color: str

    @field_validator("path", mode="before")
    @classmethod
    def tune_path(cls, field: str) -> str:
        return field.replace("v", "h")


class EeSymbolPinName(BaseModel):
    """Pin name display settings"""
    is_displayed: bool
    pos_x: float
    pos_y: float
    rotation: int
    text: str
    text_anchor: str
    font: str
    font_size: float

    @field_validator("font_size", mode="before")
    @classmethod
    def parse_font_size(cls, font_size: str) -> float:
        if isinstance(font_size, str) and "pt" in font_size:
            return float(font_size.replace("pt", ""))
        return float(font_size) if font_size else 7.0

    @field_validator("is_displayed", mode="before")
    @classmethod
    def parse_display_field(cls, field: str) -> bool:
        return True if field == "show" else False

    @field_validator("rotation", mode="before")
    @classmethod
    def empty_str_rotation(cls, rotation: str) -> int:
        return int(rotation) if rotation else 0


class EeSymbolPinDotBis(BaseModel):
    """Pin inversion dot (circle at end)"""
    is_displayed: bool
    circle_x: float
    circle_y: float

    @field_validator("is_displayed", mode="before")
    @classmethod
    def parse_display_field(cls, field: str) -> bool:
        return True if field == "show" else False


class EeSymbolPinClock(BaseModel):
    """Pin clock indicator"""
    is_displayed: bool
    path: str

    @field_validator("is_displayed", mode="before")
    @classmethod
    def parse_display_field(cls, field: str) -> bool:
        return True if field == "show" else False


@dataclass
class EeSymbolPin:
    """Complete pin structure"""
    settings: EeSymbolPinSettings
    pin_dot: EeSymbolPinDot
    pin_path: EeSymbolPinPath
    name: EeSymbolPinName
    dot: EeSymbolPinDotBis
    clock: EeSymbolPinClock


# ---------------- RECTANGLE ----------------
class EeSymbolRectangle(BaseModel):
    """Rectangle shape"""
    pos_x: float
    pos_y: float
    rx: Union[float, None] = None
    ry: Union[float, None] = None
    width: float
    height: float
    stroke_color: str
    stroke_width: str
    stroke_style: str
    fill_color: str
    id: str
    is_locked: bool

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, field: str) -> Union[str, None]:
        return field if field else None


# ---------------- CIRCLE ----------------
class EeSymbolCircle(BaseModel):
    """Circle shape"""
    center_x: float
    center_y: float
    radius: float
    stroke_color: str
    stroke_width: str
    stroke_style: str
    fill_color: bool
    id: str
    is_locked: bool

    @field_validator("is_locked", mode="before")
    @classmethod
    def empty_str_lock(cls, field: str) -> bool:
        return bool(field) if field else False

    @field_validator("fill_color", mode="before")
    @classmethod
    def parse_background_filling(cls, fill_color: str) -> bool:
        return bool(fill_color and fill_color.lower() != "none")


# ---------------- ELLIPSE ----------------
class EeSymbolEllipse(BaseModel):
    """Ellipse shape"""
    center_x: float
    center_y: float
    radius_x: float
    radius_y: float
    stroke_color: str
    stroke_width: str
    stroke_style: str
    fill_color: bool
    id: str
    is_locked: bool

    @field_validator("is_locked", mode="before")
    @classmethod
    def empty_str_lock(cls, field: str) -> bool:
        return bool(field) if field else False

    @field_validator("fill_color", mode="before")
    @classmethod
    def parse_background_filling(cls, fill_color: str) -> bool:
        return bool(fill_color and fill_color.lower() != "none")


# ---------------- POLYLINE ----------------
class EeSymbolPolyline(BaseModel):
    """Polyline shape"""
    points: str
    stroke_color: str
    stroke_width: str
    stroke_style: str
    fill_color: bool
    id: str
    is_locked: bool

    @field_validator("is_locked", mode="before")
    @classmethod
    def empty_str_lock(cls, field: str) -> bool:
        return bool(field) if field else False

    @field_validator("fill_color", mode="before")
    @classmethod
    def parse_background_filling(cls, fill_color: str) -> bool:
        return bool(fill_color and fill_color.lower() != "none")


# ---------------- POLYGON ----------------
class EeSymbolPolygon(EeSymbolPolyline):
    """Polygon shape (closed polyline)"""
    pass


# ---------------- ARC ----------------
class EeSymbolArc(BaseModel):
    """Arc shape"""
    path: str  # SVG path
    helper_dots: str
    stroke_color: str
    stroke_width: str
    stroke_style: str
    fill_color: bool
    id: str
    is_locked: bool

    @field_validator("is_locked", mode="before")
    @classmethod
    def empty_str_lock(cls, field: str) -> bool:
        return bool(field) if field else False

    @field_validator("fill_color", mode="before")
    @classmethod
    def parse_background_filling(cls, fill_color: str) -> bool:
        return bool(fill_color and fill_color.lower() != "none")


# ---------------- PATH ----------------
class EeSymbolPath(BaseModel):
    """SVG Path"""
    paths: str
    stroke_color: str
    stroke_width: str
    stroke_style: str
    fill_color: bool
    id: str
    is_locked: bool

    @field_validator("is_locked", mode="before")
    @classmethod
    def empty_str_lock(cls, field: str) -> bool:
        return bool(field) if field else False

    @field_validator("fill_color", mode="before")
    @classmethod
    def parse_background_filling(cls, fill_color: str) -> bool:
        return bool(fill_color and fill_color.lower() != "none")


# ---------------- SYMBOL INFO ----------------
@dataclass
class EeSymbolInfo:
    """Symbol metadata"""
    name: str = ""
    prefix: str = ""
    package: str = ""
    manufacturer: str = ""
    datasheet: str = ""
    lcsc_id: str = ""
    jlc_id: str = ""


# ---------------- COMPLETE SYMBOL ----------------
@dataclass
class EeSymbol:
    """Complete symbol structure"""
    info: EeSymbolInfo
    bbox: EeSymbolBbox
    pins: List[EeSymbolPin] = field(default_factory=list)
    rectangles: List[EeSymbolRectangle] = field(default_factory=list)
    circles: List[EeSymbolCircle] = field(default_factory=list)
    arcs: List[EeSymbolArc] = field(default_factory=list)
    ellipses: List[EeSymbolEllipse] = field(default_factory=list)
    polylines: List[EeSymbolPolyline] = field(default_factory=list)
    polygons: List[EeSymbolPolygon] = field(default_factory=list)
    paths: List[EeSymbolPath] = field(default_factory=list)
