"""Module stats : statistiques par fichier, score et classement.

Partie de Nawel SKENDRAOUI (fonctionnalités #9 et #10).
"""


def calculer_stats(chemin, texte, resultats, mode="ET"):
    """Renvoie un dict avec les statistiques d'un fichier (#9).
    resultats vient de appliquer_criteres : {motif: [(debut, fin), ...]}.
    Pour l'instant : nom du fichier et nombre d'occurrences par motif.
    >>> calculer_stats("cours.txt", "python python", {"python": [(0, 6), (7, 13)]})
    {'fichier': 'cours.txt', 'occ_python': 2}
    """
    stats = {"fichier": str(chemin)}
    for motif, positions in resultats.items():
        stats["occ_" + motif] = len(positions)
    # à faire : proportion, criteres_ok, criteres_total, retenu (ET/OU)
    return stats


def calculer_score(stats):
    """Renvoie un score entre 0 et 100 pour un fichier (#10).
    La formule sera expliquée dans le README.
    """
    pass


def classer(liste_stats):
    """Garde les fichiers retenus et les trie du meilleur au moins bon score (#10).
    Pour l'instant, renvoie la liste telle quelle.
    """
    return liste_stats


if __name__ == "__main__":
    print(calculer_stats("exemples/cours.txt", "python python 2026",
                         {"python": [(0, 6), (7, 13)]}))
