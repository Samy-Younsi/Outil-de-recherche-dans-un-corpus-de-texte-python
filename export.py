"""Module export : écriture des résultats dans un fichier CSV.

Partie de Nawel SKENDRAOUI (fonctionnalité #11).
"""

import csv


def exporter_csv(liste_stats, fichier_sortie):
    """Écrit un fichier CSV avec une ligne par fichier analysé (#11).
    Les colonnes sont les clés du premier dict de liste_stats.
    """
    if not liste_stats:
        print("Aucun résultat à exporter.")
        return
    colonnes = list(liste_stats[0].keys())
    with open(fichier_sortie, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(liste_stats)


if __name__ == "__main__":
    exemple = [{"fichier": "exemples/cours.txt", "occ_python": 2}]
    exporter_csv(exemple, "test.csv")
    print(open("test.csv", encoding="utf-8").read())
