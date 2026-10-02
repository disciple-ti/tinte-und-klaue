"""Bildaufbereitung: Charakterblätter (3 Haltungen nebeneinander) zerlegen,
freistellen und einheitlich ausrichten; Hintergründe verkleinern.

Liest die Originale aus ./originale/ (nicht im Repository) und schreibt nach ./img/:
  <id>_haltung1.webp, <id>_haltung2.webp, <id>_haltung3.webp   (gleich große Leinwand,
      Körpermitte horizontal mittig, Fußpunkt an der Unterkante -> kein Springen beim Wechsel)
  hintergrund_<name>.webp

Aufruf aus dem Projektordner:
    pip install pillow numpy scipy
    python3 tools/prep.py
"""
import os, json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(BASIS, 'originale')
OUT = os.path.join(BASIS, 'img')
STAND_HOEHE = 400   # Höhe der Haltung 1 in Pixeln (alle Haltungen gleicher Maßstab)

# id: (Datei, Hintergrundart, Radius zum Schließen der Kontur)
BLAETTER = {
    'basso': ('basso_blatt.jpg', 'weiss', 6),
    'coolcat': ('coolcat_blatt.jpg', 'weiss', 16),   # weißes Fell auf weißem Grund
    'riff': ('riff_blatt.jpg', 'weiss', 6),
    'rex': ('rex_blatt.jpg', 'weiss', 6),
    'bear': ('bear_blatt.jpg', 'schachbrett', 9),
    'glut': ('glut_blatt.png', 'schwarz', 4),
}
HINTERGRUENDE = {   # Name: (Datei, Zielbreite)
    'synthwave': ('bg_synthwave.jpg', 1600),
    'spielhalle': ('bg_spielhalle.jpg', 1600),
    'retro': ('bg_retro.jpg', 1600),
    'gamingzimmer': ('bg_gamingzimmer.jpg', 1600),
}


def kreis(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def vordergrund(a, art):
    """Rohmaske: welche Pixel gehören zu Figuren (nicht zum Hintergrund)."""
    mx, mn = a.max(axis=2), a.min(axis=2)
    satt = mx - mn
    if art == 'weiss':
        return mn < 244
    if art == 'schachbrett':   # helles Grau/Weiß-Schachbrett ist eingebrannt
        return (mx < 205) | (satt > 40)
    if art == 'schwarz':       # schwarzer Körper auf schwarzem Grund mit Leuchten
        r, g = a[..., 0], a[..., 1]
        hell = mx.astype(float)
        detail = hell - ndi.gaussian_filter(hell, 3)           # feine Fellstriche, kein weicher Schein
        striche = ((detail > 25) & (satt < 80)).astype(float)
        koerper = ndi.binary_fill_holes(ndi.gaussian_filter(striche, 7) > 0.10)
        kern = (r > 235) & (g > 170)                             # heller Klingenkern
        klinge = kern | (ndi.binary_dilation(kern, structure=kreis(5)) & (r > 150))
        return koerper | klinge
    raise ValueError(art)


def zerlege(id_, datei, art, r):
    im = Image.open(os.path.join(ORIG, datei)).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    roh = vordergrund(a, art)
    # Rauschen entfernen, Silhouetten schließen, Löcher füllen
    roh = ndi.binary_opening(roh, structure=kreis(1))
    pad = 2 * r
    m = ndi.binary_closing(np.pad(roh, pad), structure=kreis(r))[pad:-pad, pad:-pad]
    m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m)
    groessen = ndi.sum(m, lab, range(1, n + 1))
    gross = np.argsort(groessen)[::-1][:3] + 1
    if len(gross) < 3 or groessen[gross[2] - 1] < groessen[gross[0] - 1] * 0.15:
        raise SystemExit(f'{id_}: konnte keine 3 getrennten Haltungen finden')
    # Haltungen von links nach rechts sortieren
    gross = sorted(gross, key=lambda l: ndi.center_of_mass(lab == l)[1])
    # kleine Teile (Schnurrhaare, Spitzen) der nächstgelegenen Haltung zuordnen
    masken = [lab == l for l in gross]
    zonen = [ndi.binary_dilation(mk, structure=kreis(20)) for mk in masken]
    for l in range(1, n + 1):
        if l in gross or groessen[l - 1] < 40:
            continue
        teil = lab == l
        treffer = [z[teil].sum() for z in zonen]
        if max(treffer) > 0:
            masken[int(np.argmax(treffer))] |= teil

    infos = []
    for mk in masken:
        ys, xs = np.where(mk)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        h = y1 - y0
        band = (ys > y0 + h * 0.3) & (ys < y0 + h * 0.75)     # Rumpf für die Körpermitte
        cx = xs[band].mean()
        breite = np.percentile(xs[band], 90) - np.percentile(xs[band], 10)
        infos.append(dict(maske=mk, y0=y0, y1=y1, x0=x0, x1=x1, cx=cx, breite=breite))

    s = STAND_HOEHE / (infos[0]['y1'] - infos[0]['y0'])
    halb = max(max(i['cx'] - i['x0'], i['x1'] - i['cx']) for i in infos) * s + 6
    hoch = max(i['y1'] - i['y0'] for i in infos) * s + 6
    W, H = int(np.ceil(halb * 2)), int(np.ceil(hoch))
    for nr, i in enumerate(infos, 1):
        teil = im.crop((i['x0'], i['y0'], i['x1'], i['y1'])).convert('RGBA')
        maske = Image.fromarray((i['maske'][i['y0']:i['y1'], i['x0']:i['x1']] * 255).astype(np.uint8))
        teil.putalpha(maske.filter(ImageFilter.GaussianBlur(0.9)))
        tw, th = round(teil.width * s), round(teil.height * s)
        teil = teil.resize((tw, th), Image.LANCZOS)
        leinwand = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        leinwand.alpha_composite(teil, (round(W / 2 - (i['cx'] - i['x0']) * s), H - th))
        leinwand.save(os.path.join(OUT, f'{id_}_haltung{nr}.webp'), 'WEBP', quality=82, method=6)
    meta = dict(breite=W, hoehe=H, stand=STAND_HOEHE, rumpf=round(infos[0]['breite'] * s))
    print(id_, meta)
    return meta


def hintergrund(name, datei, breite):
    im = Image.open(os.path.join(ORIG, datei)).convert('RGB')
    im = im.resize((breite, round(im.height * breite / im.width)), Image.LANCZOS)
    pfad = os.path.join(OUT, f'hintergrund_{name}.webp')
    im.save(pfad, 'WEBP', quality=74, method=6)
    print(name, im.size, os.path.getsize(pfad) // 1024, 'KB')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    meta = {id_: zerlege(id_, *v) for id_, v in BLAETTER.items()}
    for name, (datei, breite) in HINTERGRUENDE.items():
        hintergrund(name, datei, breite)
    with open(os.path.join(ORIG, 'meta.json'), 'w') as d:
        json.dump(meta, d, indent=1)
