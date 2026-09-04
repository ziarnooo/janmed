#!/usr/bin/env python3
"""
Generator statycznej strony Hospicjum Domowego JANMED.

Wejście:  content/ (markdown + json), templates/, css/, js/, assets/
Wyjście:  dist/    - gotowe do wrzucenia na GitHub Pages

Bez zależności zewnętrznych. Uruchomienie:  python3 build.py
"""

import html
import json
import os
import re
import shutil
import sys
from datetime import date
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "dist")

# --------------------------------------------------------------------------
# markdown (podzbiór, który faktycznie występuje w treści: h2/h3, akapity,
# listy ul/ol, bold, italic, linki, obrazki)
# --------------------------------------------------------------------------

INLINE_RE = [
    (re.compile(r"!\[([^\]]*)\]\(([^)]+)\)"), None),          # obrazek - osobno
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), None),           # link - osobno
]


def inline(text, asset=lambda s: s, href=lambda h: h):
    """Zamienia inline'owy markdown na HTML. Escapuje wszystko po drodze."""
    out = []
    i = 0
    pattern = re.compile(
        r"!\[(?P<ialt>[^\]]*)\]\((?P<isrc>[^)]+)\)"
        r"|\[(?P<ltext>[^\]]+)\]\((?P<lhref>[^)]+)\)"
        r"|\*\*(?P<b>[^*]+)\*\*"
        r"|\*(?P<i>[^*]+)\*"
        r"|`(?P<c>[^`]+)`"
    )
    for m in pattern.finditer(text):
        out.append(html.escape(text[i:m.start()]))
        if m.group("isrc") is not None:
            out.append('<img src="%s" alt="%s" loading="lazy" decoding="async">'
                       % (html.escape(asset(m.group("isrc"))), html.escape(m.group("ialt"))))
        elif m.group("lhref") is not None:
            raw = m.group("lhref")
            ext = raw.startswith("http") and "janmed.pl" not in raw
            attrs = ' target="_blank" rel="noopener"' if ext else ""
            out.append('<a href="%s"%s>%s</a>'
                       % (html.escape(href(raw)), attrs,
                          inline(m.group("ltext"), asset, href)))
        elif m.group("b") is not None:
            out.append("<strong>%s</strong>" % inline(m.group("b"), asset, href))
        elif m.group("i") is not None:
            out.append("<em>%s</em>" % inline(m.group("i"), asset, href))
        else:
            out.append("<code>%s</code>" % html.escape(m.group("c")))
        i = m.end()
    out.append(html.escape(text[i:]))
    return "".join(out).replace("  \n", "<br>\n")


def markdown(src, asset=lambda s: s, href=lambda h: h):
    blocks = re.split(r"\n\s*\n", src.strip())
    out = []
    for b in blocks:
        b = b.strip("\n")
        if not b:
            continue
        first = b.lstrip().split("\n")[0]
        m = re.match(r"^(#{2,6})\s+(.*)$", first)
        if m:
            lvl = len(m.group(1))
            rest = b.split("\n", 1)
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2).strip(), asset, href), lvl))
            if len(rest) > 1 and rest[1].strip():
                out.append(markdown(rest[1], asset, href))
            continue
        if re.match(r"^\s*-\s+", first):
            items = [re.sub(r"^\s*-\s+", "", ln) for ln in b.split("\n") if ln.strip()]
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(i, asset, href) for i in items))
            continue
        if re.match(r"^\s*\d+\.\s+", first):
            items = [re.sub(r"^\s*\d+\.\s+", "", ln) for ln in b.split("\n") if ln.strip()]
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % inline(i, asset, href) for i in items))
            continue
        if b.strip() == "---":
            out.append("<hr>")
            continue
        if first.lstrip().startswith("|"):
            rows = [ln for ln in b.split("\n") if ln.strip().startswith("|")]
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            head = cells[0] if len(cells) > 1 and set("".join(cells[1]).strip()) <= set("- ") else None
            body = cells[2:] if head else cells
            parts = ['<div class="table-wrap"><table>']
            if head and any(h for h in head):
                parts.append("<thead><tr>%s</tr></thead>"
                             % "".join("<th>%s</th>" % inline(c, asset, href) for c in head))
            parts.append("<tbody>")
            for row in body:
                parts.append("<tr>%s</tr>"
                             % "".join("<td>%s</td>" % inline(c, asset, href) for c in row))
            parts.append("</tbody></table></div>")
            out.append("".join(parts))
            continue
        out.append("<p>%s</p>" % inline(b.replace("\n", " ").strip(), asset, href))
    return "\n".join(out)


def front_matter(raw):
    if not raw.startswith("---"):
        return {}, raw
    _, fm, body = raw.split("---", 2)
    meta = {}
    for line in fm.strip().split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        meta[k.strip()] = v
    return meta, body.lstrip("\n")


# --------------------------------------------------------------------------
# dane
# --------------------------------------------------------------------------

def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


SITE = json.loads(read("content/site.json"))
HOME = json.loads(read("content/home.json"))
BASE = read("templates/base.html")
ICONS = {n: read("templates/icons/%s.svg" % n)
         for n in ("sens", "szacunek", "zaufanie", "wspolne")}
LOGO = read("assets/svg/hospicjum-domowe-janmed-logo.svg")

POST_ORDER = [
    "rak-pluc-objawy",
    "komu-nalezy-sie-hospicjum-domowe",
    "czy-hospicjum-zabiera-emeryture",
    "czy-pacjent-moze-zostac-wypisany-z-hospicjum-domowego",
    "skierowanie-do-hospicjum-domowego",
    "ile-trzeba-czekac-na-hospicjum-domowe",
    "na-czym-polega-opieka-w-hospicjum-domowym",
    "hospicjum-domowe-ile-kosztuje-i-co-dostane",
    "opieka-paliatywna-czy-hospicjum-domowe",
    "hospicjum-domowe-jak-zalatwic",
    "hospicjum-domowe-instrukcja-obslugi",
    "ciezkie-chwile-dla-rodziny-pacjenta-hospicjum-domowego",
]


def excerpt(body, limit=170):
    """Pierwszy akapit treści, obcięty na granicy słowa - awaryjny lead karty."""
    for block in re.split(r"\n\s*\n", body.strip()):
        block = block.strip()
        if not block or block.startswith(("#", "-", ">")) or re.match(r"^\d+\.", block):
            continue
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", block)
        text = re.sub(r"[*`]", "", text).replace("\n", " ").strip()
        if len(text) <= limit:
            return text
        return text[:limit].rsplit(" ", 1)[0] + "…"
    return ""


def load_posts():
    posts = []
    for slug in POST_ORDER:
        meta, body = front_matter(read("content/posts/%s.md" % slug))
        meta["slug"] = slug
        meta["url"] = "/%s/" % slug
        meta["body"] = body
        if not meta.get("description"):
            meta["description"] = excerpt(body)
        posts.append(meta)
    return posts


def load_jobs():
    """Oferty pracy z content/jobs/. Kolejność: od najnowszej.
    Nie ma tu odpowiednika POST_ORDER - ofert będzie dużo i będą się zmieniać,
    więc porządkuje je data z front matter, a nie ręczna lista."""
    d = os.path.join(ROOT, "content", "jobs")
    if not os.path.isdir(d):
        return []
    jobs = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"):
            continue
        slug = fn[:-3]
        meta, body = front_matter(read("content/jobs/%s" % fn))
        meta["slug"] = slug
        meta["url"] = "/praca/%s/" % slug
        meta["body"] = body
        if not meta.get("description"):
            meta["description"] = excerpt(body)
        jobs.append(meta)
    jobs.sort(key=lambda j: (j.get("published", ""), j["title"]), reverse=True)
    return jobs


def image_size(path):
    """Wymiary JPEG/PNG prosto z nagłówka pliku - bez Pillow."""
    try:
        with open(path, "rb") as f:
            data = f.read(2)
            if data == b"\xff\xd8":                       # JPEG
                while True:
                    b = f.read(1)
                    while b and b != b"\xff":
                        b = f.read(1)
                    marker = f.read(1)
                    while marker == b"\xff":
                        marker = f.read(1)
                    if not marker:
                        return None
                    if marker[0] in range(0xC0, 0xCF) and marker[0] not in (0xC4, 0xC8, 0xCC):
                        f.read(3)
                        h = int.from_bytes(f.read(2), "big")
                        w = int.from_bytes(f.read(2), "big")
                        return w, h
                    size = int.from_bytes(f.read(2), "big")
                    f.read(size - 2)
            f.seek(0)
            if f.read(8) == b"\x89PNG\r\n\x1a\n":         # PNG
                f.read(8)
                return int.from_bytes(f.read(4), "big"), int.from_bytes(f.read(4), "big")
    except Exception:
        return None
    return None


