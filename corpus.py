
"""Module corpus : constituer le corpus, le filtrer et lire les documents.

Partie d'Aya BEN-TCHICHIA : F2 (lecture du TOML), F3, F4, F5, F13.
"""

import sys
from pathlib import Path


def corpus_depuis_repertoire(dossier, recursif=False):
    """Renvoie la liste triée des fichiers d'un dossier (F3).
    Si recursif vaut True, on parcourt aussi les sous-dossiers.
    """
    fichiers = []
    for child in Path(dossier).iterdir():
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
    """
    pass


def lire_fichier(chemin):
    """Renvoie le texte du fichier (F3).
    Essaie l'UTF-8, puis le latin-1 en cas d'erreur d'encodage.
    Renvoie "" si le fichier est illisible.
    >>> lire_fichier("exemples/latin1.txt")
    'Café à Évry, cours de python.'
    >>> lire_fichier("exemples/existe_pas.txt")
    ''
    """
    try:
        return Path(chemin).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return Path(chemin).read_text(encoding="latin-1")
    except OSError:
        return ""


def charger_config(fichier_toml):
    """Lit le fichier TOML qui décrit une recherche et renvoie le dictionnaire config (F2)."""
    pass


if __name__ == "__main__":
    print(corpus_depuis_repertoire("exemples", recursif=True))
    print(corpus_depuis_liste("exemples/liste.txt"))
    print(lire_fichier("exemples/latin1.txt"))