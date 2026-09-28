"""Webversionen der Bilder erzeugen.

Die Originale in images/projekte/ und images/hero/ bleiben unverändert.
Die Website lädt ausschließlich die hier erzeugten, verkleinerten WebP-Dateien:

  images/web/{projekt-id}/{dateiname}-{breite}.webp
      Breiten 480, 960, 1440 (Karten, Bilderleisten, Projektliste)
      und 2400 (Galerie). Kleinere Originale werden nicht vergrößert,
      die Datei trägt dann trotzdem den Namen der Größenstufe.

  images/web/hero/{dateiname}-1600.webp
      Handy-Fassung der Titelbilder. Die Originale in images/hero/ sind
      bereits WebP in voller Breite und dienen als große Fassung.

Neues Projekt oder neues Foto: Original nach images/projekte/{id}/ legen,
dann im Projektordner ausführen:

    python3 _werkzeuge/bilder-optimieren.py

Bereits erzeugte Dateien werden übersprungen, solange das Original nicht
neuer ist. Danach den Ordner images/web/ per Cyberduck hochladen.
Benötigt Pillow (pip3 install Pillow).
"""
import os
import sys
import unicodedata
from PIL import Image, ImageOps

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJEKTE = os.path.join(WURZEL, 'images', 'projekte')
HERO = os.path.join(WURZEL, 'images', 'hero')
ZIEL = os.path.join(WURZEL, 'images', 'web')

BREITEN = [480, 960, 1440, 2400]
HERO_BREITE = 1600
QUALITAET = 90       # Projektbilder: im Vergleich nicht vom Original zu unterscheiden
HERO_QUALITAET = 80  # Titelbilder liegen gedämpft unter einem Verlauf, 80 entspricht den Originalen
ENDUNGEN = ('.jpg', '.jpeg', '.png', '.webp')


def aktuell(quelle, ziel):
    return os.path.exists(ziel) and os.path.getmtime(ziel) >= os.path.getmtime(quelle)


def speichern(bild, breite, ziel, qualitaet=QUALITAET):
    if bild.width > breite:
        hoehe = round(bild.height * breite / bild.width)
        bild = bild.resize((breite, hoehe), Image.LANCZOS)
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    bild.save(ziel, 'WEBP', quality=qualitaet, method=6)


def oeffnen(pfad):
    bild = ImageOps.exif_transpose(Image.open(pfad))
    # Transparenz nur behalten, wo es sie wirklich gibt
    if bild.mode in ('RGBA', 'LA', 'P'):
        bild = bild.convert('RGBA')
        if bild.getextrema()[3][0] == 255:
            bild = bild.convert('RGB')
    elif bild.mode != 'RGB':
        bild = bild.convert('RGB')
    return bild


def main():
    neu = uebersprungen = 0
    for projekt in sorted(os.listdir(PROJEKTE)):
        ordner = os.path.join(PROJEKTE, projekt)
        if not os.path.isdir(ordner):
            continue
        for datei in sorted(os.listdir(ordner)):
            if not datei.lower().endswith(ENDUNGEN):
                continue
            quelle = os.path.join(ordner, datei)
            # macOS speichert Umlaute teils zerlegt (o + ¨). Server und HTML nutzen die
            # zusammengesetzte Form, deshalb die Zielnamen einheitlich so schreiben.
            name = unicodedata.normalize('NFC', os.path.splitext(datei)[0])
            ziele = {b: os.path.join(ZIEL, projekt, f'{name}-{b}.webp') for b in BREITEN}
            offen = [b for b, z in ziele.items() if not aktuell(quelle, z)]
            uebersprungen += len(BREITEN) - len(offen)
            if not offen:
                continue
            bild = oeffnen(quelle)
            for b in offen:
                speichern(bild, b, ziele[b])
                neu += 1
            print(f'{projekt}/{datei}: {len(offen)} Fassungen')

    for datei in sorted(os.listdir(HERO)):
        if not datei.endswith('.webp') or datei.endswith('-unscharf.webp'):
            continue
        quelle = os.path.join(HERO, datei)
        ziel = os.path.join(ZIEL, 'hero', datei.replace('.webp', f'-{HERO_BREITE}.webp'))
        bild = Image.open(quelle)
        if bild.width <= HERO_BREITE or aktuell(quelle, ziel):
            continue
        speichern(bild.convert('RGB'), HERO_BREITE, ziel, HERO_QUALITAET)
        neu += 1
        print(f'hero/{datei}: Handy-Fassung')

    print(f'Fertig: {neu} neu erzeugt, {uebersprungen} waren schon aktuell.')


if __name__ == '__main__':
    sys.exit(main())
