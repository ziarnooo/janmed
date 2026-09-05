#!/usr/bin/env python3
"""
Sanity check builda - uruchamiany lokalnie i w CI po `python3 build.py`.

Sprawdza rzeczy, które psują stronę po cichu:
  • martwe ścieżki lokalne (href/src wskazujące na nieistniejący plik),
  • brak <title> / meta description / canonical,
  • brakujące pliki, które muszą trafić na Pages (CNAME, sitemap, 404),
  • czy każdy wpis z content/posts/ ma swoją stronę.

Kończy się kodem 1, jeśli coś jest nie tak - wtedy deploy się nie odpala.
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

errors = []
warnings = []


def pages():
    for f in glob.glob(os.path.join(DIST, "**", "*.html"), recursive=True):
        if os.sep + "_probe" + os.sep in f:
            continue  # sondy robocze nie jadą na produkcję
        yield f


def rel(f):
    return os.path.relpath(f, DIST)


# --- martwe ścieżki lokalne -------------------------------------------------

for f in pages():
    src = open(f, encoding="utf-8").read()
    base = os.path.dirname(f)
    for m in re.finditer(r'(?:href|src)="([^"]+)"', src):
        h = m.group(1)
        if h.startswith(("#", "data:", "http", "mailto:", "tel:", "//")):
            continue
        target = os.path.normpath(os.path.join(base, h.split("#")[0].split("?")[0]))
        if not (os.path.isfile(target) or os.path.isfile(os.path.join(target, "index.html"))):
            errors.append("%s → martwa ścieżka %s" % (rel(f), h))

# --- podstawowe meta --------------------------------------------------------

for f in pages():
    src = open(f, encoding="utf-8").read()
    name = rel(f)
    if not re.search(r"<title>[^<]{5,}</title>", src):
        errors.append("%s → brak sensownego <title>" % name)
    if not re.search(r'<link rel="canonical" href="https://', src):
        errors.append("%s → brak canonical" % name)
    desc = re.search(r'<meta name="description" content="([^"]*)"', src)
    if not desc:
        errors.append("%s → brak meta description" % name)
    elif not desc.group(1).strip() and "404" not in name:
        warnings.append("%s → pusta meta description" % name)
    if "{{" in src:
        errors.append("%s → niepodstawiony placeholder w szablonie" % name)
    if re.search(r'<img (?![^>]*\balt=)', src):
        warnings.append("%s → obrazek bez atrybutu alt" % name)

# --- pliki wymagane przez Pages --------------------------------------------

for required in ("index.html", "404.html", "sitemap.xml", "robots.txt", "CNAME", ".nojekyll"):
    if not os.path.exists(os.path.join(DIST, required)):
        errors.append("brak pliku %s w dist/" % required)

# --- każdy wpis ma stronę ---------------------------------------------------

for md in glob.glob(os.path.join(ROOT, "content", "posts", "*.md")):
    slug = os.path.basename(md)[:-3]
    if not os.path.isfile(os.path.join(DIST, slug, "index.html")):
        errors.append("wpis %s nie ma wygenerowanej strony" % slug)

# --- każda oferta pracy ma stronę ------------------------------------------

for md in glob.glob(os.path.join(ROOT, "content", "jobs", "*.md")):
    slug = os.path.basename(md)[:-3]
    if not os.path.isfile(os.path.join(DIST, "praca", slug, "index.html")):
        errors.append("oferta pracy %s nie ma wygenerowanej strony" % slug)

# --- podsumowanie -----------------------------------------------------------

n_pages = len(list(pages()))
for w in warnings:
    print("uwaga: " + w)
for e in errors:
    print("BŁĄD:  " + e)

print("\nsprawdzono %d stron - %d błędów, %d uwag" % (n_pages, len(errors), len(warnings)))
sys.exit(1 if errors else 0)