IMG_DIMS = {}
for _f in os.listdir(os.path.join(ROOT, "assets", "img")):
    _d = image_size(os.path.join(ROOT, "assets", "img", _f))
    if _d:
        IMG_DIMS[_f] = _d


POSTS = load_posts()
POSTS_BY_SLUG = {p["slug"]: p for p in POSTS}
JOBS = load_jobs()


# --------------------------------------------------------------------------
# helpery renderowania
# --------------------------------------------------------------------------

def esc(s):
    return html.escape(str(s or ""), quote=True)


BRAND_LONG = " • Hospicjum Domowe JANMED"
BRAND_SHORT = " • JANMED"


def seo_title(t):
    """Google ucina tytuł ok. 60 znaków. Gdy nie mieści się z pełną nazwą marki,
    skracamy sufiks - a nie sam tytuł, bo to on niesie frazę."""
    t = (t or "").strip()
    if len(t) > 60 and t.endswith(BRAND_LONG):
        t = t[:-len(BRAND_LONG)] + BRAND_SHORT
    return t


def seo_desc(d, limit=158):
    """Meta description ucięty na granicy słowa - bez urwanych wyrazów w SERP."""
    d = " ".join((d or "").split())
    if len(d) <= limit:
        return d
    return d[:limit].rsplit(" ", 1)[0].rstrip(",;:--") + "…"


def rel(depth):
    """Ścieżka do katalogu głównego - build działa też w podkatalogu."""
    return "../" * depth if depth else ""


def link(href, depth):
    """Zamienia /absolutne/ ścieżki wewnętrzne na relatywne do dokumentu."""
    if href.startswith("/") and not href.startswith("//"):
        if href == "/":
            return rel(depth) or "./"
        return rel(depth) + href.lstrip("/")
    if href.startswith("/#"):
        return (rel(depth) or "./") + href[1:]
    return href


def asset(path, depth):
    return rel(depth) + path.lstrip("/")


ARROW = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
         '<path d="M2 8h11m0 0-4-4m4 4-4 4" stroke="currentColor" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')

COPY_ICON = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
             '<rect x="5.25" y="5.25" width="8" height="8" rx="1.75" stroke="currentColor" stroke-width="1.4"/>'
             '<path d="M10.75 2.75H4.5a1.75 1.75 0 0 0-1.75 1.75v6.25" stroke="currentColor" '
             'stroke-width="1.4" stroke-linecap="round"/></svg>')

CHECK_ICON = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
              '<path d="M3 8.5 6.2 11.7 13 4.9" stroke="currentColor" stroke-width="1.8" '
              'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def copy_email_btn(style="btn--ghost", value=None):
    """Adres e-mail JAKO przycisk: kliknięcie kopiuje go do schowka.
    Potwierdzenie lewituje nad przyciskiem, więc nie rozpycha układu."""
    mail = esc(value or SITE["email"])
    return (f'<span class="copy-wrap">'
            f'<button class="btn {style} copy-btn" type="button" data-copy="{mail}" '
            f'aria-label="Skopiuj adres e-mail: {mail}">{COPY_ICON}<span>{mail}</span></button>'
            f'<span class="copy-note" role="status" aria-live="polite"></span>'
            f'</span>')


def place_lines(name):
    """Nazwa placówki zawsze w dwóch liniach - „Hospicjum Domowe" i miejscowość.
    Inaczej „Olkusz" mieści się w jednej linii, „Kazimierza Wielka" w dwóch
    i kafelki obok siebie startują na różnych wysokościach."""
    prefix = "Hospicjum Domowe"
    if name.startswith(prefix):
        return esc(prefix), esc(name[len(prefix):].strip())
    head, _, tail = name.rpartition(" ")
    return esc(head or name), esc(tail if head else "")


INFO = ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9.25" stroke="currentColor" stroke-width="1.5"/>'
        '<path d="M12 11v6M12 7.4v.2" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round"/></svg>')


def logo_svg(depth, cls=""):
    return ('<a class="%s" href="%s" aria-label="Hospicjum Domowe JANMED - strona główna">%s</a>'
            % (cls, link("/", depth), LOGO))


def hero_figure(img, alt, depth, eager=True):
    """Wycięta z tła postać w nagłówku strony - ten sam chwyt co portret
    w sekcji „Nasza misja". Wymiary bierzemy z pliku, żeby nic nie skakało.

    Jeśli obok pliku leży bliźniaczy .webp, wychodzi <picture> - te grafiki
    to wycinki z kanałem alfa, więc PNG waży na nich kilkaset kilobajtów,
    a WebP dziesiątki. Bez .webp zostaje samo <img> i nic się nie zmienia."""
    w, h = IMG_DIMS.get(img, (300, 348))
    prio = 'fetchpriority="high"' if eager else 'loading="lazy"'
    tag = (f"""<img src="{asset('assets/img/' + img, depth)}" alt="{esc(alt)}"
               width="{w}" height="{h}" {prio} decoding="async">""")
    webp = os.path.splitext(img)[0] + ".webp"
    if os.path.isfile(os.path.join(ROOT, "assets", "img", webp)):
        tag = f"""<picture>
            <source srcset="{asset('assets/img/' + webp, depth)}" type="image/webp">
            {tag}
          </picture>"""
    return f"""<figure class="page-hero__figure reveal reveal--media">
          {tag}
        </figure>"""


def header(depth, active="", bare=False):
    """Belka serwisu. `bare` to ta sama belka bez nawigacji - używa jej strona
    formularza: ta sama wysokość, ta sama linia, to samo logo. Skoro nawigacji
    nie ma, logo zostaje samo i siada na środku."""
    if bare:
        return f"""
<header class="header header--bare">
  <div class="container header__inner">
    {logo_svg(depth, "header__logo")}
  </div>
</header>"""
    items = []
    for n in SITE["nav"]:
        ext = ' target="_blank" rel="noopener"' if n.get("external") else ""
        # Bieżąca sekcja jest oznaczona semantycznie, a nie klasą - `aria-current`
        # czytniki ekranu ogłaszają same, a CSS ma się po czym zaczepić.
        cur = ' aria-current="page"' if active and n["href"] == active else ""
        items.append('<li><a href="%s"%s%s>%s</a></li>'
                     % (esc(link(n["href"], depth)), ext, cur, esc(n["label"])))
    if active and active not in [n["href"] for n in SITE["nav"]]:
        # Adres sekcji zmieniono w site.json, a wywołanie header() zostało stare.
        # Bez tego zaznaczenie po prostu znika i nikt tego nie zauważa.
        raise SystemExit("header(active=%r) nie pasuje do żadnej pozycji nav "
                         "w content/site.json" % active)
    cta = SITE["cta"]
    return f"""
<header class="header">
  <div class="container header__inner">
    {logo_svg(depth, "header__logo")}
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu">
      <svg class="icon-open" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      <svg class="icon-close" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
    </button>
    <nav class="header__nav" id="nav" aria-label="Nawigacja główna">
      <ul>{''.join(items)}</ul>
      <div class="nav-cta"><a class="btn" href="{esc(link(cta['href'], depth))}">{esc(cta['label'])}</a></div>
    </nav>
    <div class="header__cta"><a class="btn" href="{esc(link(cta['href'], depth))}">{esc(cta['label'])}</a></div>
  </div>
</header>"""


def support_section(depth):
    s = SITE["support_block"]
    return f"""
<section class="section" id="wesprzyj">
  <div class="container">
    <div class="support">
      <div class="reveal">
        <p class="kicker kicker--crimson">{esc(s['kicker'])}</p>
        <p class="support__quote">{esc(s['quote'])}</p>
      </div>
      <div class="reveal" style="--reveal-delay:80ms">
        <p class="support__body">{esc(s['body'])}</p>
        <a class="btn" href="{esc(SITE['donate_url'])}" target="_blank" rel="noopener">{esc(s['button'])}</a>
        <div class="support__credit">
          <span>{esc(s['credit'])}</span>
          <a class="logo-chip" href="https://zrzutka.pl/" target="_blank" rel="noopener">
            <img src="{asset('assets/img/header__logo-2x.png', depth)}" alt="zrzutka.pl" width="104" height="32">
          </a>
        </div>
      </div>
    </div>
  </div>
</section>"""


