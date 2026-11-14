
"""Module corpus : trouver les fichiers à analyser et lire leur contenu.

Partie d'Aya BEN-TCHICHIA (fonctionnalités #1, #2, #3, #4 et #15).
"""

from pathlib import Path


def corpus_depuis_repertoire(dossier, recursif=False):
    """Renvoie la liste triée des fichiers d'un dossier (#1).
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
    """Renvoie la liste des fichiers écrits dans fichier_liste, un chemin par ligne (#2).
    Les lignes vides sont ignorées.
    """
    pass


def filtrer(fichiers, extensions=None, motif_nom=None, dossier=None):
    """Garde seulement les fichiers qui respectent les filtres (#3).
    extensions : liste comme [".txt"], motif_nom : motif comme "rapport_*",
    dossier : nom d'un dossier. None veut dire pas de filtre.
    """
    pass


def lire_fichier(chemin):
    """Renvoie le texte du fichier (#4).
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


def charger_config(fichier_ini):
    """Lit un fichier .ini qui décrit une recherche et renvoie un dict (#15)."""
    pass


if __name__ == "__main__":
    print(corpus_depuis_repertoire("exemples"))
    print(corpus_depuis_repertoire("exemples", recursif=True))
    print(lire_fichier("exemples/latin1.txt"))