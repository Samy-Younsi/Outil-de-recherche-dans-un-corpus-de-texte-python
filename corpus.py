
"""Module corpus : constituer le corpus, le filtrer et lire les documents.

Partie d'Aya BEN-TCHICHIA : F2 (lecture du TOML), F3, F4, F5, F13.
"""

import sys
import tomllib
import re
import doctest
from pathlib import Path

#Bibliotheque externes pour lire les PDF et les Word(F13)
#si elles ne sont pas installées, ca marche quand meme car les .pdf et .docx sont ignorés avec un avertissement
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
try: 
    from docx import Document
except ImportError:
    Document = None


def corpus_depuis_repertoire(dossier, recursif=False):
    """Renvoie la liste triée des fichiers d'un dossier (F3).
    Si recursif vaut True, on parcourt aussi les sous-dossiers.
    Un dossier qu'on n'a pas le droit de lire est ignoré avec un avertissement.
    """
    fichiers = []
    try:
        contenu = list(Path(dossier).iterdir())
    except PermissionError:
        print(f"Attention : {dossier} est inaccessible, il est ignoré", file=sys.stderr)
        return []
    for child in contenu:
        if child.is_file():
            fichiers.append(child)
        elif child.is_dir() and recursif:
            fichiers.extend(corpus_depuis_repertoire(child, recursif=True))
    return sorted(fichiers)


def corpus_depuis_liste(fichier_liste):
    """Renvoie la liste des fichiers écrits dans fichier_liste, un chemin par ligne (F4).
    - les lignes vides et celles qui commencent par # sont ignorées ;
    - un chemin relatif part du dossier du fichier de liste ;
    - un chemin qui n'existe pas est signalé par un avertissement ;
    - les doublons sont retirés.
    >>> [p.name for p in corpus_depuis_liste("exemples/liste.txt")]
    ['cours.txt', 'notes.txt', 'accents.txt']
    """
    dossier = Path(fichier_liste).parent
    fichiers = []
    with open(fichier_liste, encoding="utf-8") as infile:
        for line in (l.rstrip() for l in infile):
            if not line or line.startswith("#"):
                continue
            chemin = dossier / line
            if not chemin.is_file():
                print(f"Attention : {chemin} n'existe pas, il est ignoré", file=sys.stderr)
                continue
            if chemin not in fichiers:
                fichiers.append(chemin)
    return fichiers


def filtrer(fichiers, extensions=None, motif_nom=None, regex_nom=None, exclure_dossiers=None):
    """Garde seulement les fichiers qui passent tous les filtres (F5).
    extensions : liste comme [".txt"], sans tenir compte de la casse ;
    motif_nom : motif glob comme "rapport_*" ; regex_nom : expression régulière ;
    exclure_dossiers : noms de dossiers à écarter. None veut dire pas de filtre.

    >>> fichiers=corpus_depuis_repertoire("exemples", recursif=True)    # on prend tous les fichiers du dossier exemples et de ses sous-dossiers
    >>> [p.name for p in filtrer(fichiers, extensions=[".MD"])]
    ['image.md']
    >>> [p.name for p in filtrer(fichiers, motif_nom="rapport_*")]        # on ne garde que les fichiers dont le nom commence par "rapport_"
    ['rapport_2025.txt']
    >>> [p.name for p in filtrer(fichiers, regex_nom="[0-9]{4}")]          #on  ne garde que les fichiers dont le nom contient 4 chiffres consécutifs
    ['rapport_2025.txt']
    >>> [p.name for p in filtrer(fichiers, extensions=[".txt"], exclure_dossiers=["sous_dossier"])]
    ['accents.txt', 'cours.txt', 'latin1.txt', 'liste.txt', 'rapport_2025.txt', 'vide.txt']
    >>> len(filtrer(fichiers)) == len(fichiers)         
    True
    """
    gardes=[]
    if extensions is not None:
        extensions = [ext.lower() for ext in extensions]      # on met en minuscule pour ignorer la casse
    for chemin in fichiers:
        chemin = Path(chemin)     # on convertit en Path pour pouvoir utiliser .suffix et .name
        #filtre par extension 
        if extensions is not None and chemin.suffix.lower() not in extensions:      #on ignore la casse pour les extensions
            continue
        #filtre par motif glob
        if motif_nom is not None and not chemin.match(motif_nom):            #on utilise la méthode match de Path pour les motifs glob
            continue
        #filtre par regex
        if regex_nom is not None and not re.search(regex_nom, chemin.name):       #on utilise re.search pour les regex
            continue
        #filtre par dossier à exclure
        if exclure_dossiers:
            dans_un_dossier_exclu = False     #on verifie si le fichier est dans un dossier a exclure
            for dossier in chemin.parent.parts:
                if dossier in exclure_dossiers:
                    dans_un_dossier_exclu = True
            if dans_un_dossier_exclu:
                continue
        gardes.append(chemin)     # on garde le fichier par défaut
    return gardes 


