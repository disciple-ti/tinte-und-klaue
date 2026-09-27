# Tinte & Klaue

**Ein Kampfspiel im Browser – mit Tierbildern, die ich selbst gemalt habe.**

![Titelbildschirm](docs/screenshots/titel.jpg)

Ich male gern Tiere, meist als Schablonen-Kunst oder Tuschezeichnung: schwarz-weiß, mit einem einzigen Farbakzent. Irgendwann kam die Frage: *Was wäre, wenn diese Figuren gegeneinander kämpfen könnten?* Also habe ich meine Bilder [Claude](https://claude.ai) gegeben – und eins kam zum anderen.

🎮 **[Direkt im Browser spielen](https://disciple-ti.github.io/tinte-und-klaue/)**

---

## Die Kämpfer

| | Kämpfer | Tempo / Kraft / Vert. | Spezialattacke | Super-Attacke |
|---|---|:---:|---|---|
| 🎸 | **Basso** – Luchs mit E-Bass | 4 / 2 / 3 | Bass-Druckwelle am Boden | **DROP** – die Bühne bebt, nur Springen hilft |
| 🎸 | **Riff** – Tiger mit E-Gitarre | 3 / 4 / 2 | Gitarrenschwung (3 Treffer) | **POWER-CHORD** – riesige Klangwelle |
| 🗡️ | **Laserbear** – Bär mit Laserschwert | 2 / 4 / 3 | Schwertwurf als Bumerang | **LASER-WIRBELSTURM** |
| 🌺 | **Rex Aloha** – T-Rex im Hawaiihemd | 2 / 5 / 2 | Schwanzfeger (wirft um) | **HIBISKUS-STURM** – Blütenregen |
| 🦁 | **Leo Umbra** – Löwe mit Kapuze | 3 / 4 / 2 | Tintenklauen-Sprung | **KÖNIGSBRÜLLER** – Schockwelle |
| 🐯 | **Tigris** – Tiger mit Kapuze | 4 / 4 / 1 | Krallen-Sprint durch den Gegner | **SCHATTENWIRBEL** – 6 Schattenhiebe |

Alle Kämpfer sind ausbalanciert: Die Summe aus Tempo, Kraft und Verteidigung ist immer 9.

<p>
  <img src="docs/screenshots/charakterauswahl.jpg" width="49%" alt="Charakterauswahl">
  <img src="docs/screenshots/super-attacke.jpg" width="49%" alt="Super-Attacke Königsbrüller">
  <img src="docs/screenshots/laserwirbel.jpg" width="49%" alt="Laser-Wirbelsturm im Mondtal">
  <img src="docs/screenshots/kampf-buehne.jpg" width="49%" alt="Kampf auf der Konzertbühne">
  <img src="docs/screenshots/kampf-tempel.jpg" width="49%" alt="Kampf im Tinten-Tempel">
  <img src="docs/screenshots/kampf-strand.jpg" width="49%" alt="Kampf am Strand bei Nacht">
</p>

## Features

- **Arcade** – nacheinander gegen alle anderen Kämpfer, Endgegner ist der Kapuzen-Orden
- **Duell gegen CPU** – Kämpfer, Gegner und Arena frei wählbar
- **2 Spieler an einer Tastatur** – mit Siegstatistik für die Sitzung
- **KI gegen KI** – zum Zuschauen
- **KI** als Zustandsautomat mit drei Schwierigkeitsstufen (reagiert auf Angriffe, blockt, springt über Projektile)
- **Kampfsystem** mit Block (hoch/tief), 3er-Combo mit Finisher, Energieleiste, Super-Attacken mit Einblendung, Hitstop und Bildschirmwackeln
- **4 Arenen**: Mondtal (aus meinem Bild einer Nachtlandschaft), Konzertbühne, Tinten-Tempel, Strand bei Nacht
- **Sound & Musik** komplett per Web Audio API erzeugt – keine Audiodateien
- **Touch-Steuerung** im Einzelspieler auf Tablets und Handys
- Tastenbelegung, Einstellungen und Statistik werden im Browser gespeichert

## Steuerung

| Aktion | Spieler 1 | Spieler 2 |
|---|:---:|:---:|
| Laufen | A / D | ← / → |
| Springen | W | ↑ |
| Ducken | S | ↓ |
| Leichter Angriff | F | Num 1 oder J |
| Schwerer Angriff | G | Num 2 oder K |
| Block | H | Num 3 oder L |
| Spezialattacke | R | Num 4 oder I |
| Super-Attacke | T | Num 5 oder O |

**Esc** = Pause · **M** = Ton an/aus · **F1** = Trefferboxen anzeigen

Tipps: Dreimal leichter Angriff hintereinander löst einen Finisher aus. Tiefe Angriffe lassen sich nur geduckt blocken, Sprungangriffe nur im Stehen. Alle Tasten lassen sich unter *Optionen* neu belegen.

## Technik

- **Eine einzige HTML-Datei** (`index.html`, ca. 940 KB) – HTML, CSS und JavaScript inline, alle Bilder als Base64 eingebettet
- **Keine Frameworks, keine Bibliotheken**, kein Build-Schritt nötig zum Spielen
- Canvas mit fester Auflösung 1280×720, responsiv skaliert
- Spielschleife mit fester Physik-Schrittweite (60 Updates/s), unabhängig von der Bildwiederholrate
- Eingabe über `event.code` – funktioniert auf QWERTZ und QWERTY gleich
- Code und Kommentare auf Deutsch

### Projektstruktur

```
index.html                         fertiges Spiel (wird von tools/build.py erzeugt)
src/tinte-und-klaue.template.html  Quellcode des Spiels (ohne eingebettete Bilder)
img/                               freigestellte Sprites, Einblendungen, Arena-Bild
tools/prep.py                      Bildaufbereitung: Freistellen, Zuschneiden, Skalieren
tools/build.py                     bettet img/ in die Vorlage ein und schreibt index.html
tools/test.js                      automatischer Browsertest mit Playwright
tools/test-2spieler.js             Test für gleichzeitige Eingaben im 2-Spieler-Modus
docs/screenshots/                  Bilder für diese Seite
```

### Selbst bauen

```bash
python3 tools/build.py            # index.html neu erzeugen
```

Neue Kämpfer: Originalbild nach `originale/` legen, in `tools/prep.py` einen Eintrag ergänzen (Hintergrund schwarz/weiß, Zuschnitt), `python3 tools/prep.py` ausführen, dann in der Vorlage einen Eintrag in `CHARAKTERE` und die Attacken in `erstelleAttacken()` anlegen.

Tests (Node.js + Playwright):

```bash
npm install playwright && npx playwright install chromium
node tools/test.js
```

Wer das Spiel lieber mit Bildern aus dem Ordner statt eingebettet ausliefern möchte, setzt in der Vorlage `BILDER_AUS_ORDNER = true` und lädt `img/` mit hoch.

## Entstehung

Die Bilder sind von mir. Das Spiel habe ich zusammen mit Claude (Anthropic) entwickelt: Ich habe Idee, Figuren und Richtung vorgegeben, Claude hat die Bilder freigestellt und den Code geschrieben.

## Lizenz

- **Code** (HTML, CSS, JavaScript, Python-Skripte): [MIT-Lizenz](LICENSE)
- **Bilder und Zeichnungen** (`img/`, `docs/screenshots/` sowie die in `index.html` eingebetteten Bilder): © Tobias Isaak, **alle Rechte vorbehalten** – siehe [LICENSE-BILDER.md](LICENSE-BILDER.md)
