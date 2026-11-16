# Outil de recherche dans un corpus de texte

Projet Langages de scripts, L3 SR, Université d'Évry, 2026-2027.

**Groupe : TrioLogic**

**Membres :** Samy YOUNSI, Aya BEN-TCHICHIA, Nawel SKENDRAOUI (voir aussi [`groupe.csv`](groupe.csv))

> **Document mis à jour après le premier rendu** pour tenir compte des remarques reçues : définition explicite des motifs, configuration placée à la base de l'outil, dépendances revues, fonctionnalités supplémentaires plus ambitieuses, étude élargie de l'écosystème Python avec des essais. La version notée du premier rendu reste consultable au commit `88073a9`.

## Présentation

L'outil répond à la question : **« parmi tous ces documents, lesquels correspondent le mieux à ce que je cherche ? »**

L'utilisateur décrit une recherche : quels documents, quels motifs, comment les combiner. L'outil cherche les motifs dans le contenu et dans le nom des documents, calcule des statistiques et un score de pertinence pour chacun, puis produit un classement exporté en CSV.

## Installation

Python **3.11 ou plus récent** est nécessaire (`tomllib` pour la configuration, et `rapidfuzz` ne publie plus de version pour les Python plus anciens).

```bash
git clone https://github.com/Samy-Younsi/Outil-de-recherche-dans-un-corpus-de-texte-python.git
cd Outil-de-recherche-dans-un-corpus-de-texte-python
python -m venv .venv
source .venv/bin/activate          # sous Windows : .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Le noyau minimal n'utilise que la bibliothèque standard. Les modules de `requirements.txt` servent aux fonctionnalités supplémentaires.

## Utilisation

Une recherche se définit **en ligne de commande** ou dans un **fichier de configuration TOML**. En cas de conflit, la ligne de commande l'emporte sur le fichier, qui l'emporte sur les valeurs par défaut.

```bash
# documents de exemples/ (sous-dossiers compris) contenant "python" ET une année
python main.py exemples -r --mot python --regex "\d{4}" --mode ET -o resultats.csv

# la même recherche décrite dans un fichier, en changeant seulement la sortie
python main.py --config recherche.toml -o autre.csv
```

### Comment définir un motif

Un **critère** de recherche est composé d'un type, d'un motif, et éventuellement d'un poids.

| Type | Où cherche-t-on ? | Le motif est | Option |
|---|---|---|---|
| `mot` | contenu du document | une chaîne de caractères exacte | `--mot TEXTE` |
| `regex` | contenu du document | une expression régulière (syntaxe du module `re`) | `--regex MOTIF` |
| `nom` | nom du fichier | une chaîne, ou une expression régulière avec `--nom-regex` | `--nom TEXTE` |

Chaque option peut être répétée pour donner plusieurs critères. `--sauf TEXTE` ajoute un critère d'exclusion : le document ne doit pas contenir ce texte.

| Option | Effet |
|---|---|
| `--mode ET` (défaut) / `--mode OU` | le document doit satisfaire tous les critères, ou au moins un |
| `--ignorer-casse` | « Python » et « python » sont équivalents |
| `--sans-accents` | « Évry » et « evry » sont équivalents |
| `--mot-entier` | « python » ne correspond pas à « pythonique » |
| `--approx N` | tolère N fautes de frappe (fonctionnalité F14) |

Le même exemple en TOML, avec des poids :

```toml
[corpus]
dossier = "exemples"
recursif = true
extensions = [".txt", ".pdf"]
exclure_dossiers = ["brouillons"]

[[critere]]
type = "mot"
motif = "python"
poids = 2

[[critere]]
type = "regex"
motif = '\d{4}'

