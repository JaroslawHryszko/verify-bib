#!/usr/bin/env python3
"""verify_bib.py – Quick validity checker for BibTeX references.

For each entry in the given .bib file it tries to find a close-enough match
in Crossref (journal & conference papers) and, if not found there, in arXiv.
It reports a simple OK / CHECK flag plus the similarity score.
"""

import argparse
import difflib
import re
import sys
from pathlib import Path
import urllib.parse

import requests
import bibtexparser
from tabulate import tabulate


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def query_crossref(title: str):
    try:
        resp = requests.get(
            "https://api.crossref.org/works",
            params={"query.title": title, "rows": 5},
            timeout=10,
        )
        resp.raise_for_status()
    except Exception:
        return None, 0.0

    items = resp.json().get("message", {}).get("items", [])
    best_item, best_score = None, 0.0
    for it in items:
        cr_title = " ".join(it.get("title", []))
        score = similarity(title, cr_title)
        if score > best_score:
            best_item, best_score = it, score
    return best_item, best_score


def query_arxiv(title: str):
    import feedparser

    try:
        search = f'ti:"{title}"'
        query = urllib.parse.quote(search)
        url = f"http://export.arxiv.org/api/query?search_query={query}&max_results=5"
        feed = feedparser.parse(url)
    except Exception:
        return None, 0.0

    best_ent, best_score = None, 0.0
    for ent in feed.entries:
        score = similarity(title, ent.title)
        if score > best_score:
            best_ent, best_score = ent, score
    return best_ent, best_score


def main():
    p = argparse.ArgumentParser(description="Verify BibTeX entries via Crossref / arXiv look-ups.")
    p.add_argument("bibfile", type=Path, help="BibTeX file to check")
    p.add_argument("--threshold", type=float, default=0.8, help="Minimum similarity [0–1] to mark entry as OK (default: 0.80)")
    args = p.parse_args()

    if not args.bibfile.exists():
        sys.exit(f"File {args.bibfile} does not exist.")

    with args.bibfile.open(encoding="utf-8") as fh:
        bib_db = bibtexparser.load(fh)

    rows = []
    for entry in bib_db.entries:
        key = entry.get("ID", "<no-key>")
        raw_title = entry.get("title", "").strip()
        title = re.sub(r"[{}]", "", raw_title)

        status, source, score = "CHECK", "", 0.0

        cr_item, cr_score = query_crossref(title)
        if cr_score >= args.threshold:
            status, source, score = "OK", "Crossref", cr_score
        else:
            ar_item, ar_score = query_arxiv(title)
            if ar_score >= args.threshold:
                status, source, score = "OK", "arXiv", ar_score

        rows.append([
            key,
            status,
            source,
            f"{score:.2f}",
            title if len(title) <= 60 else title[:57] + "…",
        ])

    print(tabulate(
        rows,
        headers=["BibKey", "Status", "Source", "Score", "Title"],
        tablefmt="github",
        colalign=("left", "center", "center", "right", "left"),
    ))


if __name__ == "__main__":
    main()
