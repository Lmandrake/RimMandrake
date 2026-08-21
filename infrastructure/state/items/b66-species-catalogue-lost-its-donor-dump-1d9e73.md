## spec
Escalated by BUILD (`e4d6040`, `f6bed75`), routed by REP. **B66's premise —
"one file, one re-run, one redeploy" — is false, and the way it is false was
nearly expensive.**

BUILD fixed three code defects including one not in the spec: a `KeyError:
'GS_Primitive'` that stopped the generator dead, because `main` looked genes up
in the dump with a bare `g[n]` and the donors' genes left the dump when the
donors left the mod list.

🔴 **The crash was the only thing protecting us.** With it fixed the run got
further and hit the real defect: `pick_species` reads species from the DUMP and
has **no on-disk fallback**, so with the donors switched off it builds **57
species where the mod ships 69** — Herglic, Defel, Ithorian, KelDor, Mirialan,
Rakata, SithMassassi and more. A partial run had already overwritten six def
files at 57 species before BUILD caught it, over a mod **live at slot 562**.
Reverted; HEAD is 69, tree clean. BUILD added `_guard_species_regression`,
which refuses to write a smaller catalogue and prints the repair. ⛔ **Do not
weaken that guard to get a build out.**

**Your call, two routes:**
1. **Give `pick_species` the same on-disk fallback `_gene_exists` already has.**
   Offline, no load, and it permanently removes the donor dependency this mod
   exists to break. **BUILD's recommendation, and REP's.**
2. Re-enable the two donors, take a dump with them active, regenerate, switch
   them off. Costs a full load and restores the dependency we are trying to end.

Until this is chosen, the four magenta species stay magenta — Gand, Selkath,
female Chagrian, Jawa mask. That is the outcome D-CHK2 existed to avoid; BUILD
judged it better than shipping a mod twelve species short, and REP agrees.

## verify
the generator produces 69 species with the donors inactive, and
`_guard_species_regression` is still in place and still refuses a shrink.

## criteria
69 species present live with the donors off, and the four magenta cases render.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

done — **RULING: NEITHER ROUTE. Both are aimed at a defect that is not there.**
🔴 **Measured at `e4d6040`, clean tree, by calling the analysis functions only
(never `main`, which writes).** The escalation's premise does not survive it.

`pick_species` **already has the disk fallback.** `index_donors()` indexes
**513** donor defs off disk and the species resolve from it fine. The 57/65
split is real; the stated cause is not. What it actually skips:

| species | reason |
|---|---|
| Miraluka | dropped by owner ruling — **correct, not a defect** |
| Ithorian · KelDor · Mirialan | gene `Force_Gene_LatentForceUser` does not resolve |
| Rakata | gene `OuterRim_ForceInsensitive` does not resolve |
| SithMassassi | gene `OuterRim_ForceAdept` does not resolve |
| Defel | gene `guy762_AbilityGene_cloak` does not resolve |
| Herglic | "source carries no genes" — **separate cause, NOT measured. Do not assume.** |

⇒ Roster is **65, not 69** — a third number, and the 69 in B66 and in this
item is itself unverified. **Establish what the mod actually ships before
treating any count as a target.**

🔴 **ROUTE 2 IS REFUTED, and this is the load it saves.** I walked all three
donor trees for the four named genes. The three Force genes are **in none of
them** — not BTD, not SWX, not Outer Rim. They belong to a mod that is not a
donor. ⇒ Re-enabling the donors and re-dumping **cannot** surface them, so a
full load buys nothing for 5 of the 7. Do not spend it.
🔑 `guy762_AbilityGene_cloak` IS on disk, at
`SWX/1.5/AdditionalMods/KotORWeapons/Defs/AbilityDefs_defelcloaking.xml` — a
path `donor_xml_files` **deliberately skips** (`AdditionalMods`, and `1.5`).
So Defel is recoverable offline, in `donor_xml_files`, **not** in `pick_species`.

⇒ **BUILD, do this instead:**
1. **Skipping the 5 Force-gene species is CORRECT behaviour and stays.** A gene
   that resolves nowhere would ship a dangling reference. The generator refusing
   is the guard working twice.
2. Widen `donor_xml_files` to **INDEX** `AdditionalMods` (and check `Common` /
   `Common_Old`, which D-CHK2 already proved hold real content). ⛔ **Indexing
   is not copying** — the skip list exists to stop us copying conditional
   folders, and that reason still stands for the copier.
3. Measure Herglic. One species, one cause, currently unknown.
4. Re-derive the true roster count and put it in the item.
⛔ **Do not weaken `_guard_species_regression`.** Agreed, and it reads correctly
— it runs before any `write_xml`.

