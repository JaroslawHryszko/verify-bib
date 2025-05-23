# verify_bib.py

`verify_bib.py` is a lightweight command-line tool for validating entries in a `.bib` (BibTeX) file.  
It checks whether each citation title matches an actual publication found in either **Crossref** (for journals and conferences) or **arXiv** (for preprints).

### Features

- Searches by title via public Crossref API and arXiv API
- Calculates string similarity between `.bib` entry and online match
- Flags suspicious or unverifiable entries
- Produces a clear, tabulated summary with scores and source

---

## Installation

```bash
pip install -r requirements.txt
```

Required packages:
- `bibtexparser`
- `requests`
- `feedparser`
- `tabulate`

---

## Usage

```bash
python verify_bib.py references.bib
```

Optional:

```bash
python verify_bib.py references.bib --threshold 0.85
```

- `--threshold` sets the minimum similarity score (0.0–1.0) to consider a match as valid (default: 0.80)

---

## Output

You will get a Markdown-style table with status flags and similarity scores:

```
| BibKey             | Status | Source   | Score | Title                               |
|--------------------|:------:|:--------:|------:|-------------------------------------|
| brown2020language  |   OK   | Crossref |  0.97 | Language Models are Few‑Shot Learners |
| smith2023unknown   | CHECK  |          |  0.45 | A Hypothetical Paper That Does...   |
```

- **OK**: A high-confidence match was found in Crossref or arXiv
- **CHECK**: No reliable match; consider reviewing manually

---

## License

MIT License