def footer(depth):
    cards = []
    for loc in SITE["locations"]:
        p1, p2 = place_lines(loc["name"])
        cards.append(f"""<address>
        <span class="place">{p1}<span>{p2}</span></span>
        {esc(loc['street'])}<br>{esc(loc['city'])}
        <strong>{esc(loc['label'])}</strong>
      </address>""")
    links = "".join('<a href="%s">%s</a>' % (esc(link(l["href"], depth)), esc(l["label"]))
                    for l in SITE["footer"]["links"])
    return f"""
<footer class="footer">
  <div class="container">
    <div class="footer__top">
      <div class="footer__brand">
        {logo_svg(depth, "")}
        <span class="footer__nfz"><img src="{asset('assets/img/logo-nfz-3.png', depth)}"
             alt="Świadczenia finansowane ze środków Narodowego Funduszu Zdrowia" width="118" height="48" loading="lazy"></span>
      </div>
      {''.join(cards)}
    </div>
    <div class="footer__bottom">
      <p>{esc(SITE['footer']['copyright'])}</p>
      <nav aria-label="Stopka">{links}</nav>
    </div>
  </div>
</footer>"""


def cookie_notice(depth):
    c = SITE["cookie_notice"]
    links = " oraz ".join('<a href="%s">%s</a>' % (esc(link(l["href"], depth)), esc(l["label"]))
                          for l in c["links"])
    return f"""
<aside class="cookie" id="cookie-notice" hidden aria-label="Informacja o plikach cookies">
  <div class="cookie__inner">
    <p>{esc(c['text'])} {links}.</p>
    <button class="btn btn--sm" type="button" data-cookie-accept>{esc(c['accept'])}</button>
  </div>
</aside>"""


def page(**kw):
    depth = kw["depth"]
    ga = SITE.get("ga_id")
    analytics = ""
    if ga:
        group = kw.get("content_group", "inne")
        analytics = (
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>\n'
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
            "gtag('js',new Date());"
            f"gtag('config','{ga}',{{content_group:'{group}'}});</script>\n"
            f'<script src="{rel(depth)}js/analytics.js" defer></script>'
        )
    out = BASE
    repl = {
        "title": esc(seo_title(kw["title"])),
        "description": esc(seo_desc(kw.get("description", ""))),
        "canonical": esc(kw["canonical"]),
        "robots": kw.get("robots", "index, follow, max-image-preview:large"),
        "og_type": kw.get("og_type", "website"),
        "og_image": esc(kw.get("og_image") or (SITE["url"] + "/assets/img/logo_ql.jpg")),
        "meta_extra": kw.get("meta_extra", ""),
        "root": rel(depth),
        "head_extra": kw.get("head_extra", ""),
        "body": kw["body"],
        "analytics": analytics,
    }
    for k, v in repl.items():
        out = out.replace("{{%s}}" % k, v)
    return out


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return full


# --------------------------------------------------------------------------
# strony
# --------------------------------------------------------------------------

def stagger(n):
    """Jeden krok animacji dla całej strony: 80 ms na element, najwyżej trzy."""
    return ' style="--reveal-delay:%dms"' % (min(n, 3) * 80)


def post_card(p, depth, eager=False):
    img = p.get("image")
    media = ""
    if img:
        media = ('<div class="post-card__media"><img src="%s" alt="" width="600" height="375" '
                 '%s decoding="async"></div>'
                 % (asset("assets/img/" + img, depth),
                    'fetchpriority="high"' if eager else 'loading="lazy"'))
    excerpt = p.get("description") or ""
    return f"""<a class="post-card reveal"{stagger(p.get('_n', 0))} href="{esc(link(p['url'], depth))}">
  {media}
  <div class="post-card__body">
    <h3>{esc(p['title'])}</h3>
    <p>{esc(excerpt)}</p>
    <span class="post-card__more">Czytaj więcej {ARROW}</span>
  </div>
</a>"""


def contact_grid(depth):
    """Kafelki placówek plus karta formularza. Jeden blok, dwa miejsca:
    sekcja na stronie głównej i osobna strona /kontakt/."""
    cards = "".join(f"""<div class="card card--contact reveal" style="--reveal-delay:{min(n, 3) * 80}ms">
      <h3 class="h-card">{place_lines(loc['name'])[0]}<span>{place_lines(loc['name'])[1]}</span></h3>
      <address>{esc(loc['street'])}<br>{esc(loc['city'])}
        <a class="phone" href="{esc(loc['phone_href'])}">tel: {esc(loc['phone'])}</a>
        <span class="label">{esc(loc['label'])}</span>
        <span class="hours">{esc(loc['hours'])}</span>
      </address>
    </div>""" for n, loc in enumerate(SITE["locations"]))
    fc = HOME["contact"]["form_card"]
    return f"""<div class="contact-grid">
        {cards}
        <div class="card card--form reveal">
          <div>
            <h3 class="h-card">{esc(fc['title'])}</h3>
            <p>{esc(fc['text'])}</p>
          </div>
          <div>
            <div class="actions">
              {copy_email_btn("btn--ghost-light")}
              <span class="or">{esc(fc['divider'])}</span>
              <a class="btn" href="{esc(link(fc['secondary']['href'], depth))}">{esc(fc['secondary']['label'])}</a>
            </div>
          </div>
        </div>
      </div>"""


def contact_section(depth, heading="h2", flush=False):
    """Cała sekcja kontaktowa - jedno źródło dla strony głównej i dla /kontakt/.
    Zmiana tutaj zmienia oba miejsca naraz; na osobnej stronie różni je tylko
    poziom nagłówka (tam jest to `h1`), wygląd jest identyczny."""
    return f"""<section class="section{' section--flush' if flush else ''} section--tinted" id="kontakt">
    <div class="container">
      <div class="section-head reveal">
        <{heading} class="h-section">{esc(HOME['contact']['title'])}</{heading}>
      </div>
      {contact_grid(depth)}
    </div>
  </section>"""


