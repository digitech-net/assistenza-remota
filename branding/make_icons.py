"""Genera loghi e icone Digitech a partire da branding/logo-digitech.jpg.

Uso (dalla root del repo):  python branding/make_icons.py
Richiede Pillow e numpy.
"""
import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "branding" / "logo-digitech.jpg"
SYMBOL_MAX_X = 275  # il simbolo "D" finisce prima di questa colonna, poi inizia la scritta
OPAQUE_BELOW = 150  # pixel con canale minimo <= di questo valore sono pieni
CLEAR_ABOVE = 248  # pixel con canale minimo >= di questo valore sono sfondo


def remove_white(img: Image.Image) -> Image.Image:
    rgb = np.asarray(img.convert("RGB")).astype(np.float64)
    mn = rgb.min(axis=2)
    alpha = np.clip((CLEAR_ABOVE - mn) / (CLEAR_ABOVE - OPAQUE_BELOW), 0.0, 1.0)
    safe = np.where(alpha > 0, alpha, 1.0)[..., None]
    color = np.clip((rgb - (1.0 - alpha[..., None]) * 255.0) / safe, 0, 255)
    out = np.dstack([color, alpha * 255.0]).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def trim(img: Image.Image) -> Image.Image:
    return img.crop(img.split()[3].getbbox())


def square(img: Image.Image, size: int, fill: float) -> Image.Image:
    """Centra img in un quadrato trasparente; fill = frazione del lato occupata."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    scale = fill * size / max(img.size)
    w, h = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    canvas.alpha_composite(img.resize((w, h), Image.LANCZOS), ((size - w) // 2, (size - h) // 2))
    return canvas


def on_background(img: Image.Image, size: int, fill: float, shape: str) -> Image.Image:
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size * 4, size * 4), 0)
    d = ImageDraw.Draw(mask)
    if shape == "circle":
        d.ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    else:
        d.rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1), radius=size * 4 // 5, fill=255)
    bg.paste((255, 255, 255, 255), (0, 0), mask.resize((size, size), Image.LANCZOS))
    bg.alpha_composite(square(img, size, fill))
    return bg


def silhouette(img: Image.Image, rgb=(255, 255, 255)) -> Image.Image:
    a = img.split()[3]
    out = Image.new("RGBA", img.size, rgb + (0,))
    out.putalpha(a)
    return out


def logo_for_dark(img: Image.Image) -> Image.Image:
    arr = np.asarray(img).astype(np.float64)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    navy = (b < 140) & (r < 60)
    navy[:, :SYMBOL_MAX_X] = False
    arr[navy, 0:3] = 255.0
    return Image.fromarray(arr.round().astype(np.uint8), "RGBA")


def svg_with_png(img: Image.Image, size: int) -> str:
    buf = io.BytesIO()
    img.resize((size, size), Image.LANCZOS).save(buf, "PNG")
    data = base64.b64encode(buf.getvalue()).decode()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<image width="{size}" height="{size}" xlink:href="data:image/png;base64,{data}"/></svg>\n'
    )


def save(img: Image.Image, rel: str, **kw):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, **kw)
    print("scritto", rel)


def main():
    full = remove_white(Image.open(SRC))
    logo = trim(full)
    symbol = trim(full.crop((0, 0, SYMBOL_MAX_X, full.height)))
    icon = square(symbol, 1024, 0.9)
    ico_sizes = [(s, s) for s in (16, 20, 24, 32, 40, 48, 64, 128, 256)]

    # Logo nella home (max 300x60 a schermo, salvato a risoluzione doppia/tripla)
    h = 180
    save(logo.resize((round(logo.width * h / logo.height), h), Image.LANCZOS), "flutter/assets/logo.png")
    dark = logo_for_dark(logo)
    save(dark.resize((round(dark.width * h / dark.height), h), Image.LANCZOS), "flutter/assets/logo_dark.png")

    # Icone usate dall'app a runtime (finestra, tray, portable)
    save(square(symbol, 512, 0.9), "flutter/assets/icon.png")
    save(icon, "flutter/assets/icon.ico", sizes=ico_sizes)
    (ROOT / "flutter/assets/icon.svg").write_text(svg_with_png(icon, 256))
    print("scritto flutter/assets/icon.svg")

    # Windows
    save(icon, "res/icon.ico", sizes=ico_sizes)
    save(icon, "flutter/windows/runner/resources/app_icon.ico", sizes=ico_sizes)
    save(square(symbol, 256, 0.96), "res/tray-icon.ico", sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (48, 48)])

    # Linux / generiche
    save(icon, "res/icon.png")
    for s, name in ((32, "32x32"), (64, "64x64"), (128, "128x128"), (256, "128x128@2x")):
        save(icon.resize((s, s), Image.LANCZOS), f"res/{name}.png")
    (ROOT / "res/scalable.svg").write_text(svg_with_png(icon, 512))
    print("scritto res/scalable.svg")

    # macOS
    mac = on_background(symbol, 1024, 0.62, "rounded")
    mac_canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    mac_canvas.alpha_composite(mac.resize((824, 824), Image.LANCZOS), (100, 100))
    save(mac_canvas, "res/mac-icon.png")
    save(mac_canvas, "flutter/macos/Runner/AppIcon.icns")
    tray = silhouette(symbol, (0, 0, 0))
    save(square(tray, 60, 0.8), "res/mac-tray-dark-x2.png")
    save(square(tray, 48, 1.0), "res/mac-tray-light-x2.png")

    # Android
    dpis = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
    for dpi, k in dpis.items():
        base = f"flutter/android/app/src/main/res/mipmap-{dpi}"
        s = round(48 * k)
        save(on_background(symbol, s, 0.68, "rounded"), f"{base}/ic_launcher.png")
        save(on_background(symbol, s, 0.62, "circle"), f"{base}/ic_launcher_round.png")
        save(square(symbol, round(108 * k), 0.5), f"{base}/ic_launcher_foreground.png")
        stat = square(silhouette(symbol), round(24 * k), 0.9).convert("LA")
        save(stat, f"{base}/ic_stat_logo.png")


if __name__ == "__main__":
    main()
