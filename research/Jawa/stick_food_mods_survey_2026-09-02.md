# Stick food mods survey — STICK_FOOD_INGEST_1 (2026-09-02)

## 1. Active mod list check

`/mnt/d/Luke/dev/Rimworld/infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (written
2026-09-01 21:29) lists **both** candidate packageIds active, back to back in load order:

```
<li>badoaks.meatonastick</li>
<li>badoaks.meatonastick.expansion</li>
```

This confirms the owner's "I think there are two of them" — there are exactly two, and both
are currently live in the campaign's full mod list. They are not two competing mods by
different authors; they are one base mod plus its own official expansion, same author.

## 2. Steam Workshop identification

Steam Workshop direct-fetch (WebFetch) was rate-limited ("too many requests") on every
attempt this session, including retries and a wayback-machine fallback (wayback fetch is
blocked entirely for this tool). Findings below come from WebSearch result snippets and a
secondary fan-aggregator mirror (rimworld.2game.info, itself 403'd to direct fetch — titles
only, taken from search-result link text). Nothing here is a raw primary-source page read;
treat file-size and "removed for guideline violation" claims as UNCERTAIN (flagged below).

| | Meat on a Stick | Meat on a Stick - Expanded |
|---|---|---|
| Steam Workshop ID | 3435027361 | 3577333297 |
| packageId (active) | `badoaks.meatonastick` | `badoaks.meatonastick.expansion` |
| Author | BadOaks | BadOaks |
| Version tag (per 2game.info mirror titles: "Meat on a Stick 1.6" / "Meat on a Stick - Expansion 1.6") | 1.6 | 1.6 |
| What it adds | One simple-meal variant, meat-only, craftable only at a campfire. Explicitly "no real advantages over a regular simple meal" — RP/visual-interest only. | Marginal expansion: adds a new item, "Skewers," craftable from any wood (or any modded material tagged "Woody," e.g. bones) at a crafting spot. Adds more "-on a stick" recipes (meat and reportedly other ingredients) cooked at the campfire using skewers. |
| Est. scope | Very small — plausibly 1 ThingDef (meal) + 1 RecipeDef + a texture, nothing else | Small — 1 new ThingDef (Skewer) + a handful of additional RecipeDefs + textures for the new stick-food variants |
| License / open-source status | **No license statement or source-code link found anywhere** (searched WebSearch + GitHub for "badoaks"; no matching GitHub account or repo exists). Standard Steam Workshop default: content stays the author's; no explicit permissive license to ingest. | Same — no license or repo found. |
| Dependencies noted | None found | Implicitly depends on / patches the base "Meat on a Stick" mod (it is an expansion of it) |
| Incompatibility notes | One search snippet claimed the workshop page shows an "incompatible" flag; another (separate) snippet for the Expanded mod claimed it was "removed from Steam Community for violating guidelines." **The second claim is unconfirmed and looks like a search-summarizer artifact** — no other source corroborates it, and the mod is verifiably active and loading in the campaign's own ModsConfig right now, which is inconsistent with being pulled from the Workshop. Do not act on it without a direct Steam page read. |

## 3. Ingest scope (per the owner's framing: "whatever the campaign uses")

Both are active — ingest scope is **both mods' full functional content**: the base meat-on-a-
stick simple meal + the expansion's skewer item and its additional stick-food recipes. This
matches "I think there are two of them."

## VERDICT

- **Which mods, active or not**: `badoaks.meatonastick` (Meat on a Stick) and
  `badoaks.meatonastick.expansion` (Meat on a Stick - Expanded), both by author BadOaks —
  both **ACTIVE** in `ModsConfig.FULL.LATEST.xml` right now. Ingest scope = both.
- **Ingest complexity — base mod**: trivial. One meat-only simple-meal ThingDef + one
  campfire RecipeDef, no mechanical bonus over vanilla simple meals — re-authoring the XML
  from scratch is a same-day job; the only asset of real value to carry over is the meal
  texture (art call, see license note).
- **Ingest complexity — expansion**: small. One new Skewer ThingDef (wood/"Woody"-tagged
  material input) plus a handful of additional stick-food RecipeDefs; still reimplementable
  from a description alone in a day or two, art aside.
- **License status**: **UNKNOWN / effectively none** — no GitHub, no in-description license
  grant found for either mod under author BadOaks. Default Steam Workshop terms apply: the
  author retains rights to their content. Recipes/ThingDef mechanics are thin/functional and
  safe to reimplement independently; the sprite art is the one asset that should either be
  regenerated in-house (per `generating-rimworld-sprites`) or require the author's explicit
  permission before literal reuse — do not copy BadOaks' texture files into our own mod
  without that.

## UNKNOWN

- Exact defName list, recipe count, and texture inventory for both mods — Steam page reads
  were rate-limited all session; nobody has opened the actual mod archives on disk to confirm
  def/texture counts directly. If a hard ingest spec is needed, pull the two mods' folders
  from the Steam Workshop content cache (or `deploy_custom_mods.py`-visible mod path) and read
  the XML directly rather than trusting this survey's def-count estimates.
- Whether "Meat on a Stick - Expanded" was ever actually pulled from the Workshop for a
  guidelines violation — one search snippet claimed this, uncorroborated, and inconsistent
  with the mod loading live in the campaign today. Needs a direct Steam page read to resolve.
- Precise file sizes for both mods (one unverified snippet claimed 201.655 KB for the
  expansion; not independently confirmed).