def lire_fichier(chemin):
    """Renvoie le texte du fichier (F3, F13).
    .pdf : texte des pages avec pypdf ; .docx : paragraphes et tableaux avec python-docx ;
    autres fichiers : UTF-8, puis latin-1 en cas d'erreur d'encodage.
    Renvoie "" si le fichier est illisible.
    >>> lire_fichier("exemples/latin1.txt")
    'Café à Évry, cours de python.'
    >>> lire_fichier("exemples/existe_pas.txt")
    ''
    >>> "python" in lire_fichier("exemples/cours.docx")
    True
    >>> "python" in lire_fichier("exemples/cours.pdf")
    True
    >>> lire_fichier("exemples/scan.pdf")
    ''
    """
    chemin = Path(chemin)
    extension = chemin.suffix.lower()
    # 1. les PDF
    if extension == ".pdf":
        if PdfReader is None:
            print(f"Attention : {chemin} ignoré, pypdf n'est pas installé", file=sys.stderr)
            return ""
        try:
            texte = lire_pdf(chemin)
        except Exception:
            print(f"Attention : {chemin} est illisible, il est ignoré", file=sys.stderr)
            return ""
        if texte == "":
            print(f"Attention : {chemin} ne contient pas de texte (PDF scanné ?), il est compté comme illisible", file=sys.stderr)
        return texte
    # 2. les Word
    if extension == ".docx":
        if Document is None:
            print(f"Attention : {chemin} ignoré, python-docx n'est pas installé", file=sys.stderr)
            return ""
        try:
            return lire_docx(chemin)
        except Exception:
            print(f"Attention : {chemin} est illisible, il est ignoré", file=sys.stderr)
            return ""
    # 3. les fichiers texte
    try:
        return chemin.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return chemin.read_text(encoding="latin-1")
    except OSError:
        return ""



def lire_pdf(chemin):
    """Renvoie le texte de toutes les pages d'un PDF (F13).

    >>> "python" in lire_pdf("exemples/cours.pdf")
    True
    >>> lire_pdf("exemples/scan.pdf")
    ''
    """
    if PdfReader is None:
        raise ImportError("pypdf n'est pas installé")
    lecteur = PdfReader(chemin)
    textes = []
    for page in lecteur.pages:
        textes.append(page.extract_text() or "")
    return "\n".join(textes).strip()


def lire_docx(chemin):
    """Renvoie le texte d'un document Word : paragraphes puis tableaux (F13).

    >>> texte = lire_docx("exemples/cours.docx")
    >>> "python" in texte
    True
    >>> "langage" in texte
    True
    """
    if Document is None:
        raise ImportError("python-docx n'est pas installé")
    document = Document(chemin)
    textes = []
    for paragraphe in document.paragraphs:
        textes.append(paragraphe.text)
    for tableau in document.tables:
        for ligne in tableau.rows:
            for case in ligne.cells:
                textes.append(case.text)
    return "\n".join(textes)


# Valeurs utilisées quand le fichier TOML ne précise pas une clé (F2)
DEFAUTS = {
    "corpus": {"dossier": None, "liste": None, "recursif": False,
            "extensions": None, "motif_nom": None, "regex_nom": None,
            "exclure_dossiers": []},
    "options": {"mode": "ET", "ignorer_casse": True, "sans_accents": False,
                "mot_entier": False, "approx": 0, "sortie": "resultats.csv",
                "coef_criteres": 0.6, "coef_densite": 0.4, "plafond_densite": 20},
}
DEFAUT_CRITERE = {"poids": 1, "exclu": False}
CLES_CRITERE = ["type", "motif", "poids", "exclu"]
TYPES = {
    "corpus": {"dossier": str, "liste": str, "recursif": bool,
            "extensions": list, "motif_nom": str, "regex_nom": str,
            "exclure_dossiers": list},
    "options": {"mode": str, "ignorer_casse": bool, "sans_accents": bool,
                "mot_entier": bool, "approx": int, "sortie": str,
                "coef_criteres": float, "coef_densite": float, "plafond_densite": int},
}


def charger_config(fichier_toml):
    """Lit un fichier de configuration TOML et renvoie le dictionnaire config (F2).
    Les clés absentes du fichier prennent leur valeur par défaut.
    >>> config = charger_config("exemples/recherche.toml")
    >>> config["corpus"]["recursif"]
    True
    >>> config["criteres"][0]
    {'poids': 2, 'exclu': False, 'type': 'mot', 'motif': 'python'}
    >>> config["options"]["approx"]
    0
    >>> charger_config("exemples/erreur.toml")
    Traceback (most recent call last):
    ...
    ValueError: Clé inconnue dans [corpus] : recursf
    >>> charger_config("exemples/mauvais_type.toml")
    Traceback (most recent call last):
    ...
    ValueError: Mauvais type pour recursif dans [corpus] : bool attendu
    """
    with open(fichier_toml, "rb") as infile:
        lu = tomllib.load(infile)

    config = {}
    for partie in ["corpus", "options"]:
        section = lu.get(partie, {})
        for cle in section:
            if cle not in DEFAUTS[partie]:
                raise ValueError(f"Clé inconnue dans [{partie}] : {cle}")
            if not isinstance(section[cle], TYPES[partie][cle]):
                raise ValueError(f"Mauvais type pour {cle} dans [{partie}] : {TYPES[partie][cle].__name__} attendu")
        config[partie] = dict(DEFAUTS[partie])
        config[partie].update(section)  # le fichier écrase les défauts

    config["criteres"] = []
    for critere in lu.get("criteres", []):
        for cle in critere:
            if cle not in CLES_CRITERE:
                raise ValueError(f"Clé inconnue dans [[criteres]] : {cle}")
        complet = dict(DEFAUT_CRITERE)
        complet.update(critere)
        config["criteres"].append(complet)
    return config


if __name__ == "__main__":
    doctest.testmod()