[options]
mode = "ET"
ignorer_casse = true
sortie = "resultats.csv"
```

## Vue d'ensemble des fonctionnalités

Les priorités donnent l'ordre de réalisation :

- **P1, socle :** le minimum pour qu'une recherche fonctionne de bout en bout (un dossier, un mot, des statistiques, un CSV).
- **P2, fin du noyau :** le reste de ce que demande l'énoncé.
- **P3, compléments visés :** ce que nous comptons réaliser une fois le noyau terminé.
- **P4, si le temps le permet :** des ajouts simples et indépendants.
- **P5, bonus :** des ajouts plus ambitieux, seulement s'il reste du temps après P4.

Dans le noyau, F1, F3, F6, F10 et F12 sont en P1 ; F2, F4, F5, F7, F8, F9 et F11 en P2.

La colonne « État » de la section [Avancement](#avancement) est mise à jour à chaque rendu hebdomadaire.

## Noyau minimal

### Configuration

F1. Interface en ligne de commande.

   * définit le corpus (dossier ou fichier de liste), les critères, les options et le fichier de sortie
   * `--mot`, `--regex`, `--nom` et `--sauf` sont répétables, pour combiner plusieurs critères
   * `--help` affiche l'aide générée automatiquement
   * une erreur d'utilisation (dossier inexistant, aucun critère, expression régulière invalide) est signalée **avant** de lire le corpus, sur la sortie d'erreur
   * code de retour, comme `grep` : 0 si au moins un document est retenu, 1 si aucun, 2 en cas d'erreur, afin que l'outil soit utilisable dans un script shell

F2. Fichier de configuration TOML.

   * décrit une recherche complète et réutilisable : corpus, filtres, critères avec leurs poids, options
   * ordre de priorité : ligne de commande, puis fichier, puis valeurs par défaut
   * une clé inconnue ou une valeur du mauvais type provoque une erreur qui nomme la clé fautive, au lieu d'être ignorée en silence
   * le format `.ini` est écarté : toutes ses valeurs sont des chaînes, alors qu'il nous faut une liste de critères avec des poids numériques
   * dépend de F1

### Constitution du corpus

F3. Corpus par répertoire.

   * tous les fichiers d'un répertoire ; avec `-r`, ceux de ses sous-répertoires aussi
   * la liste est triée, pour que deux exécutions donnent le même résultat
   * un sous-répertoire inaccessible est ignoré avec un avertissement, sans arrêter l'analyse
   * lecture en UTF-8, puis en latin-1 en cas d'échec ; un document illisible est compté comme tel et n'interrompt pas la recherche
   * dépend de F1

F4. Corpus par liste de fichiers.

   * `--liste FICHIER` : un chemin par ligne
   * les lignes vides et celles qui commencent par `#` sont ignorées, ce qui permet de commenter la liste
   * un chemin relatif est interprété par rapport à l'emplacement du fichier de liste, pas par rapport au dossier courant, pour que la liste reste valable quel que soit l'endroit d'où on lance l'outil
   * les chemins inexistants sont signalés par un avertissement ; les doublons sont retirés
   * dépend de F1

F5. Filtres du corpus.

   * par extension (`--ext .txt .md`), sans tenir compte de la casse (`.TXT` est accepté)
   * par nom, avec un motif `glob` (`--filtre-nom "rapport_*"`) ou une expression régulière (`--filtre-regex`)
   * par emplacement : `--exclure-dossier brouillons` écarte tout ce qui se trouve sous un dossier de ce nom
   * les filtres se cumulent : un fichier doit tous les passer
   * dépend de F3 et F4

### Recherche

F6. Recherche d'une chaîne exacte dans le contenu.

   * renvoie la position de chaque occurrence, sans chevauchement (« aa » dans « aaaa » compte 2 fois)
   * options casse, accents et mot entier ; la comparaison se fait sur une copie normalisée du texte **de même longueur**, pour que les positions restent valables dans le texte d'origine (utile pour les extraits de F15)
   * dépend de F3, F4 et F5

