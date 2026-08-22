## spec
🔴 **OWNER, 2026-08-22:** *"audits all available xenotypes to consider which of them may
feasibly be candidates for the big & tall gene that allows them to wield 'big' weapons
including warcasket weapons."*

**139 `XenotypeDef`s are in the frozen capture.** The deliverable is a reviewed shortlist:
which of them could plausibly carry a size/stature gene, with a reason per candidate, for
the owner to rule on.

## 🔴 STEP ONE IS NOT THE AUDIT — IT IS PROVING THE GATE EXISTS
⛔ **Do not start listing candidates until this is measured**, or the whole shortlist may be
an answer to a question the engine never asks.

**Vanilla RimWorld does not gate weapon equipping on body size at all.** Whatever "big
weapons" means here is a MOD mechanism, and there are at least two different ones in this
stack that must not be conflated:

1. **The giant weapon tags** — `RangedHeavyGiant`, `RangedMedievalGiant`,
   `UltratechMeleeGiant`. Measured 2026-08-22: asked for by **6 pawn kinds, all Big and
   Small giants** (`BS_Jotun_Modernized`, `BS_Jotun_Modernized_Limited`, `BS_Jotun_Javelin`,
   `BS_Jotun_Hunter`, `BS_Jotun_NiflJavelin`, `BS_Ogre_Hunter`). ⚠️ These look like ordinary
   `weaponTags`, which means the "gate" may be **nothing but a tag convention** — a kind
   asks for giant weapons because its author said so, not because the engine checks a size.
   If that is so, a gene grants nothing and the lever is the pawn kind's `weaponTags`.
2. **Warcasket weapons** — `WarcasketAll`/`Veteran`/`Heavy`/`Flamer`/`Melee`. 🔑 **These are
   almost certainly gated by the warcasket APPAREL, not by size**, which would make them a
   different question entirely from the giant tags. `WarcasketAll` is asked for by exactly
   **one** kind, `VFEP_General`.

**Answer, with evidence, before auditing:**
- Is there C# in Big and Small (or VFE-Pirates) that refuses an equip on a size/stature
  stat? Read the assembly, do not infer from the tag names. ⚠️ `strings` cannot answer
  this — see `CLAUDE.md` on what a byte scan of a .NET assembly can and cannot prove.
- Is there a real "big & tall" GeneDef, and what is its defName? Measured 2026-08-22: 49
  genes have size-ish names, but **all the obvious ones are Character Editor's
  `SZBodySize_*` sliders**, which are an authoring tool rather than a shipped species trait.
  A first pass that matched on "BodySize appearing anywhere in the gene" returned **542**
  and was almost all cosmetic `renderNodeProperties` scaling — **do not use that as the
  filter.**

⇒ **If the gate turns out to be tag convention only, say so and stop.** The honest
deliverable is then "there is nothing to grant", not a shortlist that implies otherwise.

## Then the audit, if the gate is real
For each of the 139 xenotypes: name, source mod, current body size if any, and a
**feasibility verdict with a reason** — is this a species where being big and tall reads as
right? ⚠️ Judge on the FICTION, not on mechanics: a Jawa is canonically small and must never
be a candidate whatever the numbers say.
⛔ **Recommend, do not apply.** Granting a species a size gene changes how it looks, what it
eats and what it can carry; every candidate is the owner's call.

## verify
The mechanism answer is stated with the evidence that settles it, and — if a gate exists —
every one of the 139 xenotypes appears in the output exactly once with a verdict.

## criteria
The owner can rule on the shortlist without re-deriving how the gate works.
