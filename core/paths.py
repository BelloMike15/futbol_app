from pathlib import Path

HERE = Path(__file__).resolve().parent          # futbol_app/core
APP_ROOT = HERE.parent                          # futbol_app
ASSETS = APP_ROOT / "assets"
CSS_DIR = ASSETS / "css"
IMG_DIR = ASSETS / "img"
ANIM_DIR = ASSETS / "animaciones"

def css_path(name: str) -> Path:
    return CSS_DIR / name

def img_path(name: str) -> Path:
    return IMG_DIR / name

def anim_path(name: str) -> Path:
    return ANIM_DIR / name
