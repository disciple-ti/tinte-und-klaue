"""Baut index.html: bettet alle Bilder aus ./img/ als Base64 in die Vorlage ein.

Aufruf aus dem Projektordner:  python3 tools/build.py
"""
import base64, json, os

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASIS, 'img')
MIME = {'webp': 'image/webp', 'jpg': 'image/jpeg', 'png': 'image/png'}

bilder = {}
for f in sorted(os.listdir(IMG)):
    name, ext = f.rsplit('.', 1)
    if ext not in MIME:
        continue
    with open(os.path.join(IMG, f), 'rb') as d:
        bilder[name] = f'data:{MIME[ext]};base64,' + base64.b64encode(d.read()).decode()

with open(os.path.join(BASIS, 'src', 'tinte-und-klaue.template.html'), encoding='utf-8') as d:
    vorlage = d.read()
assert '/*__BILDER__*/{}' in vorlage, 'Platzhalter /*__BILDER__*/{} fehlt in der Vorlage'
html = vorlage.replace('/*__BILDER__*/{}', json.dumps(bilder, separators=(',', ':')))
with open(os.path.join(BASIS, 'index.html'), 'w', encoding='utf-8') as d:
    d.write(html)
print(f'index.html geschrieben ({len(html) // 1024} KB, {len(bilder)} Bilder)')
