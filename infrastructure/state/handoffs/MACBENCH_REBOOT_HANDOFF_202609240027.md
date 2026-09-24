# MACBENCH_REBOOT_HANDOFF_202609240027 — READ FIRST on wake

Follows `MACBENCH_REBOOT_HANDOFF_202609231859`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

🔑 **A sweep that reports a clean result has to prove it can find anything at all.** An artpipe
art-existence check over 18 plant names reported a confident **"0 of 18"** — and had run
**exactly one query, on a nonsense 18-word string**, because the shell here is zsh and
`for x in $NAMES` does not word-split. The real answer was also zero, which is precisely why the
bug nearly survived: the number was right and the instrument was broken, and nothing about the
output looked wrong. It was caught only because a second sweep over 24 Miasma names printed
`subjects checked: 1`.

⇒ **The transferable rule, now in `CLAUDE.md`:** write multi-subject sweeps in python, never a
shell loop over a variable — and **give every sweep a sanity probe** that searches for something
known to be present and prints its hit count beside the result. Re-run with probes
(`korrum` 17, `stoneback` 52, `hawkbat` 91) the zero became trustworthy, and the same corrected
sweep then caught a real defect the first one had no chance of seeing: `RM_Mirrash` collided with
`mirrash veil`, a **shipped in-game label** in the Rot Spore Kit. A defName check would have
missed it, because the clash was on a label.

🔑 **And the cheaper half of the same lesson: before filing a defect, check whether the pattern
is the convention.** A note called bare unprefixed roster defNames a defect on the evidence of
one row. Measuring first would have shown **144 such rows across 18 of 29 rosters** faithfully
mirroring what the live biome XML does deliberately. The note had to be retracted — but the
measurement that retracted it found the real gap one level up, which is worth far more than the
"defect" was.

## What the owner should see

1. 🔴 **98 live biome rows across 11 biome files still name the bare donor for 73 creatures we
   already ported**, so the campaign still hard-depends on `mlie.starwarsanimalcollection` and 73
   creatures we paid to port — art extracted, defs written, sounds absorbed — spawn nowhere.
   `MLIE_FAUNA_ABSORPTION_1` closed having found this exact gap for `RSW_Bantha`, fixed that one,
   and recorded only **7** wired. Filed as `MLIE_ABSORPTION_BIOME_WIRING_1`. ⛔ Deliberately NOT
   worked as a sweep — he stopped sweeping roster changes on 2026-09-22, so it is per-biome work.
2. ⚠️ **I gave the Miasma's attar a plant rather than the terrain its sheet implies** — immarel's
   root-bed concentrates the silt — on the precedent of his Fever Wood seep-oils ruling, where
   the terrain route was offered and declined. It is a sheet phrasing overridden by my judgement
   and it deserves his eye. One row changes if he wants terrain.
3. ⚠️ **The Fever Wood's four sap-drinkers share one posture on purpose** and are told apart by
   *state* — a thorn, a resin bead, a vent, a swelling sac. If he wanted four visibly different
   animals rather than four readings of one animal, that is a different art brief and it is
   cheaper to say so before anything is drawn.
4. ⚠️ **`RM_Brathek`'s digging rate is unset and is the most consequential missing number**
   authored this session. A creature that opens your walls is characterful only if you can always
   see it coming; "slow and visible" is written in as a requirement but nobody has proposed a rate.
5. ⚠️ **`RM_Ismerrow` is only worth building if it can be colour-randomised.** It exists solely to
   be never-alike (his coleus reference); as a single sprite the row has no reason to exist and
   should be cut rather than shipped.
6. ⚠️ **`RSW_Porg` probably fails his own "not parrots" brief** — it is on the homeless-flier list
   for the Fever Wood's birds and is canonically bird-cute. Flagged, not used.
7. ⚠️ **A dangling item reference:** four purged Miasma flora rows cite
   `POLLUTED_LANDS_FLORA_PORT_1`, which exists in neither `items/` nor `items/closed/`. So the
   reason the biome's only rainbow plant left is not recorded anywhere retrievable.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `SEA_BEASTS_TIER_RULING_1` — **RULED this session and fully specified, nothing built.** The 11 invented sea beasts move to `RM_`, the 7 canon stay; reassigned to FOUNDRY, `needs` moved owner→offline; NEXT: on the **Desktop**, rename the 11 ThingDef/PawnKindDef pairs **and their juveniles** and repoint every leather, meat, egg, sound, `wildBiomes` and biome-cast reference — ⛔ a retier MOVES creatures and removes none, and the final-concept mockups are not re-rolled.
