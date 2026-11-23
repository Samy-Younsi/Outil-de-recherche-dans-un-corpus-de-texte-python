"""Module stats : statistiques par document, score de pertinence et classement.

Partie de Nawel SKENDRAOUI : F10 (statistiques), F11 (score et classement).
"""

import doctest
from collections import Counter

# Valeurs utilisées quand les options ne précisent pas les réglages du score (F11)
DEFAUTS_SCORE = {"mode": "ET", "coef_criteres": 0.6, "coef_densite": 0.4, "plafond_densite": 20}


def intervalles_fusionnes(positions):
    """Renvoie un à un les intervalles (debut, fin), triés et sans recouvrement (F10).
    C'est une fonction génératrice : chaque intervalle est produit avec yield.
    Deux occurrences qui se recouvrent ou se touchent forment un seul intervalle.
    >>> list(intervalles_fusionnes([(10, 16), (0, 6), (3, 9)]))
    [(0, 9), (10, 16)]
    >>> list(intervalles_fusionnes([]))
    []
    """
    courant = None
    for debut, fin in sorted(positions):
        if courant is None:
            courant = (debut, fin)
        elif debut <= courant[1]:          # recouvrement : on agrandit l'intervalle courant
            courant = (courant[0], max(courant[1], fin))
        else:
            yield courant
            courant = (debut, fin)
    if courant is not None:
        yield courant


def proportion_couverte(positions, longueur):
    """Renvoie la part du texte couverte par au moins une occurrence, entre 0 et 1 (F10).
    Un caractère couvert par deux occurrences n'est compté qu'une fois.
    Un texte vide donne 0.0, sans division par zéro.
    >>> proportion_couverte([(0, 6), (3, 9)], 20)      # de 0 à 9 : 9 caractères sur 20
    0.45
    >>> proportion_couverte([], 0)
    0.0
    """
    if longueur == 0:
        return 0.0
    couverts = sum(fin - debut for debut, fin in intervalles_fusionnes(positions))
    return couverts / longueur


def calculer_stats(chemin, texte, resultats, criteres=None, options=None):
    """Renvoie le dictionnaire des statistiques d'un document (F10).
    - resultats : le dict {motif: [(debut, fin), ...]} renvoyé par appliquer_criteres (Samy) ;
    - criteres : la liste des critères, au format de charger_config (Aya), pour le poids
      et l'exclusion (SAUF) de chaque motif ; None = poids 1 et pas d'exclusion ;
    - options : le dict config["options"] ; on y lit le mode ET ou OU (F9).
    Les clés du dictionnaire renvoyé sont aussi les colonnes du CSV (F12).

    >>> s = calculer_stats("cours.txt", "python et python 2026", {"python": [(0, 6), (10, 16)], "java": []})
    >>> s["occ_python"], s["occ_java"], s["criteres_ok"], s["criteres_total"], s["retenu"]
    (2, 0, 1, 2, False)
    >>> calculer_stats("cours.txt", "python", {"python": [(0, 6)], "java": []}, options={"mode": "OU"})["retenu"]
    True
    >>> criteres = [{"type": "mot", "motif": "python", "poids": 1, "exclu": False},
    ...             {"type": "mot", "motif": "java", "poids": 1, "exclu": True}]
    >>> calculer_stats("cours.txt", "python java", {"python": [(0, 6)], "java": [(7, 11)]}, criteres)["retenu"]
    False
    >>> calculer_stats("vide.txt", "", {"python": []})["densite"]
    0.0
    >>> calculer_stats("cours.txt", "python", {"python": [(0, 6)]}, options={"mode": "XOR"})
    Traceback (most recent call last):
    ...
    ValueError: Mode inconnu : XOR (ET ou OU attendu)
    """
    options = options or {}
    mode = options.get("mode", DEFAUTS_SCORE["mode"])
    if mode not in ("ET", "OU"):
        raise ValueError(f"Mode inconnu : {mode} (ET ou OU attendu)")
    if criteres is None:
        criteres = [{"motif": motif} for motif in resultats]

    poids = {critere["motif"]: critere.get("poids", 1) for critere in criteres}
    exclus = {critere["motif"] for critere in criteres if critere.get("exclu", False)}

    # Counter est un dict qui compte : il renvoie 0 pour un motif absent
    occurrences = Counter({motif: len(positions) for motif, positions in resultats.items()})
    nb_mots = len(texte.split())

    stats = {"fichier": str(chemin), "nb_mots": nb_mots}
    for motif in resultats:
        stats[f"occ_{motif}"] = occurrences[motif]

    # les critères SAUF ne comptent pas dans les statistiques, ils servent seulement à écarter
    normaux = [motif for motif in resultats if motif not in exclus]
    satisfaits = [motif for motif in normaux if occurrences[motif] > 0]
    total = sum(occurrences[motif] for motif in normaux)
    toutes_positions = [position for motif in normaux for position in resultats[motif]]

    stats["occurrences"] = total
    stats["proportion"] = round(proportion_couverte(toutes_positions, len(texte)), 4)
    stats["densite"] = round(total * 1000 / nb_mots, 2) if nb_mots else 0.0     # pour 1000 mots
    stats["criteres_ok"] = len(satisfaits)
    stats["criteres_total"] = len(normaux)

    # part pondérée : un critère de poids 2 compte double (F11)
    if poids_total := sum(poids.get(motif, 1) for motif in normaux):
        stats["part_ponderee"] = round(sum(poids.get(motif, 1) for motif in satisfaits) / poids_total, 4)
    else:
        stats["part_ponderee"] = 0.0

    # F9 : un critère SAUF trouvé écarte le document, quel que soit le mode
    if any(occurrences[motif] > 0 for motif in exclus):
        stats["retenu"] = False
    elif mode == "ET":
        stats["retenu"] = len(normaux) > 0 and len(satisfaits) == len(normaux)
    else:
        stats["retenu"] = len(satisfaits) > 0

    stats["score"] = calculer_score(stats, options)
    return stats