def build_home():
    d = 0
    h = HOME["hero"]
    points = "".join("<li>%s</li>" % p for p in h["points"])
    trust = "".join('<span><b>%s</b> %s</span>' % (esc(t["strong"]), esc(t["rest"]))
                    for t in h["trust"])
    dis = HOME["diseases"]
    tiles = "".join(
        f'<div class="disease"><p class="disease__code">{esc(i["code"])}</p>'
        f'<p class="disease__name">{esc(i["name"])}</p></div>' for i in dis["items"])
    vals = "".join(
        f'<div class="value reveal" style="--reveal-delay:{min(n, 3) * 80}ms">'
        f'<div class="value__icon">{ICONS[v["icon"]]}</div>'
        f'<h3 class="h-card">{esc(v["title"])}</h3><p>{esc(v["text"])}</p></div>'
        for n, v in enumerate(HOME["values"]["items"]))
    m = HOME["mission"]
    body = f"""{header(d)}
<main id="main">

  <section class="hero">
    <div class="container hero__body">
      <div class="hero__grid">
        <div class="hero__col">
          <p class="kicker reveal">{esc(h['kicker'])}</p>
          <h1 class="reveal" style="--reveal-delay:80ms">{esc(h['title'])}</h1>
          <ul class="hero__points reveal" style="--reveal-delay:160ms">{points}</ul>
          <div class="btn-row reveal" style="--reveal-delay:240ms">
            <a class="btn" href="{esc(link(h['primary']['href'], d))}">{esc(h['primary']['label'])}</a>
            <a class="btn btn--ghost" href="{esc(link(h['secondary']['href'], d))}">{esc(h['secondary']['label'])}</a>
          </div>
          <a class="hero__phone reveal" style="--reveal-delay:240ms" href="{esc(h['phone']['href'])}">
            {esc(h['phone']['label'])} <b>{esc(h['phone']['number'])}</b>
          </a>
        </div>

        <div class="hero__media reveal reveal--media" style="--reveal-delay:160ms"
             data-video="{esc(h['video'])}"
             data-video-title="Hospicjum Domowe JANMED - film o opiece w domu pacjenta">
          <img src="{asset('assets/img/' + h['image'], d)}" alt="{esc(h['image_alt'])}"
               width="1600" height="886" fetchpriority="high" decoding="async">
        </div>
      </div>
    </div>

    <div class="hero__trust">
      <div class="container reveal" style="--reveal-delay:240ms">{trust}</div>
    </div>
  </section>

{support_section(d)}

  <section class="section section--dark" id="choroby">
    <div class="container">
      <div class="section-head reveal">
        <p class="kicker kicker--light">{esc(dis['kicker'])}</p>
        <h2 class="h-section">{esc(dis['title'])}</h2>
        <p class="lede" style="color:var(--on-dark-2);margin-top:20px">{dis['intro']}</p>
      </div>
      <div class="disease-grid reveal">{tiles}</div>
      <div class="note reveal">
        <span class="note__icon">{INFO}</span>
        <p>{dis['note']}</p>
      </div>
      <a class="nfz-link reveal" href="{esc(dis['nfz']['href'])}" target="_blank" rel="noopener">
        <img src="{asset('assets/img/' + dis['nfz']['image'], d)}" alt="{esc(dis['nfz']['alt'])}" width="84" height="34" loading="lazy">
      </a>
    </div>
  </section>

  <section class="section" id="wartosci">
    <div class="container">
      <div class="section-head reveal">
        <h2 class="h-section">{esc(HOME['values']['title'])}</h2>
      </div>
      <div class="values">{vals}</div>
    </div>
  </section>

  <section class="section section--dark section--misja" id="misja">
    <div class="container">
      <div class="mission">
        <div class="mission__text reveal">
          <p class="kicker kicker--light">{esc(m['kicker'])}</p>
          <h2 class="h-section">{esc(m['title'])}</h2>
          <blockquote class="mission__quote" style="margin-top:28px">{m['quote']}</blockquote>
          <p class="mission__author"><strong>{esc(m['author'])}</strong><span>{esc(m['role'])}</span></p>
        </div>
        <figure class="mission__portrait reveal reveal--media" style="--reveal-delay:80ms">
          <picture>
            <source srcset="{asset('assets/img/' + m['image'] + '.webp', d)}" type="image/webp">
            <img src="{asset('assets/img/' + m['image'] + '.png', d)}" alt="{esc(m['image_alt'])}"
                 width="900" height="1058" loading="lazy" decoding="async">
          </picture>
        </figure>
      </div>
    </div>
  </section>

  {contact_section(d)}

</main>
{footer(d)}
{cookie_notice(d)}"""

    write("index.html", page(
        depth=d, title=HOME["seo_title"], description=HOME["description"],
        canonical=SITE["url"] + "/", og_type="website", content_group="strona-glowna",
        og_image=SITE["url"] + "/assets/img/" + HOME["og_image"],
        body=body, head_extra=schema_org()))


def build_baza():
    d = 1
    for n, p in enumerate(POSTS):
        p["_n"] = n
    cards = "".join(post_card(p, d, eager=(n < 3)) for n, p in enumerate(POSTS))
    body = f"""{header(d, active="/baza-wiedzy/")}
<main id="main">
  <section class="page-hero page-hero--figure">
    <div class="page-hero__scrim" style="background:var(--ink)"></div>
    <div class="container page-hero__grid"
         style="--figure-w:520px;--figure-min-h:clamp(300px,40vh,420px);--figure-h:calc(var(--figure-min-h) + 100px);--figure-shift:48px">
      <div class="page-hero__inner reveal">
        <p class="kicker kicker--light">Hospicjum domowe</p>
        <h1>Baza wiedzy o Hospicjum</h1>
        <p class="lede" style="color:var(--on-dark-2);margin-top:20px">
          Odpowiedzi na pytania, które najczęściej słyszymy od rodzin pacjentów -
          o kwalifikację, skierowanie, koszty i codzienność opieki w domu.
        </p>
      </div>
      {hero_figure('baza-wiedzy-ksiazki.png', 'Stos książek o medycynie paliatywnej i opiece nad chorym', d)}
    </div>
  </section>
  <section class="section section--flush">
    <div class="container">
      <div class="post-grid">{cards}</div>
    </div>
  </section>
</main>
{support_section(d)}
{footer(d)}
{cookie_notice(d)}"""
    write("baza-wiedzy/index.html", page(
        depth=d, title="Baza wiedzy • Hospicjum Domowe JANMED",
        description="Baza wiedzy o hospicjum domowym: kwalifikacja, skierowanie, koszty, "
                    "czas oczekiwania i zakres opieki. Odpowiedzi zespołu JANMED.",
        canonical=SITE["url"] + "/baza-wiedzy/", content_group="baza-wiedzy",
        meta_extra='<link rel="alternate" type="text/plain" href="../llms.txt" title="Indeks treści dla asystentów AI">',
        head_extra=schema_archive(), body=body))


def build_post(p):
    d = 1
    others = [q for q in POSTS if q["slug"] != p["slug"]][:3]
    related = "".join(post_card(q, d) for q in others)
    cta = SITE["post_cta"]
    steps = "".join("<li>%s</li>" % esc(s) for s in cta["steps"])
    img = p.get("image")
    media = ""
    if img:
        media = ('<div class="page-hero__media"><img src="%s" alt="" width="1600" height="1000" '
                 'fetchpriority="high" decoding="async"></div>' % asset("assets/img/" + img, d))
    pub = p.get("published", "")
    meta_line = ('<p class="page-hero__meta"><time datetime="%s">Aktualizacja: %s</time></p>'
                 % (esc(p.get("modified") or pub), esc(fmt_date(p.get("modified") or pub)))) if pub else ""

    body = f"""{header(d, active="/baza-wiedzy/")}
<main id="main">
  <article>
    <section class="page-hero">
      {media}
      <div class="page-hero__scrim"></div>
      <div class="container">
        <div class="page-hero__inner reveal">
          <p class="kicker kicker--light">Hospicjum domowe</p>
          <h1>{esc(p['title'])}</h1>
          {meta_line}
        </div>
      </div>
    </section>

    <nav class="breadcrumb" aria-label="Okruszki">
      <div class="container">
        <ol>
          <li><a href="{esc(link('/', d))}">Strona główna</a></li>
          <li><a href="{esc(link('/baza-wiedzy/', d))}">Baza wiedzy</a></li>
          <li aria-current="page">{esc(p['title'])}</li>
        </ol>
      </div>
    </nav>

    <section class="section section--flush">
      <div class="container article-layout">
        <div class="prose">{markdown(p['body'], lambda s: asset('assets/img/' + s, d), lambda h: link(h, d))}</div>
        <aside class="aside">
          <div class="aside__card">
            <h3>{esc(cta['heading'])}</h3>
            <ol>{steps}</ol>
            <a class="btn" href="{esc(link(SITE['form_url'], d))}">{esc(cta['button'])}</a>
          </div>
          <div class="aside__card">
            <h3>Masz pytanie?</h3>
            <ol style="list-style:none;padding:0">
              {''.join('<li><a class="phone" href="%s" style="color:var(--ink);text-decoration:none;font-weight:500">%s - %s</a></li>' % (esc(l['phone_href']), esc(l['label']), esc(l['phone'])) for l in SITE['locations'])}
            </ol>
            {copy_email_btn("btn--ghost")}
          </div>
        </aside>
      </div>
    </section>

    <section class="section section--tight section--tinted">
      <div class="container">
        <div class="section-head reveal"><h2 class="h-section">Przeczytaj również</h2></div>
        <div class="post-grid">{related}</div>
      </div>
    </section>
  </article>
</main>
{support_section(d)}
{footer(d)}
{cookie_notice(d)}"""

    meta_extra = [
        '<meta property="article:published_time" content="%s">' % esc(p.get("published", "")),
        '<meta property="article:modified_time" content="%s">' % esc(p.get("modified") or p.get("published", "")),
        '<meta property="article:section" content="Hospicjum domowe">',
        '<link rel="alternate" type="text/markdown" href="index.md" title="Ta strona jako czysty markdown">',
    ]
    if img:
        dims = IMG_DIMS.get(img)
        if dims:
            meta_extra += ['<meta property="og:image:width" content="%d">' % dims[0],
                           '<meta property="og:image:height" content="%d">' % dims[1]]
        meta_extra.append('<meta property="og:image:alt" content="%s">' % esc(p["title"]))
    write("%s/index.html" % p["slug"], page(
        meta_extra="\n".join(meta_extra),
        depth=d, title=p.get("seo_title") or p["title"],
        description=p.get("description", ""),
        canonical="%s/%s/" % (SITE["url"], p["slug"]),
        og_type="article", content_group="artykul",
        og_image=(SITE["url"] + "/assets/img/" + img) if img else None,
        body=body, head_extra=schema_article(p)))


