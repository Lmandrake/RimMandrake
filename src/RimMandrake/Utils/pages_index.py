#!/usr/bin/env python3
"""pages_index.py: the one list of the pages that a person reads, and the line at the top of each that links to the others.

Census and plan: design/specs/2026-11-24-monitors-consolidated/ (census.md, plan.md). A page in KEPT prints
crossref_md(<its key>) or crossref_html(<its key>) as its first line under the title. Augur's FLEET_NOW draws the same
links from its own config (D:\\ClaudeWork\\augur\\config\\dashboard.json `links`), because Augur is another repo.
To add or remove a page, edit KEPT here and the Augur config links, and say so in census.md.

    python3 src/RimMandrake/Utils/pages_index.py      prints the markdown line for every page
"""
import html

# key -> (label, the full Windows path, the question that the page answers)
KEPT = {
    "fleet": ("FLEET_NOW", r"D:\ClaudeWork\augur\dashboard\FLEET_NOW.md",
              "what is running, each account, each machine"),
    "maturation": ("MATURATION_NOW", r"D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW.md",
                   "what needs you, what each mod is doing"),
    "detail": ("MATURATION_DETAIL", r"D:\ClaudeWork\rimmandrake\conductor\MATURATION_DETAIL.md",
               "the lists behind MATURATION_NOW"),
    "codebase": ("CODEBASE_NOW", r"D:\ClaudeWork\rimmandrake\conductor\CODEBASE_NOW.html",
                 "which code is clean"),
    "ops": ("ops digest", r"D:\ClaudeWork\rimmandrake\ops_watch\digest.md",
            "alarms and health readings, for Operations"),
}


def _others(self_key):
    if self_key not in KEPT:
        raise KeyError("pages_index: %r is not a kept page (KEPT has %s)" % (self_key, ", ".join(KEPT)))
    return [(k, v) for k, v in KEPT.items() if k != self_key]


def crossref_md(self_key):
    """-> one markdown line that names every other kept page by its full Windows path."""
    return "Other pages: " + " · ".join("%s `%s` (%s)" % (lab, path, q) for _, (lab, path, q) in _others(self_key))


def crossref_html(self_key):
    """-> one HTML paragraph with the same links (file:/// links open the page; the path is shown as text)."""
    parts = []
    for _, (lab, path, q) in _others(self_key):
        href = "file:///" + path.replace("\\", "/")
        parts.append("<a href='%s'>%s</a> <code>%s</code> (%s)" % (
            html.escape(href, quote=True), html.escape(lab), html.escape(path), html.escape(q)))
    return "<p class='m' style='font-size:12.5px'>Other pages: %s</p>" % " · ".join(parts)


if __name__ == "__main__":
    for k in KEPT:
        print("%-10s %s" % (k, crossref_md(k)))