F7. Recherche par expression régulière dans le contenu.

   * syntaxe du module `re` de Python, avec l'option `--ignorer-casse`
   * l'expression est compilée une seule fois, à la lecture de la configuration : une expression invalide arrête l'outil avec un message clair avant toute lecture de fichier (F1)
   * les correspondances vides (par exemple avec `a*`) ne sont pas comptées
   * dépend de F3, F4 et F5

F8. Recherche dans le nom des fichiers.

   * porte sur le nom du fichier seul, sans son dossier (le filtrage par dossier est le rôle de F5)
   * chaîne simple ou expression régulière
   * différence avec F5 : un filtre retire le fichier du corpus, alors qu'un critère de nom compte dans les statistiques et le score
   * dépend de F3, F4 et F5

F9. Combinaison de critères.

   * mode ET : le document est retenu s'il satisfait tous les critères
   * mode OU : s'il en satisfait au moins un
   * SAUF : un document qui contient un critère d'exclusion n'est jamais retenu, quel que soit le mode
   * dépend de F6, F7 et F8

### Statistiques et résultats

F10. Statistiques par document.

   * nombre d'occurrences de chaque motif
   * proportion du contenu correspondant aux motifs : nombre de caractères couverts par au moins une occurrence, divisé par la longueur du texte ; deux occurrences qui se recouvrent ne sont comptées qu'une fois
   * densité : nombre total d'occurrences pour 1000 mots, afin de comparer un document court et un document long
   * nombre de critères satisfaits sur le nombre total
   * un document vide a des statistiques nulles, sans division par zéro
   * dépend de F6, F7, F8 et F9

F11. Score de pertinence et classement.

   * `score = 100 × (0,6 × part pondérée des critères satisfaits + 0,4 × min(1, densité / 20))`
   * la part pondérée utilise le poids de chaque critère (1 par défaut) : un critère de poids 2 compte double
   * la densité est plafonnée pour qu'un document qui répète un seul mot ne passe pas devant un document qui satisfait tous les critères
   * les coefficients 0,6 et 0,4 et le plafond de 20 sont réglables dans le fichier de configuration
   * classement par score décroissant ; à égalité, par nombre d'occurrences puis par nom, pour un ordre toujours identique
   * dépend de F2 et F10

F12. Export CSV.

   * une ligne par document retenu, dans l'ordre du classement
   * colonnes : fichier, nombre de mots, une colonne d'occurrences par motif, proportion, densité, critères satisfaits, score
   * encodage UTF-8 avec BOM, pour que les accents s'affichent correctement à l'ouverture dans Excel
   * `--tous` exporte aussi les documents non retenus, avec une colonne « retenu »
   * dépend de F10 et F11

## Fonctionnalités supplémentaires

### Compléments visés (P3)

F13. Documents PDF et Word.

   L'énoncé se limite aux `.txt`, mais un vrai corpus (cours, rapports) contient surtout des PDF et des documents Word.

   * modifier la lecture de F3 et F4 pour extraire le texte des `.pdf` et des `.docx`, selon l'extension
   * pour un `.docx` : les paragraphes et le contenu des tableaux
   * un PDF scanné (des images, sans texte) est signalé comme illisible au lieu d'être compté comme un document vide
   * F6 à F12 ne changent pas : elles reçoivent du texte, quelle que soit son origine
   * dépend de F3 et F4

F14. Recherche approximative.

   * `--approx N` retrouve un mot malgré N fautes de frappe : « pyhton » ou « pithon » trouvent « python »
   * mesure utilisée : distance de **Damerau-Levenshtein**. Notre essai montre que la distance de Levenshtein simple compte 2 erreurs pour deux lettres inversées (« pyhton »), la faute de frappe la plus courante, alors que Damerau-Levenshtein en compte 1
   * s'applique seulement aux critères de type `mot`, et pas aux motifs de moins de 4 lettres, qui donneraient trop de faux résultats
   * modifier F10 pour compter les occurrences approximatives dans une colonne séparée, et F11 pour qu'elles comptent moins qu'une occurrence exacte
   * dépend de F6 ; modifie F10 et F11