def build_page(slug):
    d = 1
    meta, md = front_matter(read("content/pages/%s.md" % slug))
    body = f"""{header(d)}
<main id="main">
  <section class="page-hero">
    <div class="page-hero__scrim" style="background:var(--ink)"></div>
    <div class="container">
      <div class="page-hero__inner reveal">
        <h1>{esc(meta['title'])}</h1>
      </div>
    </div>
  </section>
  <nav class="breadcrumb" aria-label="Okruszki">
    <div class="container">
      <ol>
        <li><a href="{esc(link('/', d))}">Strona główna</a></li>
        <li aria-current="page">{esc(meta['title'])}</li>
      </ol>
    </div>
  </nav>
  <section class="section">
    <div class="container">
      <div class="prose">{markdown(md, lambda s: asset('assets/img/' + s, d), lambda h: link(h, d))}</div>
    </div>
  </section>
</main>
{footer(d)}
{cookie_notice(d)}"""
    write("%s/index.html" % slug, page(
        depth=d, title=meta.get("seo_title") or meta["title"],
        description=meta.get("description", ""),
        canonical="%s/%s/" % (SITE["url"], slug),
        robots="noindex, follow" if slug in ("pliki-cookies", "polityka-prywatnosci") else "index, follow",
        content_group="prawne", head_extra=schema_page(meta["title"], slug),
        meta_extra='<link rel="alternate" type="text/markdown" href="index.md">', body=body))


# --------------------------------------------------------------- praca --
# Oferty pracy: lista pod /praca/, każda oferta pod /praca/<slug>/, formularz
# aplikacyjny na stronie oferty. Numer oferty leci do formularza w adresie,
# więc w skrzynce widać od razu, na co ktoś odpowiada.


def job_chips(j):
    """Trzy fakty, po których czyta się ofertę z listy: gdzie, na jakich
    warunkach, w jakim rytmie."""
    out = []
    for key in ("places", "employment", "schedule"):
        val = (j.get(key) or "").strip()
        if val:
            out.append('<li class="chip">%s</li>' % esc(val))
    return '<ul class="chips">%s</ul>' % "".join(out) if out else ""


def job_facts(j):
    """To samo, co pigułki na liście, tylko w panelu bocznym: etykieta i wartość."""
    rows = []
    for key, label in (("places", "Miejsce"), ("employment", "Forma współpracy"),
                       ("schedule", "Wymiar")):
        val = (j.get(key) or "").strip()
        if val:
            rows.append("<div><dt>%s</dt><dd>%s</dd></div>" % (label, esc(val)))
    return '<dl class="facts">%s</dl>' % "".join(rows) if rows else ""


def job_places(j):
    """Lista miejscowości z front matter - do pigułek i do filtra."""
    return [x.strip() for x in (j.get("places") or "").split(",") if x.strip()]


def job_card(j, depth, n=0):
    return f"""<a class="job-card reveal"{stagger(n)} data-places="{esc('|'.join(job_places(j)))}" href="{esc(link(j['url'], depth))}">
  <div>
    <h2>{esc(j['title'])}</h2>
    <p>{esc(j.get('description', ''))}</p>
    {job_chips(j)}
  </div>
  <span class="job-card__more">Zobacz ofertę {ARROW}</span>
</a>"""


def job_filters(jobs):
    """Filtr po miejscowości. Bez JS-u wszystkie oferty są widoczne, a pasek
    filtrów w ogóle się nie pokazuje - nie ma martwych przycisków."""
    places = []
    for j in jobs:
        for p in job_places(j):
            if p not in places:
                places.append(p)
    if len(jobs) < 2 or len(places) < 2:
        return ""
    buttons = ['<button class="filter is-on" type="button" data-filter="" '
               'aria-pressed="true">Wszystkie miejscowości</button>']
    for p in places:
        buttons.append('<button class="filter" type="button" data-filter="%s" '
                       'aria-pressed="false">%s</button>' % (esc(p), esc(p)))
    return ('<div class="filters reveal" data-job-filters hidden aria-label="Filtruj oferty po miejscowości" role="group">'
            + "".join(buttons) + "</div>")


def apply_block(j, depth):
    """Formularz aplikacyjny wstawiony na stronie oferty.

    Dopóki `recruitment.tally_embed` w content/site.json jest puste, strona
    pokazuje ścieżkę mailową - działa od pierwszego dnia. Po wklejeniu adresu
    osadzenia formularz pojawia się sam, bez zmian w kodzie."""
    r = SITE.get("recruitment", {})
    embed = (r.get("tally_embed") or "").strip()
    mail = r.get("email") or SITE["email"]
    mailto = "mailto:%s?subject=%s" % (mail, quote("Aplikacja: %s" % j["title"]))

    if embed:
        # Stanowisko i miejscowość lecą do formularza w adresie osadzenia -
        # Tally ma na nie pola ukryte, więc w zgłoszeniu widać, na co ktoś
        # odpowiada, bez pytania o to kandydata.
        params = {
            r.get("param_position", "stanowisko"): j.get("position") or j["title"],
            r.get("param_place", "lokalizacja"): (job_places(j) or [""])[0],
        }
        src = esc(embed + ("&" if "?" in embed else "?") + "&".join(
            "%s=%s" % (quote(k), quote(v)) for k, v in params.items() if v))
        intro = esc(r.get("intro", ""))
        form = f"""<iframe data-tally-src="{src}" loading="lazy" width="100%"
                height="640" frameborder="0"
                title="Formularz aplikacyjny - {esc(j['title'])}"></iframe>
        <noscript>
          <p>Formularz wymaga włączonego JavaScriptu. Możesz też wysłać CV
            na <a href="{mailto}">{esc(mail)}</a>.</p>
        </noscript>
        <p class="apply__fallback">Wolisz mailem? Wyślij CV na
          <a href="{mailto}">{esc(mail)}</a> z dopiskiem „{esc(j['title'])}”.</p>"""
    else:
        intro = ("Wyślij CV na adres poniżej, w tytule wiadomości wpisz "
                 "„%s”. Napisz też, w której miejscowości chcesz pracować "
                 "i od kiedy jesteś dostępny." % esc(j["title"]))
        form = f"""<div class="btn-row">
          {copy_email_btn("btn--ghost", mail)}
          <a class="btn" href="{mailto}">Napisz do nas</a>
        </div>"""

    return f"""<section class="section section--tight section--tinted" id="aplikuj">
  <div class="container">
    <div class="apply reveal" data-form="rekrutacja" data-oferta="{esc(j['slug'])}">
      <div class="apply__head">
        <h2 class="h-card">Aplikuj na to stanowisko</h2>
        <p>{intro}</p>
      </div>
      {form}
    </div>
  </div>
</section>"""


def build_kontakt():
    """Mała strona kontaktowa. Ta sama treść co sekcja na stronie głównej -
    ale pod własnym adresem, żeby „Kontakt" w menu prowadził do strony,
    a nie do skoku w środek strony głównej."""
    d = 1
    body = f"""{header(d, active="/kontakt/")}
<main id="main">
  {contact_section(d, heading="h1", flush=True)}
</main>
{footer(d)}
{cookie_notice(d)}"""
    write("kontakt/index.html", page(
        depth=d, title="Kontakt • Hospicjum Domowe JANMED",
        description="Kontakt do Hospicjum Domowego JANMED - Olkusz 698-887-816, "
                    "Pińczów i Kazimierza Wielka 535-043-985, biuro@janmed.pl. "
                    "Informacja i rejestracja 8:00-15:00.",
        canonical=SITE["url"] + "/kontakt/", content_group="kontakt",
        head_extra=schema_page("Kontakt", "kontakt"), body=body))