- `MIASMA_FLORA_ROSTER_1` — 19 plants authored, art search discharged, **zero defs, zero art**; NEXT: author the four mangal `ThingDef`s first (§3), because they replace the donor canopy and are what `mandrake.rm.miasma` needs in order to stand alone at all.
- `MIASMA_FAUNA_FLOOR_ROSTER_1` — 5 creatures + the stranded mechanism specified, nothing built; NEXT: **read `RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation` before writing any C#** — a scuttler population drawn down by five plants, a harvest and every predator is exactly what a vermin-population component already is.
- `FEVERWOOD_SAP_SUCKER_GUILD_1` — the cast is now named (`fever_wood_fauna_roster_2026-09-23.md`), still no defs; NEXT: build the nectar contract on `RM_CompGatherableCalmGated`, which already compiles — ⛔ do **not** reach for `CompProperties_HasGatherableBodyResource`, which has zero precedent in this repo.
- `FEVERWOOD_ALIEN_BIRD_CHORUS_1` — four birds named with one ruled role each, nothing built; NEXT: give `RM_MapComponent_SilenceCue` a public "hush now" entry point, the exact gap the sitting recorded, and resolve whether `EnvironmentalHazards` may reference `CreatureBehaviors` at all.
- **The Miasma's §7 economy defs are NOT authored** — the attar refinement chain, delta loam, the arthropod harvest and the flotsam tables. The flora roster gives all four a source plant, but no item owns the goods themselves; NEXT: **file one item for the four §7 trade goods**, citing `miasma_flora_roster_2026-09-23.md` §6 for which plant feeds which.
- **The three engine questions this sitting raised are UNMEASURABLE on the Mac** and ⛔ must not be reasoned out from a doc; NEXT: on the **Desktop**, measure (a) whether a plant's reproduction can be gated on a nearby animal — the fever-swarm's whole bargain, (b) how much a hediff can alter an animal's rendered appearance — the stranded's look, (c) whether a plant can consume a small wild animal and be restricted to one species — all five Miasma predators.
- ⚠️ `MIASMA_MECHANICS_1` — M1–M6 all built 2026-09-13/14; its only open boxes are **in-game verification**; NEXT: on a Desktop cold load, run a quicktest on a **scratch** world tiled to the Miasma and confirm forced miasma weather with no rain, then tick the two boxes or record what failed.
- ⚠️ `KORRUM_ART_REGEN_1` / `STONEBACK_BOKKA_ART_STANDARD_1` / `ROSTER_DEAD_BMT_NAMES_SWEEP_1` — I **stopped carrying these** and that is deliberate, not neglect: all three are Desktop-gated (artpipe daemon, or live-modlist resolution) and their own item text says carrying them forward as pending decisions is wrong behaviour; NEXT: **leave them alone until a Desktop session** — ⛔ do not re-inherit them into a Mac handoff a sixth time.

## Traps learned

1. 🔴 zsh does **not** word-split `for x in $NAMES` — it loops ONCE on the whole string, and a sweep reported a confident "0 of 18" having checked nothing. Use python, and give every sweep a sanity probe (see: `CLAUDE.md > Instruments that return a confident wrong number`).
2. ⚠️ Same family: `R="python3 …/cli.py"; $R file …` fails with `no such file or directory: python3 …` because zsh passes the whole string as one word (see: same section).
3. ⚠️ A bare unprefixed defName in a design roster is the **convention**, not a defect — 144 rows, 18 rosters, mirroring the live XML deliberately (see: same section).
4. 🔴 A rebase conflict in `events.jsonl` is resolved by git **plumbing** (`hash-object` → `update-index --cacheinfo` → `checkout-index`), never `checkout --ours/--theirs`, which discards a concurrent seat's events (see: `CLAUDE.md > Git`).
5. ⚠️ `rimflow render -- --overwrite-queues` — the flag belongs to `render.py`, must come after `--`, and `reindex` rejects it (see: same Git section).
6. ⚠️ `--seat MACBENCH` is **refused** by rimflow; the valid seats are BENCH/FOUNDRY/OWNER/DECIDE/BUILD/CHECK/REP, so this window signs as `BENCH` and names itself in the event text (filed: LESSONS).
7. ⚠️ The health publisher re-dirties 5 tracked artifacts on every rimflow/`code_review_status` call, so a `git pull --rebase` refuses mid-session until they are committed — already recorded, hit three times this session (see: `CLAUDE.md > Git`).

## Commits

```
94a16b6e4 Three traps into CLAUDE.md, one of which reported a clean bill of health
075729232 The sea beasts are retiered: invented goes free, canon stays campaign
16b5bd1c9 chore: health publisher artifacts regenerated
144e7019f The Fever Wood fauna roster the last four handoffs kept owing
683211335 CUT_FALLOUT_GENERATED_DATA_1: regenerate animal tolerances against clean cast_assignment.csv
80e5f17f5 Art search discharged for 42 subjects, and it caught a shipped label collision
b4000c394 chore: health publisher artifacts regenerated by the rimflow pass
9dad24edc Four Miasma items filed, and a bare-name "defect" that was never one
9b40980da Merge remote-tracking branch 'origin/main'
ab0dc44b8 health publisher: auto-regenerated artifacts (unblocks merge)
6792aa6ba rimflow: Q12–Q15 ruling notes on 10 biome build tickets (ledger sync)
2b2d6b660 biome_mod_architecture §7 Q12–Q15: owner rulings 2026-09-23 on the split's four recurring questions
d9394a353 The stranded are a condition, not a cast - and 11 sea beasts are misfiled as IP
e2d806a34 chore: health publisher artifacts regenerated
928e034d2 The Miasma's signature flora did not exist; 19 invented plants now do
6b37e752f rimflow: BIOME_MOD_SPLIT_EXECUTION_1 wave note + seat (ledger sync)
eb64153e3 LANTERNDEEPS, MIASMA, TERMINALBIOMES build tickets: render STATE sections; nine stale claims corrected
621bfc9a7 RUSTCATHEDRAL_RM_MOD_BUILD_1: render STATE section; readiness table mis-graded a ruled plantless biome
07c4226dc Ledger sync: CUT_FALLOUT_GENERATED_DATA_1 (a) note
113b53956 CUT_FALLOUT_GENERATED_DATA_1 (a): regenerate cast_assignment.csv, 0 BMT_ defNames left
... 40 more: git log --oneline 1e7fee2d5..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Working tree clean.