F15. Affichage du classement dans le terminal.

   * tableau en couleur des meilleurs documents (`--top N`, 10 par défaut)
   * `--extraits N` : sous chaque document, les N premiers passages où un motif apparaît, avec le motif surligné et 30 caractères de contexte de chaque côté
   * `--silencieux` supprime l'affichage, pour l'usage dans un script
   * dépend de F6, F7 et F11

### Si le temps le permet (P4)

F16. Bilan global du corpus.

   * nombre de documents analysés, retenus, vides, illisibles
   * total des occurrences par motif sur tout le corpus
   * les 10 mots les plus fréquents dans les documents retenus, hors mots de moins de 4 lettres
   * dépend de F10

F17. Rapport HTML autonome.

   * `--html rapport.html` enregistre le classement et les extraits surlignés dans une page consultable sans l'outil
   * dépend de F15

F18. Export JSON.

   * `--json resultats.json` : les mêmes données que le CSV, avec en plus la position de chaque occurrence, pour qu'un autre programme puisse réutiliser les résultats
   * dépend de F10 et F11

### Bonus (P5)

F19. Pondération par rareté (TF-IDF).

   * un motif présent dans presque tous les documents distingue mal les documents entre eux : modifier F11 pour qu'un motif rare dans le corpus compte davantage
   * demande deux passes : compter d'abord dans combien de documents chaque motif apparaît, puis calculer les scores
   * dépend de F10 et F11

F20. Recherche de proximité.

   * `--proche "python,erreur" --distance 10` : les deux mots doivent apparaître à moins de 10 mots l'un de l'autre
   * réutilise les positions renvoyées par F6
   * modifier F9 pour ajouter ce type de critère
   * dépend de F6 et F9

F21. Gros corpus.

   * barre de progression pendant l'analyse
   * analyse des documents en parallèle sur plusieurs processus
   * dépend de F3 à F10

## Briques logicielles

### Nos choix

