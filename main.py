import argparse
import json
import sys
import re
from pathlib import Path
from typing import List, Literal

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display
from pydantic import BaseModel, Field, field_validator, ConfigDict, ValidationError

# =======================
# Validation Models
# =======================

HEX_COLOR_REGEX = r"^#([A-Fa-f0-9]{6})$"


class FillModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["solid", "gradient"]
    color: str | None = None
    colors: List[str] | None = None
    direction: Literal["vertical", "horizontal"] | None = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if v and not re.match(HEX_COLOR_REGEX, v):
            raise ValueError("Color must be valid HEX like #ff00aa")
        return v

    @field_validator("colors")
    @classmethod
    def validate_colors(cls, v):
        if v:
            for color in v:
                if not re.match(HEX_COLOR_REGEX, color):
                    raise ValueError(f"Invalid gradient color: {color}")
        return v


class StrokeModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool
    width: int = Field(ge=0, le=100)
    color: str

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if not re.match(HEX_COLOR_REGEX, v):
            raise ValueError("Stroke color must be HEX like #000000")
        return v


class ShadowModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool
    offset: List[int]
    blur: int = Field(ge=0, le=200)
    color: str
    opacity: float = Field(ge=0, le=1)

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if not re.match(HEX_COLOR_REGEX, v):
            raise ValueError("Shadow color must be HEX like #000000")
        return v


class StyleModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    font_path: str
    font_size: int = Field(gt=0, le=500)
    center: List[int]

    fill: FillModel
    stroke: StrokeModel
    shadow: ShadowModel
    outer_glow: ShadowModel
    inner_shadow: ShadowModel

    letter_spacing: int = Field(ge=0, le=100)
    line_height: float = Field(gt=0, le=5)
    rotation: float = Field(ge=-360, le=360)
    opacity: float = Field(ge=0, le=1)


# =======================
# Utility Functions
# =======================

def hex_to_rgba(hex_color: str, opacity: float = 1.0):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return (r, g, b, int(255 * opacity))


def reshape_text(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def create_gradient(size, colors, direction):
    width, height = size
    gradient = np.zeros((height, width, 4), dtype=np.uint8)

    c1 = np.array(hex_to_rgba(colors[0]))
    c2 = np.array(hex_to_rgba(colors[1]))

    for i in range(height if direction == "vertical" else width):
        ratio = i / (height if direction == "vertical" else width)
        color = (1 - ratio) * c1 + ratio * c2
        if direction == "vertical":
            gradient[i, :] = color
        else:
            gradient[:, i] = color

    return Image.fromarray(gradient)


# =======================
# Render Engine
# =======================

def render(image_path: str, output_path: str, text: str, style: StyleModel):
    if not Path(style.font_path).exists():
        raise FileNotFoundError("Font file not found")

    image = Image.open(image_path).convert("RGBA")
    text_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)

    font = ImageFont.truetype(style.font_path, style.font_size)
    text = reshape_text(text)

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = style.center[0] - w // 2
    y = style.center[1] - h // 2

    # Fill
    if style.fill.type == "solid":
        draw.text((x, y),
                  text,
                  font=font,
                  fill=hex_to_rgba(style.fill.color, style.opacity))
    else:
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).text((x, y), text, font=font, fill=255)
        gradient = create_gradient(image.size,
                                   style.fill.colors,
                                   style.fill.direction)
        text_layer.paste(gradient, (0, 0), mask)

    # Stroke
    if style.stroke.enabled:
        draw.text((x, y),
                  text,
                  font=font,
                  fill=None,
                  stroke_width=style.stroke.width,
                  stroke_fill=hex_to_rgba(style.stroke.color))

    image.alpha_composite(text_layer)

    if style.rotation != 0:
        image = image.rotate(style.rotation, expand=True)

    image.save(output_path)
    print("Rendered successfully →", output_path)


# =======================
# CLI
# =======================

def print_validation_error(e: ValidationError):
    print("\n❌ Style configuration error:\n")

    for error in e.errors():
        field = " → ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        print(f"• {field}: {message}")

    print("\nPlease fix style.json and try again.\n")


def main():
    try:
        parser = argparse.ArgumentParser(description="Advanced Text Renderer")
        parser.add_argument("--image", required=True)
        parser.add_argument("--output", required=True)
        parser.add_argument("--text", required=True)
        parser.add_argument("--style", required=True)

        args = parser.parse_args()

        if not Path(args.image).exists():
            print("❌ Image file not found.")
            sys.exit(1)

        if not Path(args.style).exists():
            print("❌ Style JSON file not found.")
            sys.exit(1)

        with open(args.style, "r", encoding="utf-8") as f:
            style_data = json.load(f)

        style = StyleModel(**style_data)

        render(args.image, args.output, args.text, style)

    except ValidationError as e:
        print_validation_error(e)
        sys.exit(1)

    except Exception as e:
        print("\n❌ Unexpected error:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
