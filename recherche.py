"""Module recherche : trouver les motifs dans le texte d'un document.

Partie de Samy YOUNSI (fonctionnalités F6, F7, F8 et F9).
"""

import re
import unicodedata
from pathlib import Path


def normaliser(texte, ignorer_casse=False, sans_accents=False):
    """Met le texte en minuscules et/ou enlève les accents.
    Le texte garde la même longueur.
    >>> normaliser("Évry Café", ignorer_casse=True, sans_accents=True)
    'evry cafe'
    >>> normaliser("Évry Café")
    'Évry Café'
    """
    lettres = []
    for lettre in texte:
        if sans_accents:
            lettre = unicodedata.normalize("NFD", lettre)[0]
        if ignorer_casse:
            lettre = lettre.lower()[0]
        lettres.append(lettre)
    return "".join(lettres)


def chercher_chaine(texte, mot, ignorer_casse=False, sans_accents=False, mot_entier=False):
    """Renvoie la liste des positions du mot dans le texte (F6).
    >>> chercher_chaine("Le Café du café", "cafe", ignorer_casse=True, sans_accents=True)
    [(3, 7), (11, 15)]
    >>> chercher_chaine("python et pythonique", "python", mot_entier=True)
    [(0, 6)]
    >>> chercher_chaine("python", "Python")
    []
    """
    if mot == "":
        return []

    texte = normaliser(texte, ignorer_casse, sans_accents)
    mot = normaliser(mot, ignorer_casse, sans_accents)
    motif = re.escape(mot)
    if mot_entier:
        motif = r"\b" + motif + r"\b"

    positions = []
    for match in re.compile(motif).finditer(texte):
        positions.append(match.span())
    return positions


def chercher_regex(texte, motif, ignorer_casse=False):
    """Renvoie la liste des positions de l'expression régulière (F7).
    >>> chercher_regex("Né en 1998 et 2004", r"\\d{4}")
    [(6, 10), (14, 18)]
    >>> chercher_regex("Python python", "PYTHON", ignorer_casse=True)
    [(0, 6), (7, 13)]
    >>> chercher_regex("bbb", "a*")
    []
    >>> chercher_regex("abc", "(")
    Traceback (most recent call last):
    ...
    ValueError: expression régulière invalide : (
    """
    try:
        if ignorer_casse:
            regex = re.compile(motif, re.IGNORECASE)
        else:
            regex = re.compile(motif)
    except re.error:
        raise ValueError(f"expression régulière invalide : {motif}")

    positions = []
    for match in regex.finditer(texte):
        # une correspondance vide ne compte pas
        if match.group() != "":
            positions.append(match.span())
    return positions


def chercher_dans_nom(chemin, motif, regex=False, ignorer_casse=False):
    """Dit si le nom du fichier, sans son dossier, contient le motif (F8).
    >>> chercher_dans_nom("exemples/Rapport_2024.txt", "rapport", ignorer_casse=True)
    True
    >>> chercher_dans_nom("exemples/cours.txt", "exemples")
    False
    >>> chercher_dans_nom("exemples/rapport_2024.txt", r"_\\d{4}", regex=True)
    True
    """
    nom = Path(chemin).name
    if regex:
        return chercher_regex(nom, motif, ignorer_casse) != []
    return normaliser(motif, ignorer_casse) in normaliser(nom, ignorer_casse)


def appliquer_criteres(texte, chemin, criteres, options):
    """Cherche chaque critère dans le texte et renvoie {motif: positions} (F9).
    Pour l'instant seul le type "mot" est géré.
    >>> criteres = [{"type": "mot", "motif": "python", "poids": 1, "exclu": False}]
    >>> appliquer_criteres("Python, python !", "cours.txt", criteres, {"ignorer_casse": True})
    {'python': [(0, 6), (8, 14)]}
    """
    resultats = {}
    for critere in criteres:
        motif = critere["motif"]
        if critere["type"] == "mot":
            resultats[motif] = chercher_chaine(
                texte,
                motif,
                ignorer_casse=options.get("ignorer_casse", False),
                sans_accents=options.get("sans_accents", False),
                mot_entier=options.get("mot_entier", False),
            )
        # regex et nom : prochaine étape
    return resultats


if __name__ == "__main__":
    texte = "Python est un langage. On apprend le python et le Café à Évry en 2026."
    criteres = [
        {"type": "mot", "motif": "python", "poids": 2, "exclu": False},
        {"type": "mot", "motif": "cafe", "poids": 1, "exclu": False},
    ]
    options = {"ignorer_casse": True, "sans_accents": True, "mot_entier": True}
    print(appliquer_criteres(texte, "exemple.txt", criteres, options))
    print(chercher_regex(texte, r"\d{4}"))
    print(chercher_dans_nom("exemples/exemple.txt", "exemple"))