| Besoin | Fonctionnalités | Choix | Écartés |
|---|---|---|---|
| Ligne de commande | F1 | `argparse` (standard) | `click`, `typer` (dépendances en plus ; leur intérêt est surtout dans les sous-commandes, que nous n'avons pas) |
| Configuration | F2, F11 | `tomllib` (standard) | `configparser` (toutes les valeurs sont des chaînes, pas de listes), PyYAML (dépendance en plus, et l'indentation significative rend les erreurs faciles), `json` (pas de commentaires) |
| Parcours et filtres | F3, F4, F5 | `pathlib` + `re` | `os.walk` (chemins sous forme de chaînes), `fnmatch` seul (trop limité), `glob` (fonctions reprises par `Path.glob` et `Path.match`) |
| Encodage | F3 | essais UTF-8 puis latin-1 | `charset-normalizer` (gardé en réserve), `chardet` |
| Recherche | F6 à F9 | `re`, méthodes de `str` | `regex` (voir F14) |
| Accents | F6 | `unicodedata` (standard) | Unidecode (licence GPL ; translittère d'autres alphabets, inutile ici) |
| Statistiques | F10, F16 | `collections.Counter` | `pandas` (installe `numpy`, très lourd pour un tableau de quelques colonnes) |
| Score | F11, F19 | formule écrite par nous | scikit-learn (TF-IDF tout fait, mais dépendance énorme pour un seul calcul) |
| Exports | F12, F18 | `csv`, `json` (standard) | `pandas` |
| PDF | F13 | `pypdf` | `pdfminer.six` (plus lent, interface plus complexe), PyMuPDF (rapide, mais licence AGPL) |
| Word | F13 | `python-docx` | `docx2txt` (ne donne que le texte brut, pas d'accès aux tableaux) |
| Recherche approximative | F14 | `rapidfuzz` | `difflib` (40 fois plus lent dans notre essai, pas de distance en nombre de fautes), `thefuzz` (dernière version en janvier 2024), `regex` (résultats difficiles à maîtriser) |
| Affichage, HTML, progression | F15, F17, F21 | `rich` | `colorama` (couleurs seulement), `tabulate` (tableaux seulement), `tqdm` (progression seulement), Jinja2 (gabarit HTML à écrire nous-mêmes) |
| Parallélisme | F21 | `concurrent.futures` (standard) | `multiprocessing` directement (plus bas niveau) |
| Outil externe | F6, F7 | aucun | `grep`, `ripgrep` appelés par `subprocess` (absents de Windows par défaut, syntaxe d'expressions régulières différente de Python, ne calculent pas nos statistiques) |

### Analyse des briques

Les essais ont été faits sous Windows 11 avec Python 3.14, dans un environnement virtuel, avec le script [`essais/essai_modules.py`](essais/essai_modules.py). Les versions et les dates sont celles de PyPI au 16/11/2026.

**pypdf** extrait le texte de chaque page d'un PDF. Il ne lit pas les PDF scannés (il faudrait de l'OCR) et peut mélanger l'ordre du texte sur les mises en page en colonnes. Il est écrit en pur Python et n'a aucune dépendance, donc il s'installe partout. L'utilisation tient en une ligne par page (`PdfReader(f).pages[i].extract_text()`), et l'essai sur un PDF simple a rendu le texte exact. Licence BSD. Demande Python 3.10 ou plus. C'est le successeur de PyPDF2 ; la documentation est complète.
**Dernière version :** 7.1.0, 13 novembre 2026

**python-docx** lit les paragraphes et les tableaux d'un `.docx`. Il ne lit pas l'ancien format `.doc`, et les en-têtes et notes de bas de page se lisent à part. Il dépend de `lxml`, qui fournit des paquets précompilés, et l'installation n'a posé aucun problème. L'essai a relu correctement un texte accentué. Licence MIT. Les versions sont peu fréquentes, mais le format `.docx` est stable. Documentation complète avec exemples.
**Dernière version :** 1.2.0, 16 juin 2025

**rapidfuzz** calcule des distances entre chaînes (Levenshtein, Damerau-Levenshtein et d'autres). Il compare des chaînes entre elles : c'est à nous de découper le texte en mots et de retrouver leurs positions. Écrit en C++, il publie des paquets précompilés pour Windows, Linux et macOS, sans aucune dépendance. Dans notre essai sur 140 000 mots, il a répondu en 0,02 s contre 0,85 s pour `difflib`. C'est aussi cet essai qui nous a fait choisir Damerau-Levenshtein (voir F14). Licence MIT. Demande Python 3.11 ou plus, ce qui fixe la version minimale du projet. Projet très actif, documentation complète.
**Dernière version :** 3.14.6, 30 août 2026

**rich** affiche des tableaux, des couleurs, du texte surligné et des barres de progression, et peut enregistrer ce qu'il affiche en HTML : une seule brique couvre F15, F17 et la progression de F21. Il ne fait que de l'affichage. Pur Python, deux petites dépendances (`markdown-it-py`, `pygments`). L'essai a produit un tableau et son export HTML en quelques lignes, y compris dans le terminal Windows. Il retire de lui-même les couleurs quand la sortie est redirigée vers un fichier. Licence MIT. Très grande communauté, documentation très complète.
**Dernière version :** 15.0.0, 12 avril 2026

**tomllib** lit un fichier TOML et renvoie directement des dictionnaires, des listes, des nombres et des booléens ; l'essai a relu une liste de critères avec leurs poids sans conversion. Il ne sait pas écrire de TOML, ce dont nous n'avons pas besoin. Fourni avec Python depuis la version 3.11.

**regex** (écarté) remplace `re` et accepte une syntaxe approximative, par exemple `(?:python){e<=1}`. Dans notre essai, il a trouvé « pithon » mais a renvoyé « ␣python » avec l'espace qui précède et n'a pas trouvé « pyhton » à une erreur près : le résultat dépend de l'endroit où le moteur place les erreurs, ce qui fausserait nos positions et nos comptages.
**Dernière version :** 2026.11.15, 15 novembre 2026

**charset-normalizer** (en réserve) devine l'encodage d'un fichier. Nous ne l'utiliserons que si nos deux essais successifs (UTF-8 puis latin-1) se révèlent insuffisants sur de vrais corpus, car une détection automatique peut se tromper sur des fichiers très courts.
**Dernière version :** 3.5.2, 30 septembre 2026

La bibliothèque standard couvre le reste :

- `argparse` pour la ligne de commande (F1)
- `pathlib` pour le parcours, les motifs `glob` et la lecture (F3, F4, F5, F8)
- `re` pour les expressions régulières, les filtres et l'option mot entier (F5, F6, F7, F8)
- `unicodedata` pour retirer les accents (F6)
- `collections` pour les comptages (F10, F16)
- `csv` et `json` pour les exports (F12, F18)
- `math` pour le logarithme de TF-IDF (F19)
- `concurrent.futures` pour le parallélisme (F21)
- `sys` pour les codes de retour et la sortie d'erreur (F1)

## Structure du code

| Fichier | Rôle | Responsable |
|---|---|---|
| `main.py` | ligne de commande, fusion avec la configuration, enchaînement des étapes | Nawel |
| `corpus.py` | constitution et filtrage du corpus, lecture des documents (texte, PDF, Word), lecture du fichier TOML | Aya |
| `recherche.py` | recherche des motifs, options, application des critères, recherche approximative | Samy |
| `stats.py` | statistiques, score, classement | Nawel |
| `export.py` | export CSV, affichage terminal, rapport HTML | Nawel |
| `bilan.py` | bilan global du corpus | Aya |
| `exemples/` | petit corpus de test | Aya |
| `essais/` | scripts d'essai des modules tiers | Aya |

## Répartition du travail

| Membre | Fonctionnalités |
|---|---|
| Aya BEN-TCHICHIA | F2 (lecture du TOML), F3, F4, F5, F13, F16 |
| Samy YOUNSI | F6, F7, F8, F9, F14 |
| Nawel SKENDRAOUI | F1, F10, F11, F12, F15, F17 |

F18 à F21 seront attribuées selon les disponibilités, une fois P3 terminé.

## Avancement

État au 16/11/2026. La commande `python main.py exemples -r --mot python -o resultats.csv` fonctionne de bout en bout.

| Fonctionnalité | État | Détail |
|---|---|---|
| F1 Ligne de commande | en partie | dossier, `-r`, `--mot` (répétable), `-o` ; restent les autres options, les messages d'erreur et les codes de retour |
| F2 Fichier TOML | à faire | |
| F3 Corpus par répertoire | fait | parcours, sous-répertoires, lecture UTF-8 puis latin-1 ; reste l'avertissement pour un dossier inaccessible |
| F4 Corpus par liste | à faire | |
| F5 Filtres | à faire | |
| F6 Chaîne exacte | fait | options casse, accents et mot entier, avec doctests |
| F7 Expression régulière | à faire | |
| F8 Nom des fichiers | à faire | |
| F9 Combinaison de critères | en partie | plusieurs critères de type `mot` ; restent les types `regex` et `nom`, et les modes ET, OU, SAUF |
| F10 Statistiques | en partie | occurrences par motif ; restent la proportion, la densité et les critères satisfaits |
| F11 Score et classement | à faire | |
| F12 Export CSV | en partie | une ligne par document ; restent le BOM, l'ordre du classement et `--tous` |
| F13 à F21 | à faire | |
