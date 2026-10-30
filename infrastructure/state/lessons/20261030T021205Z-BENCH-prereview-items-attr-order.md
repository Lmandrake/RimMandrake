prereview.py reads ITEMS with the regex <script id="ITEMS"[^>]*>, so a block written as <script type="application/json" id="ITEMS"> is reported as 'no readable ITEMS block' even though it is valid HTML. Either put id first or loosen ITEMS_RE to match id anywhere in the tag. Hit on the 2026-10-30 mineral matrix rebuild.
home: src/RimMandrake/Utils/art/prereview.py
