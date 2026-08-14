# REFRESH.md — what to do after changing the mod list

**Every generated artefact in this project is a snapshot of ONE mod set.** Add a
mod and they do not break — they quietly start describing a game that no longer
exists. Silently stale data is worse than missing data, because it still answers
questions.

**The command, the dependency order, whether you need a game load, and how to take
a fresh live dump are in `skills/rimworld-load-round/SKILL.md` §5.**

```bash
python src/RimMandrake/Utils/refresh.py              # changes nothing; prints what is stale and its cost
python src/RimMandrake/Utils/refresh.py --patches    # regenerate + validate the armoury patches
```

It fingerprints the active mod list **including load order** — RimWorld resolves
def overrides by order, so the same mods reordered really is a different game —
and compares that against a stamp in `observed/2026-08-13/inventory/GENERATED_FROM.json` and
against the live dump's own manifest.

This file holds what is specific to *what* you added.

## Adding weapon mods specifically (ship weaponry)

The armoury generator is **idempotent under roster change**, deliberately. It
maps each old damage value onto its target band by a *fixed function of the
value*, not by rank among current members.

That distinction is load-bearing. The first implementation ranked whatever was
installed and laid it across the band, so **adding one new blaster shifted the
assigned damage of every existing blaster**. Install a ship-weapons pack, re-run,
and the entire armoury churns — values move for defs nobody touched, and the
diff is unreadable.

With fixed anchors, new defs slot in and existing defs hold still. Verified: two
consecutive runs are byte-identical.

**When you add ship weaponry, expect to:**
1. Take a fresh dump (new weapons are invisible until you do).
2. Check whether the new guns land in an existing rung. `SOURCE_RANGE` in
   `gen_armoury_patch.py` assumes the vanilla-ish input range per rung; a mod
   whose turbolaser already does 500 will be **clamped**, not extrapolated — by
   design, so one outlier cannot drag a rung, but it does mean genuinely
   ship-scale mods may need their own rung.
3. Re-run `compare_ladder.py` to see where everything sits afterwards.

## Adding xenotypes specifically

Xenotypes mostly add `XenotypeDef`, `GeneDef` and pawnkinds rather than weapons,
so the armoury patches are unaffected. What *does* move:

- `observed/2026-08-13/inventory/` — if the pack adds animals or races.
- The **live dump**, and therefore `validate_patch.py --live`. A patch you write
  against a new xenotype's defs cannot be validated until the dump includes it.
- `vendor/wisdom/def_override_clusters.md` — new mods mean new contested defNames.

## Rebuilding during a debug configuration

Never capture a **live dump** while mods are pulled to isolate a bug — see
`skills/rimworld-load-round/SKILL.md` §5. Offline artefacts are cheap and
self-correcting, so rebuild those freely, but record why:

```bash
python src/RimMandrake/Utils/refresh.py --offline --note "VSIE pulled temporarily for debugging"
```

The note is stored in `GENERATED_FROM.json` and printed on every status run. Six
months later the hash only tells you the mod set differed; the note tells you it
was deliberate and temporary.
