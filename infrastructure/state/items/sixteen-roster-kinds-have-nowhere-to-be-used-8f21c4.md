## spec
The 48-kind roster covers all TWELVE factions, but only the eight authored
`Jawa_*` FactionDefs were wired to it. The other four — Galactic Empire,
Homestead Defense League, Deep Desert Tribes, Blackstar Company — are RESKINS,
and B41, B42 and B43 each say in terms: *"⛔ Do NOT touch `pawnGroupMakers` —
they are inherited and already balanced."* B40 is the sanctioned exception and
already replaced the Empire's combat groups with `OuterRim_Imp*` kinds.
⇒ 16 kinds (`Jawa_Empire_*`, `Jawa_Homestead_*`, `Jawa_DeepDesert_*`,
`Jawa_Blackstar_*`) are authored, valid and referenced by nothing.
THE CHOICES:
(a) **Leave them unwired.** The four reskins keep vanilla's balanced groups; the
    16 kinds are dead weight but harmless, and available if wanted later.
(b) **Wire them, reversing the don't-touch rule for these four.** They would then
    field roles like the other eight — and the Deep Desert Tribes in particular
    would stop drawing on `Tribal_Warrior`/`Tribal_Hunter`, two kinds this
    project has separately proven spawn bare-handed.
(c) Wire only Deep Desert, where the bare-handed problem actually bites.
🔑 (c) is the cheapest correct answer if the concern is player-visible harm, and
BUILD's recommendation — but it is a scope reversal either way, which is why it
is here and not in the build.

## verify
n/a — a ruling.

## criteria
n/a

## notes
**from:** BUILD, 2026-08-20, closing B53.

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

✅ RULED 2026-08-20 — **NOT WORLDGEN-CRITICAL. It comes OFF the critical path.**
Verified: all four prefixes (`Jawa_Empire_*`, `Jawa_Homestead_*`,
`Jawa_DeepDesert_*`, `Jawa_Blackstar_*`) appear in exactly one file each — their
own def file — with **zero `pawnGroupMakers` references.** BUILD's finding is exact.
🔑 **THE RULING, and the reason is a timing fact rather than a taste call:**
`pawnGroupMakers` are consulted when a RAID or group is generated — live, during
play — **not at world creation.** Faction *existence* bakes at worldgen;
faction *rosters* do not. ⇒ **This can be fixed at any time, including after the
world is frozen and shipped.** It is the only faction-adjacent item on the board
that is not on the worldgen clock, and it should stop competing with B40–B54.
⇒ **Deferred past the gate, not dropped.** ⛔ Do not wire the reskins'
`pawnGroupMakers` now — B41/B42/B43 forbid it for a real reason (they are
inherited and balanced), B40 is the one sanctioned exception and is already done,
and buying that risk in the week before an irreversible worldgen run is a bad
trade. 16 unreferenced `PawnKindDef`s are inert and cost nothing.
⚠️ **The live consequence, stated so nobody is surprised in play:** until it is
wired, the Homestead, Deep Desert and Blackstar reskins field VANILLA kinds in
raids, not our authored ones. That is a content gap, not a defect, and it is
reversible on any day after the world exists.
