# ALPHA_FAMILY_SOURCE_REVIEW_1 — study every Alpha mod: leverage, be inspired, broaden

Owner, 2026-09-06: *"let's make a ticket to look at all the alpha biome mods not just to
leverage their capabilities but be inspired by them and broaden them. Do they have a
public git we can examine?"* — Yes: **`https://github.com/juanosarg/AlphaBiomes`** and
**`https://github.com/juanosarg/AlphaAnimals`** (juanosarg = Sarg Bjornson, the author;
C# source included). Sibling repos under the same account (Alpha Genes, Alpha Memes,
Alpha Mechs, Alpha Prefabs…) — enumerate them from `github.com/juanosarg?tab=repositories`.

## spec
1. **Inventory the family**: which Alpha mods are in our stack (ModsConfig, MEASURED) and
   which are not; for each repo, the license (borrowing design and def-identities is our
   precedent — never shipped code or art files; check whether the source license changes
   that for C#).
2. **Catalog the MECHANICS, not the content** — every C# comp/worker that does something
   the base game can't, e.g. (seen today): the Agarilux Prime's spore-cloud attack, the
   Forsaken fog's darkness/accuracy mechanic, the Gelatinous terrain attacks
   (slime-in-eyes), the slime compressor, the Mycotic spore diseases, the Darkbeast's
   sun-blocking mechanites, Alpha Animals' abilities (quill volleys, gas emitters,
   burrowing, hydrogen floaters). Table: comp class · what it does · which of OUR sheets
   wants it · effort to replicate/generalize.
3. **"Replicate ourselves with other similar functions"** (owner): for each mechanic worth
   owning, propose our generalized version under the tier grammar (`RSW_`/`RUT_`) —
   e.g. a generic *active-defender plant* comp (spore cloud / gas / sap / lure) that the
   Rot's guardian mushrooms, the Contagion's aberrations and the Deeps' Lantern can all
   use; a generic *environmental-attack terrain* comp; a generic *sensor-degrading fog*
   weather comp.
4. **Broaden**: what each Alpha biome/creature concept could become on Ash'karr beyond
   the donor's intent — feed the sheets' Owed lists.
5. Output as DATA (a mechanics table) + a short design memo; card anything that needs the
   owner (licensing, scope).

## verify
The table exists with defNames/classes cited from the repos; the owner has ruled which
mechanics we replicate; nothing from the repos is copied into src/ without a license
ruling.
