"""Essais rapides des modules tiers envisagés (lancer dans le venv du projet)."""
import time, tomllib, difflib
from pathlib import Path

# --- python-docx : écrire puis relire un .docx
import docx
d = docx.Document(); d.add_paragraph("Cours de Python à Évry en 2026."); d.save("essais/test.docx")
print("python-docx :", [p.text for p in docx.Document("essais/test.docx").paragraphs])

# --- pypdf : relire un PDF
from pypdf import PdfReader
if Path("essais/test.pdf").exists():
    print("pypdf       :", repr(PdfReader("essais/test.pdf").pages[0].extract_text()))

# --- rapidfuzz contre difflib : distance et vitesse
from rapidfuzz.distance import Levenshtein, DamerauLevenshtein
print("rapidfuzz   : Damerau-Levenshtein(pyhton, python) =", DamerauLevenshtein.distance("pyhton", "python"))
print("rapidfuzz   : distance(pyhton, python) =", Levenshtein.distance("pyhton", "python"),
      "| distance(pithon, python) =", Levenshtein.distance("pithon", "python"))
mots = ("python pyhton java script corpus texte recherche " * 20000).split()
t = time.perf_counter(); n1 = sum(Levenshtein.distance(m, "python", score_cutoff=1) <= 1 for m in mots); t1 = time.perf_counter() - t
t = time.perf_counter(); n2 = sum(difflib.SequenceMatcher(None, m, "python").ratio() >= 0.8 for m in mots); t2 = time.perf_counter() - t
print(f"  {len(mots)} mots : rapidfuzz {t1:.2f} s ({n1} trouvés), difflib {t2:.2f} s ({n2} trouvés)")

# --- regex : correspondance approximative
# (module écarté, absent de requirements.txt : python -m pip install regex pour refaire l'essai)
try:
    import regex
    print("regex       :", regex.findall(r"(?:python){e<=1}", "du pyhton, du python et du pithon"))
except ModuleNotFoundError:
    print("regex       : non installé, essai ignoré")

# --- rich : tableau + export HTML
from rich.console import Console
from rich.table import Table
c = Console(record=True, width=60)
t = Table(title="Classement"); t.add_column("fichier"); t.add_column("score", justify="right")
t.add_row("cours.txt", "[green]72.5[/green]"); c.print(t)
c.save_html("essais/test.html"); print("rich        : HTML de", Path("essais/test.html").stat().st_size, "octets")

# --- tomllib : listes et nombres typés
cfg = tomllib.loads('[[critere]]\ntype = "mot"\nmotif = "python"\npoids = 2\n[options]\nignorer_casse = true')
print("tomllib     :", cfg)

# --- pathlib : motifs glob
print("pathlib     :", Path("exemples/rapport_2025.txt").match("rapport_*"), sorted(p.name for p in Path("essais").rglob("*.docx")))
