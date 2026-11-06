#!/usr/bin/env python3
"""Selftest: the Baroque Biomes list page tells the biome truth (BAROQUE_LIST_PAGE_REDRAW_UMBRA_AS_BIOME).

design/RimMandrake/baroque_biomes_list_2026-10-19.html once listed the retired RUT_FuelSnows as a
live biome and called RUT_Umbra a "byte-for-byte behavioural duplicate" to be deleted. The owner
renamed the land back to RUT_Umbra, the Auroral Umbra (card 2026-10-19), and it is a painted world
biome; a sea IS its floor (owner 2026-10-28), so no RM_SeabedFloor* def is a biome row or card.
Source of the repair: design/RimMandrake/biome_name_provenance_audit_2026-10-28.md.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAGE = ROOT / "design/RimMandrake/baroque_biomes_list_2026-10-19.html"


class Cards(HTMLParser):
    """Collect section ids, table-row first-cell anchors, and each card's text."""

    def __init__(self):
        super().__init__()
        self.card_ids, self.row_links, self.cards = [], [], {}
        self._card, self._in_tr, self._td = None, False, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and a.get("id"):
            self._card = a["id"]
            self.card_ids.append(self._card)
            self.cards[self._card] = ""
        elif tag == "tr":
            self._in_tr, self._td = True, 0
        elif tag == "td" and self._in_tr:
            self._td += 1
        elif tag == "a" and self._in_tr and self._td == 1 and a.get("href", "").startswith("#"):
            self.row_links.append(a["href"][1:])

    def handle_endtag(self, tag):
        if tag == "section":
            self._card = None
        elif tag == "tr":
            self._in_tr = False

    def handle_data(self, data):
        if self._card:
            self.cards[self._card] += data


def main():
    text = PAGE.read_text(encoding="utf-8")
    p = Cards()
    p.feed(text)
    fails = []
    if not p.card_ids or not p.row_links:
        fails.append("instrument blind: no cards or table rows parsed")
    if re.search(r"(?i)fuel\s*snows", text):
        fails.append("page still names RUT_FuelSnows / Fuel Snows")
    if "RUT_Umbra" not in p.card_ids or "RUT_Umbra" not in p.row_links:
        fails.append("RUT_Umbra missing from the table or the cards")
    else:
        card = p.cards["RUT_Umbra"]
        if "Auroral Umbra" not in card:
            fails.append("RUT_Umbra card not titled the Auroral Umbra")
        if not re.search(r"\bpainted\b", card) or re.search(r"(?i)\bnot painted\b", card):
            fails.append("RUT_Umbra card does not say it is a painted biome")
        if re.search(r"(?i)duplicate|\bcompat\b", card):
            fails.append("RUT_Umbra card still calls it a duplicate")
    floors = [i for i in p.card_ids + p.row_links if i.startswith("RM_SeabedFloor")]
    if floors:
        fails.append(f"sea floors listed as biomes: {floors}")
    if len(set(p.card_ids)) != len(p.card_ids):
        fails.append("duplicate card ids")
    dead = [h for h in p.row_links if h not in p.card_ids]
    if dead:
        fails.append(f"table rows link to missing cards: {dead}")
    for f in fails:
        print("FAIL:", f)
    print(f"{'FAIL' if fails else 'PASS'}: {len(p.row_links)} rows, {len(p.card_ids)} cards")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
