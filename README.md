# 🎨 Advanced Text Rendering Engine (CLI)

A production-ready, Photoshop-like text rendering engine built with
**Python + Pillow**.

This tool allows you to render fully styled text onto images using a
validated JSON configuration file. Designed for automation, batch
processing, and CI/CD usage.

------------------------------------------------------------------------

## ✨ Features

-   CLI-based interface
-   Fully validated `style.json` (Pydantic v2)
-   Clean, user-friendly error messages (no stack traces)
-   Solid and Gradient text fill
-   Stroke (outline)
-   Drop shadow
-   Outer glow
-   Inner shadow
-   Opacity control
-   Rotation
-   Multi-line text
-   RTL (Arabic / Persian) support
-   Strict JSON schema (no extra fields allowed)
-   Production-safe exit codes

------------------------------------------------------------------------

## 📦 Requirements

-   Python 3.10+
-   uv (recommended) or pip

------------------------------------------------------------------------

## 🚀 Installation

### Using uv (recommended)

``` bash
uv venv
uv pip install pillow arabic-reshaper python-bidi numpy pydantic
```

### Using pip

``` bash
python -m venv .venv
source .venv/bin/activate
pip install pillow arabic-reshaper python-bidi numpy pydantic
```

------------------------------------------------------------------------

## 🖼 Usage

``` bash
python main.py   --image assets/input.jpg   --output assets/output.png   --text "Hello World"   --style assets/style.json
```

------------------------------------------------------------------------

## 📄 CLI Arguments

  Argument     Required   Description
  ------------ ---------- ---------------------------
  `--image`    Yes        Path to input image
  `--output`   Yes        Path to save output image
  `--text`     Yes        Text to render
  `--style`    Yes        Path to style.json

------------------------------------------------------------------------

## 🧾 style.json Example

``` json
{
  "font_path": "Vazirmatn-Regular.ttf",
  "font_size": 90,
  "center": [800, 450],
  "fill": {
    "type": "gradient",
    "colors": ["#ff0080", "#7928ca"],
    "direction": "vertical"
  },
  "stroke": {
    "enabled": true,
    "width": 4,
    "color": "#000000"
  },
  "shadow": {
    "enabled": true,
    "offset": [8, 8],
    "blur": 15,
    "color": "#000000",
    "opacity": 0.6
  },
  "outer_glow": {
    "enabled": true,
    "offset": [0, 0],
    "blur": 20,
    "color": "#ff00ff",
    "opacity": 0.5
  },
  "inner_shadow": {
    "enabled": false,
    "offset": [3, 3],
    "blur": 10,
    "color": "#000000",
    "opacity": 0.5
  },
  "letter_spacing": 5,
  "line_height": 1.2,
  "rotation": 0,
  "opacity": 1.0
}
```

------------------------------------------------------------------------

## 🔒 Validation

-   Invalid HEX colors are rejected
-   Missing required fields produce clear error messages
-   Extra JSON fields are forbidden
-   Numeric ranges are enforced
-   No stack traces shown to end users

Example error:

    ❌ Style configuration error:
    • outer_glow → offset: Field required
    Please fix style.json and try again.

------------------------------------------------------------------------

## 🌍 RTL Support

Arabic and Persian text is automatically reshaped using: -
arabic-reshaper - python-bidi

------------------------------------------------------------------------

## 🧪 Exit Codes

  Code   Meaning
  ------ -----------------------------
  0      Success
  1      Validation or runtime error

------------------------------------------------------------------------

## 📜 License

MIT License