def build_jobs_index():
    d = 1
    if JOBS:
        cards = "".join(job_card(j, d, n) for n, j in enumerate(JOBS))
        lista = job_filters(JOBS) + '<div class="job-list" id="oferty">%s</div>' % cards
        lista += ('<p class="job-empty" hidden>Nie mamy teraz oferty w tej miejscowości. '
                  'Zobacz pozostałe albo napisz na %s.</p>' % esc(SITE["email"]))
    else:
        lista = f"""<div class="apply reveal">
        <h2 class="h-card">Nie prowadzimy teraz naboru</h2>
        <p style="margin-top:10px">Zgłoszenia i tak czytamy. Jeśli chcesz pracować
          w hospicjum domowym, napisz na {esc(SITE['email'])} - odezwiemy się,
          kiedy otworzymy nabór.</p>
        <div class="btn-row" style="margin-top:22px">{copy_email_btn("btn--ghost")}</div>
      </div>"""

    body = f"""{header(d, active="/praca/")}
<main id="main">
  <section class="page-hero page-hero--figure">
    <div class="page-hero__scrim" style="background:var(--ink)"></div>
    <div class="container page-hero__grid"
         style="--figure-w:560px;--figure-min-h:clamp(380px,54vh,540px);--figure-h:calc(var(--figure-min-h) + 40px)">
      <div class="page-hero__inner reveal">
        <p class="kicker kicker--light">Praca w hospicjum</p>
        <h1>Pracuj tam, gdzie widać sens</h1>
        <p class="lede" style="color:var(--on-dark-2);margin-top:20px">
          Wierzymy, że dobra opieka medyczna, wsparcie i czujność potrafią dać
          choremu i jego bliskim spokój na ostatniej drodze życia. Jeśli to jest
          również Twoje myślenie o tej pracy - zapraszamy do zespołu w Olkuszu,
          Pińczowie i Kazimierzy Wielkiej.
        </p>
      </div>
      {hero_figure('praca-zespol.png', 'Zespół hospicjum domowego JANMED', d)}
    </div>
  </section>
  <section class="section section--flush">
    <div class="container">{lista}</div>
  </section>
</main>
{footer(d)}
{cookie_notice(d)}"""
    write("praca/index.html", page(
        depth=d, title="Praca w hospicjum domowym • Hospicjum Domowe JANMED",
        description="Oferty pracy w Hospicjum Domowym JANMED - Olkusz, Pińczów, "
                    "Kazimierza Wielka. Lekarze, pielęgniarki, rehabilitanci, psycholodzy.",
        canonical=SITE["url"] + "/praca/", content_group="praca",
        head_extra=schema_jobs_index(), body=body))


def build_job(j):
    d = 2
    others = [q for q in JOBS if q["slug"] != j["slug"]][:3]
    pub = j.get("published", "")
    meta_line = ('<p class="page-hero__meta"><time datetime="%s">Ogłoszenie z %s</time></p>'
                 % (esc(pub), esc(fmt_date(pub)))) if pub else ""
    more = ""
    if others:
        more = f"""<section class="section section--tight">
    <div class="container">
      <div class="section-head reveal"><h2 class="h-section">Inne oferty</h2></div>
      <div class="job-list">{''.join(job_card(q, d, n) for n, q in enumerate(others))}</div>
    </div>
  </section>"""

    body = f"""{header(d, active="/praca/")}
<main id="main">
  <article>
    <section class="page-hero page-hero--figure">
      <div class="page-hero__scrim" style="background:var(--ink)"></div>
      <div class="container page-hero__grid"
           style="--figure-w:480px;--figure-min-h:clamp(320px,46vh,450px);--figure-h:calc(var(--figure-min-h) + 60px)">
        <div class="page-hero__inner reveal">
          <p class="kicker kicker--light">Oferta pracy</p>
          <h1>{esc(j['title'])}</h1>
          {job_chips(j)}
          {meta_line}
        </div>
        {hero_figure('praca-lekarze.png', 'Lekarz i pielęgniarka z zespołu hospicjum domowego', d)}
      </div>
    </section>

    <nav class="breadcrumb" aria-label="Okruszki">
      <div class="container">
        <ol>
          <li><a href="{esc(link('/', d))}">Strona główna</a></li>
          <li><a href="{esc(link('/praca/', d))}">Praca</a></li>
          <li aria-current="page">{esc(j['title'])}</li>
        </ol>
      </div>
    </nav>

    <section class="section section--flush">
      <div class="container article-layout">
        <div class="prose">{markdown(j['body'], lambda x: asset('assets/img/' + x, d), lambda h: link(h, d))}</div>
        <aside class="aside">
          <div class="aside__card reveal">
            <h3>{esc(j['title'])}</h3>
            {job_facts(j)}
            <a class="btn" href="#aplikuj">Aplikuj</a>
          </div>
          <div class="aside__card reveal">
            <h3>Masz pytanie?</h3>
            <ol style="list-style:none;padding:0;margin-bottom:18px">
              <li><a class="phone" href="{esc(SITE['locations'][0]['phone_href'])}"
                     style="color:var(--ink);text-decoration:none;font-weight:500">{esc(SITE['locations'][0]['label'])} - {esc(SITE['locations'][0]['phone'])}</a></li>
            </ol>
            {copy_email_btn("btn--ghost")}
          </div>
        </aside>
      </div>
    </section>

    {apply_block(j, d)}
    {more}
  </article>
</main>
{footer(d)}
{cookie_notice(d)}
{TALLY_BOOTSTRAP if (SITE.get("recruitment", {}).get("tally_embed") or "").strip() else ""}"""

    write("praca/%s/index.html" % j["slug"], page(
        depth=d, title=j.get("seo_title") or (j["title"] + " • Hospicjum Domowe JANMED"),
        description=j.get("description", ""),
        canonical="%s/praca/%s/" % (SITE["url"], j["slug"]),
        og_type="article", content_group="praca",
        head_extra=schema_job(j), body=body))


TALLY_BOOTSTRAP = """<script src="https://tally.so/widgets/embed.js" defer></script>
<script>
// Zapasowe wczytanie, gdyby skrypt Tally nie zdazyl podmienic src (adblock, wolna siec).
window.addEventListener('load', function () {
  setTimeout(function () {
    if (window.Tally) { Tally.loadEmbeds(); }
    var frames = document.querySelectorAll('iframe[data-tally-src]:not([src])');
    Array.prototype.forEach.call(frames, function (f) { f.src = f.dataset.tallySrc; });
  }, 1200);
});
</script>"""


def build_form():
    """Strona formularza. Hierarchia: najpierw formularz, potem wszystko inne -
    kto tu trafia, przyszedł go wypełnić, a nie czytać nagłówek."""
    d = 1
    loc = SITE["locations"][0]
    body = f"""{header(d, bare=True)}
<div class="form-page">
  <main id="main" class="form-page__body">
    <div class="container">
      <h1 class="form-page__title">Zgłoszenie pacjenta do hospicjum domowego</h1>
      <div class="form-embed" data-form="zgloszenie">
        <iframe data-tally-src="https://tally.so/embed/5B4vYb?alignLeft=1&amp;hideTitle=1&amp;transparentBackground=1&amp;dynamicHeight=1"
                loading="lazy" width="100%" height="600" frameborder="0"
                title="Formularz zgłoszeniowy do Hospicjum Domowego"></iframe>
        <noscript>
          <p>Formularz wymaga włączonego JavaScriptu.
            Możesz też napisać na <a href="mailto:{esc(SITE['email'])}">{esc(SITE['email'])}</a>
            lub zadzwonić: {esc(loc['phone'])}.</p>
        </noscript>
      </div>
      <p class="form-page__foot">
        <a href="{esc(link('/', d))}">&larr; Wróć na stronę główną</a>
        <span class="urgent">W sprawach pilnych zadzwoń:
          <a href="{esc(loc['phone_href'])}">{esc(loc['phone'])}</a></span>
      </p>
    </div>
  </main>
</div>
{TALLY_BOOTSTRAP}"""
    write("formularz-zgloszeniowy-do-hospicjum-domowego/index.html", page(
        depth=d, title="Formularz Zgłoszeniowy do Hospicjum Domowego • Hospicjum Domowe JANMED",
        description="Zgłoś pacjenta do Hospicjum Domowego JANMED - Olkusz, Pińczów, Kazimierza Wielka.",
        canonical=SITE["url"] + "/formularz-zgloszeniowy-do-hospicjum-domowego/",
        robots="noindex, follow", content_group="formularz", body=body))


