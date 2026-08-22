## spec
🔴 **OWNER, 2026-08-21 21:53 and confirmed 22:39.** *"We should simply add a line that Jawa
genetics has a disability toward farming."* Then, on the fork between a penalty and a hard
incapability: *"Correct on the aptitude decision."*

⇒ **An APTITUDE, not `disabledWorkTags`.** Jawa are *bad at farming*; they are not barred
from it. That distinction is load-bearing: `disabledWorkTags` has no `Growing`-only WorkTag,
only `PlantWork`, which also stops a Jawa harvesting, cutting wild plants and **chopping
trees**. No wood, on a scavenger clan.

**The gene already ships.** Biotech's `AptitudeTerrible_Plants` —
`aptitudes: [{skill: Plants, level: -8}]`. Measured against `OFFICIAL-2026-08-21T22-44-59Z`:
Biotech carries a full `AptitudeTerrible_*` set across all twelve skills, and 24 GeneDefs in
the active stack use a negative aptitude. **Nothing to author.**

**Do:** add one `<li>AptitudeTerrible_Plants</li>` to
`src/Jawa/RimMandrake_StarWarsRaces/Defs/XenotypeDefs/MandrakeJawaXenotype.xml`, in the
`<!-- aptitudes: they build, they make, they haggle -->` block beside
`AptitudeStrong_Construction`, `AptitudeStrong_Crafting` and `AptitudeStrong_Social`.
Gene count 35 → 36.

🔴 **AND THE HEADER MUST BE CORRECTED IN THE SAME COMMIT, OR THIS GENE DIES.** That file
says *"GENES: all 35, in the .xtp's own order, transcribed verbatim"* and *"The two must be
kept in step by hand; if the owner edits the .xtp in game, re-transcribe."* After this edit
that is false: the def deliberately carries one gene the `.xtp` does not, and a re-transcribe
would silently drop it. ⛔ Do **not** edit `MandrakeJawa.xtp` to match — it is the owner's
saved editor artifact and a record of what he built by hand. Measured 2026-08-21: the repo
copy and the live `LocalLow\Xenotypes\MandrakeJawa.xtp` are byte-identical, and they should
stay that way.

## verify
- `validate_patch.py --defs` clean on the xenotype file
- `MandrakeJawa` lists `AptitudeTerrible_Plants` exactly once, gene count 36
- `AptitudeTerrible_Plants` resolves to a `GeneDef` in the frozen capture
- ⛔ `MandrakeJawa.xtp` is **unchanged** in both copies, and they remain byte-identical
- the file header no longer claims the def and the `.xtp` are in step, and names the
  divergence

## criteria
CHECK, next load: a generated Jawa's Plants skill carries the *terrible at* aptitude and the
skill is **not** greyed out as incapable — they can still harvest and chop wood.