📌 **The design question underneath, and it is mine: those five species want
FORCE-SENSITIVITY genes we do not have.** This is a Jawa scavenger campaign on
a desert world; latent Force users are not content I would add on purpose. ⇒
**Ruling: strip the missing Force genes from those five species and build them
without.** They are species, not Jedi. If that lands them clean, the roster
recovers 5 of 7 with no load and no new mod. **Do not add a Force mod to satisfy
a gene reference** — that is a dependency the campaign never asked for.

⚠️ **B66's "one file, one re-run, one redeploy" was mine and it was wrong.**
BUILD was right to stop. The four magenta species stay magenta meanwhile, and
that remains the better trade.

━━━ 🔴 **OWNER RULING 2026-08-15 — SUPERSEDES THE ABOVE AND GENERALISES IT** ━━━
*"Remove any genes from our implementation of the xenotypes that aren't
supported in our mod at this time. We will investigate what to do later."*
⇒ Not just the Force genes, and not just these six species: **ANY gene that
does not resolve is stripped, and the species is BUILT WITHOUT IT.** Skipping
a species because one gene is missing is no longer correct behaviour — it is
the behaviour being overturned. **A species is never dropped for a gene again.**

**Measured 2026-08-15 at `e4d6040`, the complete set — 4 genes, 6 species,
exactly one bad gene each. Nothing is hidden behind the skip message's
`missing[:3]` truncation; I enumerated the full lists.**

| gene to strip | species |
|---|---|
| `Force_Gene_LatentForceUser` | Ithorian · KelDor · Mirialan |
| `OuterRim_ForceAdept` | SithMassassi |
| `OuterRim_ForceInsensitive` | Rakata |
| `guy762_AbilityGene_cloak` | Defel |

✅ **Stripping is SAFE, and I measured that rather than assuming it** — the
failure mode would be a species reduced to a bald human:

```
Defel        18 -> 17 genes   head-forcer 1 -> 1
Ithorian     16 -> 15         1 -> 1
KelDor       15 -> 14         1 -> 1
Mirialan     11 -> 10         0 -> 0   (pre-existing, D-CHK2's class)
Rakata        7 ->  6         1 -> 1
SithMassassi 14 -> 13         0 -> 0   (pre-existing)
```
**No species empties, and not one loses its head-forcing gene.** Mirialan and
SithMassassi had none before the strip either — that is D-CHK2's separate
finding and this ruling neither causes nor fixes it.

⇒ Roster recovers **57 → 63** of the 64 buildable (65 less Miraluka's owner
drop). **Herglic stays out** on "source carries no genes", a different and
still-unmeasured cause. Do not let the recovery hide it.

⇒ ⛔ **DEMOTED BY THIS RULING: widening `donor_xml_files` to index
`AdditionalMods`.** I directed it an hour ago to rescue Defel's cloak gene from
`SWX/1.5/AdditionalMods/KotORWeapons/`. Under the owner's ruling that gene is
**stripped, not rescued**, so the widening is no longer B66 work. It is a real
finding and keeps — `Common`/`Common_Old` demonstrably hold content D-CHK2
needed — but it belongs to the later investigation. **Do not do it inside B66.**

✅ **RE-TESTED 2026-08-15 against CHECK's empty-dump warning, and it HOLDS.**
CHECK found **79 of the 529 def-type files in the dump are EMPTY** — for those
types, "absent from the dump" is UNMEASURED, not absent, so any ruling resting
on absence needed re-testing. This one did, and it survives:
- `GeneDef.json` is **16,600,229 bytes** — richly populated, NOT one of the 79.
  All four genes return **0 hits** in it. Their absence is a real measurement.
- 🔑 `AbilityDef.json` **IS** empty (44 bytes), and `guy762_AbilityGene_cloak`
  lives on disk in a file named `AbilityDefs_defelcloaking.xml` — which looks
  exactly like the trap. It is not: the def is declared `<GeneDef>`, so it is
  checked against the populated `GeneDef.json`. **The filename is misleading and
  the def type is what counts.**
⇒ The strip list is unchanged. Recorded because a ruling that was re-tested and
held is worth more than one that was never questioned.

📌 **What "investigate later" needs, so file it now rather than re-deriving it:**
the four genes above, what each did, and which mod would supply it. Parked in
`design/V2_DREAMS.md`. **BUILD: emit the strip list as generator OUTPUT** — a
printed line per stripped gene — so the record is produced by the run and never
drifts from what shipped.
