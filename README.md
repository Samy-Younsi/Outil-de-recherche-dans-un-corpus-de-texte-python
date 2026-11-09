# Outil de recherche dans un corpus de texte

Projet Langages de scripts, L3 SR, Université d'Évry, 2026-2027.

**Groupe : TrioLogic**

| Nom | Prénom |
|---|---|
| YOUNSI | Samy |
| BEN-TCHICHIA | Aya |
| SKENDRAOUI | Nawel |

Les informations du groupe sont aussi dans le fichier [`groupe.csv`](groupe.csv).

## Présentation

Notre outil effectue des recherches dans un ensemble de documents texte (`.txt`). Il cherche des motifs (chaînes simples ou expressions régulières) dans le contenu des fichiers et dans leurs noms. Pour chaque fichier, il calcule des statistiques et un score de pertinence, puis il exporte le classement des fichiers dans un fichier CSV.

Exemple d'utilisation envisagé :

```
python recherche.py mes_textes/ -r --mot "python" --regex "\d{4}" --ext .txt -o resultats.csv
```

## Partie 1 : fonctionnalités

### Noyau minimal

1. **Corpus par répertoire** : tous les fichiers d'un répertoire, avec une option pour inclure les sous-répertoires.
2. **Corpus par fichier de liste** : un fichier qui contient les chemins des documents à analyser.
3. **Filtres** sur le nom, l'extension ou l'emplacement des fichiers.
   * dépend de #1 et #2
4. **Lecture du contenu** des fichiers, avec gestion des problèmes d'encodage.
   * dépend de #3
5. **Recherche d'une chaîne simple** dans le contenu.
   * dépend de #4
6. **Recherche par expression régulière** dans le contenu.
   * dépend de #4
7. **Recherche dans les noms de fichiers** (chaîne simple ou expression régulière).
   * dépend de #3
8. **Combinaison de plusieurs critères** de recherche (ET / OU).
   * dépend de #5, #6 et #7
9. **Statistiques par fichier** :
   * nombre d'occurrences de chaque motif
   * proportion du contenu qui correspond aux motifs
   * nombre de critères satisfaits
   * dépend de #8
10. **Score de pertinence** calculé à partir des statistiques, et tri des fichiers selon ce score.
    * dépend de #9
11. **Export des résultats** dans un fichier CSV.
    * dépend de #10
12. **Interface en ligne de commande** : options, valeurs par défaut, message d'aide.
    * relie toutes les fonctionnalités précédentes

### Fonctionnalités supplémentaires

13. **Recherche insensible à la casse et aux accents** (« Évry » trouve « evry »).
    * modifier #5 et #6 pour normaliser le texte et le motif
14. **Affichage d'un extrait** du texte autour de chaque résultat, comme `grep`.
    * modifier #5 et #6 pour mémoriser la position de chaque résultat
15. **Fichier de configuration** `.ini` qui enregistre une recherche pour la réutiliser.
    * modifier #12 pour lire les critères dans le fichier

### Priorités

1. **Étape 1** : #1, #4, #5, #9, #11 et #12. On obtient un outil qui fonctionne de bout en bout : un répertoire, un mot recherché, des statistiques et un CSV.
2. **Étape 2** : #2, #3, #6, #7, #8 et #10, pour compléter le noyau minimal.
3. **Étape 3** : les fonctionnalités supplémentaires choisies.

## Partie 2 : briques logicielles

### Correspondance entre fonctionnalités et modules

| Fonctionnalité | Brique logicielle | Type |
|---|---|---|
| #1, #3, #7 parcours de répertoire, filtres, noms de fichiers | `pathlib` | standard |
| #3 filtres avec motifs `*` et `?` | `fnmatch` | standard |
| #2 lecture du fichier de liste | `pathlib` | standard |
| #4 lecture et encodage | `pathlib` / `open`, éventuellement `charset-normalizer` | standard / tiers |
| #5 recherche de chaîne simple | méthodes de `str` (`in`, `count`) | intégré |
| #6, #7, #8 expressions régulières et combinaison | `re` | standard |
| #13 casse et accents | `re` (option `IGNORECASE`), `unicodedata` | standard |
| #9, #10 statistiques, score, tri | `len`, `sum`, `sorted` | intégré |
| #11 export CSV | `csv` | standard |
| #12 ligne de commande | `argparse` | standard |
| #15 fichier de configuration | `configparser` | standard |