def calculer_score(stats, options=None):
    """Renvoie le score de pertinence d'un document, entre 0 et 100 (F11).
    score = 100 × (coef_criteres × part pondérée + coef_densite × min(1, densité / plafond))
    Les réglages sont lus dans options (fichier TOML), sinon dans DEFAUTS_SCORE.
    Le plafond empêche un document qui répète un seul mot de passer devant
    un document qui satisfait tous les critères.
    >>> calculer_score({"part_ponderee": 1.0, "densite": 40})
    100.0
    >>> calculer_score({"part_ponderee": 0.5, "densite": 10})
    50.0
    >>> calculer_score({"part_ponderee": 1.0, "densite": 0}, {"coef_criteres": 1, "coef_densite": 0})
    100.0
    """
    reglages = dict(DEFAUTS_SCORE)
    reglages.update(options or {})        # les options écrasent les valeurs par défaut
    plafond = reglages["plafond_densite"]
    part_densite = min(1, stats["densite"] / plafond) if plafond > 0 else 0
    score = reglages["coef_criteres"] * stats["part_ponderee"] + reglages["coef_densite"] * part_densite
    return round(100 * score, 1)


def cle_de_tri(stats):
    """Renvoie la clé du classement (F11) : score décroissant, puis occurrences
    décroissantes, puis nom du fichier, pour un ordre toujours identique.
    sorted compare les tuples élément par élément.
    """
    return (-stats["score"], -stats["occurrences"], stats["fichier"])


def classer(liste_stats, tous=False):
    """Renvoie les documents triés du meilleur au moins bon (F11).
    Seuls les documents retenus sont gardés, sauf si tous vaut True (option --tous, F12).
    >>> docs = [{"fichier": "b", "score": 50, "occurrences": 2, "retenu": True},
    ...         {"fichier": "a", "score": 50, "occurrences": 2, "retenu": True},
    ...         {"fichier": "c", "score": 90, "occurrences": 1, "retenu": False}]
    >>> [d["fichier"] for d in classer(docs)]
    ['a', 'b']
    >>> [d["fichier"] for d in classer(docs, tous=True)]
    ['c', 'a', 'b']
    """
    gardes = [stats for stats in liste_stats if tous or stats["retenu"]]
    return sorted(gardes, key=cle_de_tri)


if __name__ == "__main__":
    doctest.testmod()
