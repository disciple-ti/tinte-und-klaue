"""Bildaufbereitung: Freistellen, Zuschneiden, Skalieren.

Liest die Originalbilder aus ./originale/ (nicht im Repository) und schreibt
die fertigen Sprites nach ./img/. Aufruf aus dem Projektordner:

    pip install pillow numpy scipy
    python3 tools/prep.py
"""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
import os, json

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = os.path.join(BASIS, 'originale') + '/'
OUT = os.path.join(BASIS, 'img')
os.makedirs(OUT, exist_ok=True)

def disk(r):
    y, x = np.ogrid[-r:r+1, -r:r+1]
    return x*x + y*y <= r*r

def cutout(src, bg, crop=None, thr=None, close_r=10, min_frac=0.02, erase=(), target_h=440, name=None, ortho=False):
    im = Image.open(U + src).convert('RGB')
    a = np.asarray(im).astype(np.int16).copy()
    for (x0, y0, x1, y1) in erase:  # Signatur / Schrift übermalen
        a[y0:y1, x0:x1] = 0 if bg == 'black' else 255
    if crop:
        x0, y0, x1, y1 = crop
        a = a[y0:y1, x0:x1]
    if bg == 'black':
        fg = a.max(axis=2) > (thr or 38)
    else:
        fg = a.min(axis=2) < (thr or 222)
    # kleine Teile (Spritzer) entfernen
    lab, n = ndi.label(fg)
    sizes = ndi.sum(fg, lab, range(1, n+1))
    keep = np.zeros(n+1, bool)
    big = sizes.max()
    keep[1:] = sizes >= big * min_frac
    fg = keep[lab]
    # Silhouette schließen + Löcher füllen
    pad = close_r * 2
    fgp = np.pad(fg, pad)
    fgp = ndi.binary_closing(fgp, structure=disk(close_r))
    fg = fgp[pad:-pad, pad:-pad]
    fg = ndi.binary_fill_holes(fg)
    if ortho:  # orthogonal konvexe Hülle: Zeilen- UND Spaltenspannen füllen
        rows = np.zeros_like(fg); cols = np.zeros_like(fg)
        for i in range(fg.shape[0]):
            idx = np.flatnonzero(fg[i])
            if idx.size: rows[i, idx[0]:idx[-1]+1] = True
        for j in range(fg.shape[1]):
            idx = np.flatnonzero(fg[:, j])
            if idx.size: cols[idx[0]:idx[-1]+1, j] = True
        fg = rows & cols
    lab, n = ndi.label(fg)
    sizes = ndi.sum(fg, lab, range(1, n+1))
    keep = np.zeros(n+1, bool); keep[1:] = sizes >= sizes.max() * min_frac
    fg = keep[lab]
    ys, xs = np.where(fg)
    y0, y1, x0, x1 = ys.min(), ys.max()+1, xs.min(), xs.max()+1
    rgb = a[y0:y1, x0:x1].astype(np.uint8)
    m = (fg[y0:y1, x0:x1] * 255).astype(np.uint8)
    mimg = Image.fromarray(m).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.fromarray(rgb).convert('RGBA')
    out.putalpha(mimg)
    s = target_h / out.height
    out = out.resize((round(out.width * s), target_h), Image.LANCZOS)
    out.save(f'{OUT}/{name}.webp', 'WEBP', quality=84, method=6)
    return out

sprites = {}
# Kämpfer
sprites['basso'] = cutout('Bass_Luchs.jpg', 'black', erase=[(1350, 2060, 1620, 2160)], name='basso')
sprites['riff'] = cutout('Tiger_Guitar.jpg', 'black', erase=[(1350, 2060, 1620, 2160)], name='riff')
sprites['bear'] = cutout('Laserbear.webp', 'black', crop=(0, 0, 766, 880), close_r=8, thr=12, ortho=True, name='bear')
sprites['rex'] = cutout('Dinosaur.jpg', 'white', crop=(0, 0, 1620, 1680), name='rex')
sprites['leo'] = cutout('HoodieLion.jpg', 'white', crop=(0, 0, 1620, 2040), min_frac=0.05, close_r=14, name='leo')
sprites['tigris'] = cutout('HoodieTiger.jpg', 'white', crop=(0, 0, 1620, 1930), thr=215, min_frac=0.05, close_r=14, name='tigris')

# Vorschau auf Grau und Rot
W = sum(s.width for s in sprites.values()) + 20 * len(sprites)
sheet = Image.new('RGBA', (W, 460 * 2), (0, 0, 0, 255))
x = 0
for s in sprites.values():
    for row, col in enumerate([(110, 110, 110, 255), (170, 20, 20, 255)]):
        bgi = Image.new('RGBA', s.size, col)
        bgi.alpha_composite(s)
        sheet.paste(bgi, (x, row * 460))
    x += s.width + 20
sheet.convert('RGB').save(os.path.join(BASIS, 'originale', 'vorschau.jpg'), quality=80)
print({k: v.size for k, v in sprites.items()})

# Cut-ins (Super-Attacken)
def strip(src, box, name, w=900):
    im = Image.open(U + src).convert('RGB').crop(box)
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(f'{OUT}/{name}.jpg', quality=78)
    print(name, im.size)
strip('Loewe.jpg', (300, 560, 1750, 1300), 'cut_leo')
strip('Tigerschrei.jpg', (0, 350, 1620, 1250), 'cut_tiger')

# Mondtal: Landschaft (unterhalb des Mondes) + Mond separat
im = Image.open(U + 'Nachtlandschaft.jpg').convert('RGB')
land = im.crop((0, 290, 1620, 2100))
land = land.resize((600, round(land.height * 600 / 1620)), Image.LANCZOS)
from PIL import ImageDraw
ImageDraw.Draw(land).rectangle((0, 0, 170, 40), fill=(0, 0, 0))  # Rest der Mondsichel entfernen
land.save(f'{OUT}/mondtal.jpg', quality=74)
moon = im.crop((60, 50, 340, 380))
ma = np.asarray(moon).astype(np.float32)
lum = ma.max(axis=2)
alpha = np.clip((lum - 25) * 2.2, 0, 255).astype(np.uint8)
mo = Image.fromarray(np.dstack([np.full_like(alpha, 235), np.full_like(alpha, 235), np.full_like(alpha, 228), alpha]), 'RGBA')
mo = mo.resize((140, 165), Image.LANCZOS)
mo.save(f'{OUT}/mond.webp', 'WEBP', quality=85)
print('land', land.size)
for f in sorted(os.listdir(OUT)):
    print(f, os.path.getsize(f'{OUT}/{f}') // 1024, 'KB')
