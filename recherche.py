"""Module recherche : trouver les motifs dans le texte d'un document.

Partie de Samy YOUNSI (fonctionnalités F6 et F9).
"""

import re
import unicodedata


def normaliser(texte, ignorer_casse=False, sans_accents=False):
    """Met le texte en minuscules et/ou enlève les accents.
    Le texte garde la même longueur, sinon les positions seraient fausses.
    >>> normaliser("Évry Café", ignorer_casse=True, sans_accents=True)
    'evry cafe'
    >>> normaliser("Évry Café")
    'Évry Café'
    """
    lettres = []
    for lettre in texte:
        if sans_accents:
            # é devient e + accent, on garde juste le e
            lettre = unicodedata.normalize("NFD", lettre)[0]
        if ignorer_casse:
            lettre = lettre.lower()[0]
        lettres.append(lettre)
    return "".join(lettres)


def chercher_chaine(texte, mot, ignorer_casse=False, sans_accents=False, mot_entier=False):
    """Renvoie la liste des positions (debut, fin) du mot dans le texte (F6).
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

    # le mot est cherché tel quel, un point reste un point
    motif = re.escape(mot)
    if mot_entier:
        motif = r"\b" + motif + r"\b"

    positions = []
    for match in re.compile(motif).finditer(texte):
        positions.append(match.span())
    return positions


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
    texte = "Python est un langage. On apprend le python et le Café à Évry."
    criteres = [
        {"type": "mot", "motif": "python", "poids": 2, "exclu": False},
        {"type": "mot", "motif": "cafe", "poids": 1, "exclu": False},
    ]
    options = {"ignorer_casse": True, "sans_accents": True, "mot_entier": True}
    print(appliquer_criteres(texte, "exemple.txt", criteres, options))