def build_404():
    d = 0
    body = f"""{header(d)}
<main id="main">
  <section class="section" style="text-align:center;padding-block:clamp(96px,14vw,180px)">
    <div class="container">
      <p class="kicker">Błąd 404</p>
      <h1 class="h-section">Nie znaleźliśmy tej strony</h1>
      <p class="lede" style="margin:20px auto 34px">Być może adres się zmienił. Zajrzyj do bazy wiedzy albo wróć na stronę główną.</p>
      <div class="btn-row" style="justify-content:center">
        <a class="btn" href="{esc(link('/', d))}">Strona główna</a>
        <a class="btn btn--ghost" href="{esc(link('/baza-wiedzy/', d))}">Baza wiedzy</a>
      </div>
    </div>
  </section>
</main>
{footer(d)}"""
    write("404.html", page(depth=d, title="Nie znaleziono strony • Hospicjum Domowe JANMED",
                           description="", canonical=SITE["url"] + "/404.html",
                           robots="noindex, nofollow", content_group="404", body=body))


# --------------------------------------------------------------------------
# SEO
# --------------------------------------------------------------------------

MONTHS = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
          "sierpnia", "września", "października", "listopada", "grudnia"]


def fmt_date(iso):
    try:
        y, m, dd = iso[:10].split("-")
        return "%d %s %s" % (int(dd), MONTHS[int(m) - 1], y)
    except Exception:
        return iso


def schema_article(p):
    """Article + MedicalWebPage + BreadcrumbList, a dla wpisów pytaniowych FAQPage."""
    url = "%s/%s/" % (SITE["url"], p["slug"])
    article = {
        "@type": ["Article", "MedicalWebPage"],
        "@id": url + "#article",
        "headline": p["title"],
        "description": p.get("description", ""),
        "datePublished": p.get("published", ""),
        "dateModified": p.get("modified", "") or p.get("published", ""),
        "inLanguage": "pl-PL",
        "mainEntityOfPage": url,
        "isPartOf": {"@id": SITE["url"] + "/#website"},
        "about": {"@id": SITE["url"] + "/#organization"},
        "author": {"@id": SITE["url"] + "/#organization"},
        "publisher": {"@id": SITE["url"] + "/#organization"},
        "medicalAudience": ["Patient", "Caregiver"],
        "specialty": "PalliativeCare",
    }
    if p.get("image"):
        article["image"] = SITE["url"] + "/assets/img/" + p["image"]

    graph = [article, breadcrumb([
        ("Strona główna", SITE["url"] + "/"),
        ("Baza wiedzy", SITE["url"] + "/baza-wiedzy/"),
        (p["title"], url),
    ]), organization()]

    faq = faq_pairs(p["body"])
    if len(faq) >= 2:
        graph.append({
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [{
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            } for q, a in faq],
        })
    return ld(graph)


def faq_pairs(body, limit=8):
    """Nagłówki będące pytaniami + pierwszy akapit odpowiedzi."""
    pairs = []
    blocks = re.split(r"\n\s*\n", body.strip())
    for i, b in enumerate(blocks):
        m = re.match(r"^#{2,3}\s+(.*\?)\s*$", b.strip())
        if not m:
            continue
        answer = []
        for nxt in blocks[i + 1:]:
            t = nxt.strip()
            if t.startswith("#"):
                break
            t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
            t = re.sub(r"^\s*[-*]\s+", "", t, flags=re.M)
            t = re.sub(r"^\s*\d+\.\s+", "", t, flags=re.M)
            t = re.sub(r"[*`|]", "", t).replace("\n", " ").strip()
            if t:
                answer.append(t)
            if sum(len(x) for x in answer) > 300:
                break
        if answer:
            pairs.append((m.group(1).strip(), " ".join(answer)[:600].strip()))
        if len(pairs) >= limit:
            break
    return pairs


def breadcrumb(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": n, "name": name, "item": url}
            for n, (name, url) in enumerate(items, 1)
        ],
    }


def organization():
    return {
        "@type": ["MedicalOrganization", "LocalBusiness"],
        "@id": SITE["url"] + "/#organization",
        "name": SITE["name"],
        "alternateName": "JANMED",
        "url": SITE["url"] + "/",
        "email": SITE["email"],
        "medicalSpecialty": "PalliativeCare",
        "logo": {
            "@type": "ImageObject",
            "@id": SITE["url"] + "/#logo",
            "url": SITE["url"] + "/assets/svg/hospicjum-domowe-janmed-logo.svg",
        },
        "image": {"@id": SITE["url"] + "/#logo"},
        "areaServed": [{"@type": "City", "name": n} for n in
                       ("Olkusz", "Pińczów", "Kazimierza Wielka")],
        "availableService": {
            "@type": "MedicalTherapy",
            "name": "Opieka paliatywna i hospicyjna w domu pacjenta",
            "howPerformed": "Wizyty domowe lekarza, pielęgniarki, rehabilitanta i psychologa.",
        },
        "isAcceptingNewPatients": True,
        "location": [{
            "@type": "MedicalClinic",
            "@id": "%s/#%s" % (SITE["url"], slugify(l["name"])),
            "name": l["name"],
            "telephone": l["phone_href"].replace("tel:", ""),
            "openingHours": "Mo-Fr 08:00-15:00",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": l["street"],
                "postalCode": l["city"].split(" ")[0],
                "addressLocality": " ".join(l["city"].split(" ")[1:]),
                "addressCountry": "PL",
            },
        } for l in SITE["locations"]],
    }


def website():
    return {
        "@type": "WebSite",
        "@id": SITE["url"] + "/#website",
        "url": SITE["url"] + "/",
        "name": SITE["name"],
        "inLanguage": "pl-PL",
        "publisher": {"@id": SITE["url"] + "/#organization"},
    }


def slugify(t):
    t = t.lower()
    for a, b in zip("ąćęłńóśźż", "acelnoszz"):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def ld(graph):
    return ('<script type="application/ld+json">%s</script>'
            % json.dumps({"@context": "https://schema.org", "@graph": graph},
                         ensure_ascii=False, separators=(",", ":")))


def schema_org():
    return ld([organization(), website(), breadcrumb([("Strona główna", SITE["url"] + "/")])])


def schema_archive():
    url = SITE["url"] + "/baza-wiedzy/"
    return ld([
        {
            "@type": ["CollectionPage", "Blog"],
            "@id": url + "#collection",
            "name": "Baza wiedzy o hospicjum domowym",
            "url": url,
            "inLanguage": "pl-PL",
            "isPartOf": {"@id": SITE["url"] + "/#website"},
            "publisher": {"@id": SITE["url"] + "/#organization"},
            "hasPart": [{
                "@type": "Article",
                "headline": p["title"],
                "url": "%s/%s/" % (SITE["url"], p["slug"]),
                "datePublished": p.get("published", ""),
            } for p in POSTS],
        },
        breadcrumb([("Strona główna", SITE["url"] + "/"),
                    ("Baza wiedzy", url)]),
        organization(),
    ])


def schema_page(title, slug):
    url = "%s/%s/" % (SITE["url"], slug)
    return ld([
        {"@type": "WebPage", "@id": url, "name": title, "url": url,
         "inLanguage": "pl-PL", "isPartOf": {"@id": SITE["url"] + "/#website"}},
        breadcrumb([("Strona główna", SITE["url"] + "/"), (title, url)]),
    ])


def job_locations(j):
    """Miejsca pracy wybrane z placówek po nazwie miejscowości z front matter."""
    wanted = [x.strip().lower() for x in (j.get("places") or "").split(",") if x.strip()]
    out = []
    for loc in SITE["locations"]:
        city = " ".join(loc["city"].split(" ")[1:])
        if not wanted or city.lower() in wanted:
            out.append({
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": loc["street"],
                    "postalCode": loc["city"].split(" ")[0],
                    "addressLocality": city,
                    "addressCountry": "PL",
                },
            })
    return out


def schema_job(j):
    """JobPosting - to dzięki niemu oferta trafia do Google Jobs.
    Bez `datePosted` i `validThrough` Google jej nie pokaże."""
    url = "%s/praca/%s/" % (SITE["url"], j["slug"])
    posting = {
        "@type": "JobPosting",
        "@id": url + "#job",
        "title": j["title"],
        "description": markdown(j["body"]),
        "datePosted": j.get("published", ""),
        "employmentType": [x.strip() for x in
                           j.get("employment_type", "PART_TIME").split(",") if x.strip()],
        "hiringOrganization": {"@id": SITE["url"] + "/#organization"},
        "jobLocation": job_locations(j),
        "directApply": True,
        "industry": "Opieka zdrowotna",
        "inLanguage": "pl-PL",
        "url": url,
    }
    if j.get("valid_through"):
        posting["validThrough"] = j["valid_through"]
    return ld([posting,
               breadcrumb([("Strona główna", SITE["url"] + "/"),
                           ("Praca", SITE["url"] + "/praca/"),
                           (j["title"], url)]),
               organization()])


