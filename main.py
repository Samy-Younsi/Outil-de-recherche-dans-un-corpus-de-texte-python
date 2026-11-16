"""Point d'entrée du programme : python main.py dossier --mot python -o resultats.csv

Partie de Nawel SKENDRAOUI (fonctionnalité #12).
Relie corpus.py (Aya), recherche.py (Samy), stats.py et export.py (Nawel).
"""

import argparse

from corpus import corpus_depuis_repertoire, lire_fichier
from recherche import appliquer_criteres
from stats import calculer_stats, classer
from export import exporter_csv


def lire_arguments():
    """Définit les options de la ligne de commande et les renvoie (#12)."""
    parser = argparse.ArgumentParser(description="Recherche dans un corpus de texte")
    parser.add_argument("dossier", help="dossier à analyser")
    parser.add_argument("-r", "--recursif", action="store_true",
                        help="parcourir aussi les sous-dossiers")
    parser.add_argument("--mot", action="append", default=[],
                        help="mot à chercher (option répétable)")
    parser.add_argument("-o", "--sortie", default="resultats.csv",
                        help="fichier CSV de sortie")
    # à faire : --regex, --nom, --ext, --liste, --mode, -i, --contexte, --config
    return parser.parse_args()


def main():
    args = lire_arguments()

    # un critère par mot donné avec --mot
    criteres = [{"type": "mot", "motif": m, "poids": 1, "exclu": False} for m in args.mot]
    options = {}

    fichiers = corpus_depuis_repertoire(args.dossier, args.recursif)   # Aya
    tous_les_resultats = []
    for chemin in fichiers:
        texte = lire_fichier(chemin)                                    # Aya
        resultats = appliquer_criteres(texte, chemin, criteres, options)  # Samy
        stats = calculer_stats(chemin, texte, resultats)                # Nawel
        tous_les_resultats.append(stats)

    classement = classer(tous_les_resultats)                            # Nawel
    exporter_csv(classement, args.sortie)                               # Nawel
    print(len(classement), "fichier(s) écrit(s) dans", args.sortie)


if __name__ == "__main__":
    main()