### Modules de la bibliothèque standard

Les critères suivants sont communs à tous les modules standard utilisés (`pathlib`, `fnmatch`, `re`, `unicodedata`, `csv`, `argparse`, `configparser`) :

* **installation** : aucune, ils sont fournis avec Python ;
* **compatibilité** : Windows, Linux et macOS, avec toutes les versions récentes de Python 3 ;
* **maintenance et communauté** : maintenus par l'équipe de développement de Python, très largement utilisés ;
* **documentation** : complète, avec des exemples, sur [docs.python.org](https://docs.python.org/3/library/).

| Module | Service rendu | Limites | Facilité d'utilisation |
|---|---|---|---|
| `pathlib` | Représenter des chemins, lister un répertoire (`iterdir`, `rglob` pour les sous-répertoires), obtenir le nom, l'extension et la taille d'un fichier, lire un fichier (`read_text`) | Ne détecte pas l'encodage d'un fichier | Simple, syntaxe orientée objet |
| `fnmatch` | Filtrer des noms de fichiers avec des motifs `*` et `?` | Moins expressif qu'une expression régulière | Très simple |
| `re` | Rechercher et compter des motifs (`finditer`, `findall`), option `IGNORECASE` | Ne traite pas les accents ; les expressions complexes deviennent difficiles à lire et peuvent être lentes | Moyenne : la syntaxe des expressions régulières demande de l'entraînement |
| `unicodedata` | Supprimer les accents (normalisation NFD) | Doit être appliqué au texte et au motif | Simple une fois la fonction écrite |
| `csv` | Écrire le fichier de résultats (`DictWriter`) | Aucun calcul : les statistiques sont faites par notre code | Simple |
| `argparse` | Définir les options, lire les paramètres, générer le message d'aide | Déclaration un peu longue | Moyenne |
| `configparser` | Lire et écrire des fichiers `.ini` | Toutes les valeurs sont lues comme du texte, il faut les convertir | Simple |

### Modules tiers

Installation avec `pip` dans un environnement virtuel (`venv` ou `uv`).

| Critère | `tqdm` | `charset-normalizer` | `pandas` |
|---|---|---|---|
| Service rendu | Barre de progression pendant l'analyse | Détecter l'encodage d'un fichier | Manipuler des tableaux, trier, exporter en CSV |
| Limites | Uniquement visuel | Peut se tromper sur les fichiers très courts | Beaucoup plus que nécessaire pour notre besoin |
| Installation | `pip install tqdm`, légère | `pip install charset-normalizer`, légère | Lourde (installe aussi `numpy`) |
| Facilité d'utilisation | Très simple : `for f in tqdm(fichiers)` | Simple | Demande un apprentissage |
| Compatibilité | Tous systèmes | Tous systèmes | Tous systèmes |
| Maintenance et communauté | Active, très utilisé | Active, utilisé notamment par `requests` | Très active, très grande communauté |
| Documentation | Bonne | Correcte | Très complète |
| **Décision** | **Non retenu pour l'instant** : pourra être ajouté si l'analyse des gros corpus est lente | **En réserve**, si des fichiers posent des problèmes d'encodage | **Écarté** : le module `csv` suffit |

### Outils indépendants

| Outil | Service rendu | Limites | Décision |
|---|---|---|---|
| `grep` (appelé avec `subprocess`) | Recherche très rapide de motifs dans des fichiers | Absent par défaut sous Windows ; ne calcule pas nos statistiques ; syntaxe des expressions régulières différente de celle de Python | **Écarté** |

Si, pendant le développement, un module ne convient pas, nous le remplacerons et nous l'indiquerons dans le second rendu.