def schema_jobs_index():
    url = SITE["url"] + "/praca/"
    return ld([
        {"@type": "CollectionPage", "@id": url + "#collection",
         "name": "Praca w Hospicjum Domowym JANMED", "url": url, "inLanguage": "pl-PL",
         "isPartOf": {"@id": SITE["url"] + "/#website"},
         "publisher": {"@id": SITE["url"] + "/#organization"}},
        breadcrumb([("Strona główna", SITE["url"] + "/"), ("Praca", url)]),
        organization(),
    ])


MD_INTRO = ("<!-- Czysta treść w markdownie dla botów i asystentów AI. "
            "Źródło prawdy: content/ w repozytorium. -->\n")


def build_markdown_mirrors():
    """Każdy wpis i strona dostają bliźniaczy plik .md - czysty tekst bez HTML-a.
    LLM-y i narzędzia typu „wklej mi tę stronę" dostają treść bez szumu."""
    for p in POSTS:
        head = ["# " + p["title"], ""]
        if p.get("description"):
            head += ["> " + p["description"], ""]
        head += ["Źródło: %s/%s/" % (SITE["url"], p["slug"]),
                 "Aktualizacja: %s" % (p.get("modified") or p.get("published") or ""), "", "---", ""]
        write("%s/index.md" % p["slug"], "\n".join(head) + p["body"].strip() + "\n")
    for slug in ("polityka-prywatnosci", "pliki-cookies"):
        meta, md = front_matter(read("content/pages/%s.md" % slug))
        write("%s/index.md" % slug,
              "# %s\n\nŹródło: %s/%s/\n\n---\n\n%s\n" % (meta["title"], SITE["url"], slug, md.strip()))


def build_llms_txt():
    """llms.txt - konwencja indeksu treści dla asystentów AI."""
    lines = [
        "# Hospicjum Domowe JANMED",
        "",
        "> Bezpłatna opieka paliatywna i hospicyjna w domu pacjenta - dla dorosłych i dzieci.",
        "> Działamy w Olkuszu, Pińczowie i Kazimierzy Wielkiej oraz okolicach.",
        "> Świadczenia finansowane przez NFZ; opieka jest dla pacjenta i rodziny bezpłatna.",
        "",
        "Kontakt:",
    ]
    for l in SITE["locations"]:
        lines.append("- %s, %s, %s - tel. %s (informacja i rejestracja 8:00-15:00)"
                     % (l["name"], l["street"], l["city"], l["phone"]))
    lines += [
        "- E-mail: %s" % SITE["email"],
        "- Zgłoszenie pacjenta: %s/formularz-zgloszeniowy-do-hospicjum-domowego/" % SITE["url"],
        "- Wsparcie finansowe: %s" % SITE["donate_url"],
        "",
        "## Baza wiedzy",
        "",
    ]
    for p in POSTS:
        lines.append("- [%s](%s/%s/index.md): %s"
                     % (p["title"], SITE["url"], p["slug"], p.get("description", "")))
    if JOBS:
        lines += ["", "## Praca", "",
                  "- [Oferty pracy](%s/praca/)" % SITE["url"]]
        for j in JOBS:
            lines.append("- [%s](%s/praca/%s/): %s"
                         % (j["title"], SITE["url"], j["slug"], j.get("description", "")))
    lines += [
        "",
        "## Informacje formalne",
        "",
        "- [Polityka prywatności](%s/polityka-prywatnosci/index.md)" % SITE["url"],
        "- [Pliki cookies](%s/pliki-cookies/index.md)" % SITE["url"],
        "",
        "## Uwagi",
        "",
        "- Kwalifikacja wymaga zakończenia leczenia przyczynowego i skierowania od lekarza.",
        "- Pełna treść każdej podstrony jest dostępna pod tym samym adresem z końcówką index.md.",
        "- Treści mają charakter informacyjny i nie zastępują porady lekarskiej.",
        "",
    ]
    write("llms.txt", "\n".join(lines))

    full = ["# Hospicjum Domowe JANMED - pełna treść serwisu", "",
            "Wygenerowano z %s. Licencja: treść należy do Janmed Sp. z o.o." % SITE["url"], ""]
    for p in POSTS:
        full += ["", "---", "", "## " + p["title"],
                 "", "Adres: %s/%s/" % (SITE["url"], p["slug"]), "", p["body"].strip()]
    write("llms-full.txt", "\n".join(full) + "\n")


def build_sitemap():
    urls = [(SITE["url"] + "/", HOME.get("modified", str(date.today())), "1.0"),
            (SITE["url"] + "/baza-wiedzy/", str(date.today()), "0.8")]
    urls.append((SITE["url"] + "/kontakt/", str(date.today()), "0.7"))
    if JOBS:
        urls.append((SITE["url"] + "/praca/", str(date.today()), "0.6"))
    for j in JOBS:
        urls.append(("%s/praca/%s/" % (SITE["url"], j["slug"]),
                     j.get("published") or str(date.today()), "0.6"))
    for p in POSTS:
        urls.append(("%s/%s/" % (SITE["url"], p["slug"]),
                     p.get("modified") or p.get("published") or str(date.today()), "0.7"))
    for slug in ("polityka-prywatnosci", "pliki-cookies"):
        urls.append(("%s/%s/" % (SITE["url"], slug), str(date.today()), "0.2"))
    items = "".join(
        "\n  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>"
        % (u, m[:10], pr) for u, m, pr in urls)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s\n</urlset>\n' % items)
    ai_bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
               "Claude-SearchBot", "anthropic-ai", "PerplexityBot", "Perplexity-User",
               "Google-Extended", "Applebot-Extended", "meta-externalagent",
               "Amazonbot", "Bytespider", "CCBot", "cohere-ai", "MistralAI-User",
               "DuckAssistBot", "YouBot"]
    lines = ["# Zapraszamy wszystkie boty - także wyszukiwarki AI.",
             "# Rodziny szukają hospicjum w wyszukiwarkach i czatach; chcemy tam być.",
             "", "User-agent: *", "Allow: /", ""]
    for bot in ai_bots:
        lines += ["User-agent: %s" % bot, "Allow: /", ""]
    lines += ["Sitemap: %s/sitemap.xml" % SITE["url"],
              "", "# Indeks treści dla asystentów AI:",
              "# %s/llms.txt" % SITE["url"],
              "# %s/llms-full.txt" % SITE["url"], ""]
    write("robots.txt", "\n".join(lines))


# --------------------------------------------------------------------------

def copy_drafts():
    """Makiety robocze - tylko lokalnie (`python3 build.py --drafts`).
    Nie trafiają do artefaktu CI, więc nie ma jak przypadkiem ich opublikować."""
    src = os.path.join(ROOT, "drafts")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(OUT, "_drafts"))
    doc = os.path.join(ROOT, "docs", "design.html")
    if os.path.isfile(doc):
        write("_drafts/design.html", read("docs/design.html"))
    print("uwaga: dołączono drafts/ i docs/design.html → dist/_drafts/ (tylko podgląd lokalny)")


def copy_static():
    for d in ("assets", "css", "js"):
        src, dst = os.path.join(ROOT, d), os.path.join(OUT, d)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
    # CNAME musi lecieć w artefakcie, inaczej deploy kasuje custom domain
    domain = SITE["url"].replace("https://", "").replace("http://", "").strip("/")
    write("CNAME", domain + "\n")
    write(".nojekyll", "")


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    copy_static()
    if "--drafts" in sys.argv:
        copy_drafts()
    build_home()
    build_baza()
    build_kontakt()
    build_jobs_index()
    for j in JOBS:
        build_job(j)
    for p in POSTS:
        build_post(p)
    for slug in ("polityka-prywatnosci", "pliki-cookies"):
        build_page(slug)
    build_form()
    build_404()
    build_sitemap()
    build_markdown_mirrors()
    build_llms_txt()

    n = sum(len(files) for _, _, files in os.walk(OUT))
    pages = sum(1 for r, _, fs in os.walk(OUT) for f in fs if f.endswith(".html"))
    print("dist/ gotowe - %d plików, %d stron HTML" % (n, pages))


if __name__ == "__main__":
    sys.exit(main())
