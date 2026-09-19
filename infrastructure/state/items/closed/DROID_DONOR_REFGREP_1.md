## sweep on record (BENCH, 2026-09-06 — haiku, treat as evidence not verdict)
`design/Jawa/droids/D1_donor_reference_grep.md`: per donor, every gameplay reference is
MayRequire/FindMod-gated; the "hard" hits are comments and About.xml dependency listings
(FactionSlate/About.xml lists kotordroids as a modDependency — a mod-list warning, not a
load error). ⚠️ The 15 Depot-gated faction/roster references will SILENTLY stop spawning
when Depot leaves (the bare-hands trap) — C2 (`DROID_FDE_KINDS_REPOINT_1`) must land
first. Whoever claims this packet: spot-check two hard hits per donor before closing.

## FOUNDRY spot-check, 2026-09-07 — verified 3/4 donors clean, corrected one

Spot-checked 2 hard-reference citations per donor against the actual files (not
re-trusting the sweep's own excerpts).

**guy762.kotordroids** — CONFIRMED accurate. `DroidDonor_ABFGate.xml` lines
41/58/97 are comment prose (verified: each line is inside a `<!-- -->` block, no
live XML/C#). `FactionSlate/About.xml:16` is a genuine bare `<li>guy762.kotordroids</li>`
dependency listing, exactly as reported.

**neronix17.asimov** — CONFIRMED accurate. `BoltCorePatches.cs:38-45` is a C#
`///` doc comment (informational, matches report). `Doctrine/About.xml:90`
(`<li>Neronix17.Asimov</li>`) and `ResearchRetag/About.xml:52`
(`<li>neronix17.asimov</li>`) are both genuine `<loadAfter>`/dependency listings,
exact packageId match, no discrepancy.

**neronix17.outerrim.droiddepot** — CONFIRMED accurate. `DroidFemaleTexture_Fix.xml`'s
comment block (lines 16-18, 41-43, 127-128) matches the reported texture-bug
documentation. `JawaFreeDroidEnclaves.xml` genuinely carries multiple
`MayRequire="Neronix17.OuterRim.DroidDepot"`-gated pawnkind entries (both our own
`Jawa_Droid_*` names and Depot's own `OuterRim_ProtocolDroid`/`OuterRim_KXSecurityDroid`)
— matches the "properly gated" verdict.

**killathon.artificialbeings (ABF) — CORRECTED.** The sweep's report cited
`Doctrine/About.xml`'s `<loadAfter>` and `ResearchRetag/About.xml`'s dependency
listing as hard references to `killathon.artificialbeings` (the base framework).
Read directly: **both actually reference `killathon.artificialbeings.syncore`** —
a different, related packageId (the "ABF: Synstructs Core" sub-mod), not the
framework itself. `Doctrine/About.xml` carries its own dated comment
(`DOCTRINE_LOADAFTER_STALE_1`, 2026-09-06) explaining this exact distinction: the
bare `killathon.artificialbeings` packageId belongs to the framework, while
`.syncore` is what `DroidsAreMachines.xml` actually gates on
(`ABF_FleshType_Synstruct_Base`) — and that fix already corrected these two
entries FROM the bare packageId TO `.syncore`, apparently before or without the
haiku sweep picking up the distinction (both are dated the same day).

Grepped for the true bare packageId across all of `src/` (`grep -rn
"killathon\.artificialbeings\b"` excluding `.syncore` hits): **exactly one hit,
and it is itself the DOCTRINE_LOADAFTER_STALE_1 comment's own prose** — zero live
functional references to the base ABF framework remain anywhere. This makes the
framework's retirement readiness STRONGER than the sweep reported, not weaker —
but the sweep's own citations for this donor should not be trusted for a future
cleanup pass (a future session "removing stale killathon.artificialbeings
references" from those two `About.xml` files would be deleting the CURRENTLY
NEEDED `.syncore` loadAfter, not stale ABF-framework debris).

## Retirement readiness, corrected

| Donor | Status | Note |
|---|---|---|
| guy762.kotordroids | READY | sweep accurate |
| killathon.artificialbeings (bare framework) | READY, cleaner than reported | zero live refs; `.syncore` is a SEPARATE mod, not part of this retirement |
| neronix17.asimov | READY | sweep accurate |
| neronix17.outerrim.droiddepot | READY | sweep accurate; C2 (`DROID_FDE_KINDS_REPOINT_1`) must land first per the sweep's own bare-hands warning |

## verify
```
PROVE   grep -rn "killathon\.artificialbeings\b" src/ excluding .syncore hits -> exactly
        the DOCTRINE_LOADAFTER_STALE_1 comment, no live reference
EXPECT  the other 3 donors' cited hard/gated references match the sweep's own excerpts
        verbatim when read directly
LIES    trusting a loose "contains ArtificialBeings" grep to mean "references THIS
        donor" when a same-named sub-mod (.syncore) is a distinct, currently-needed
        dependency
```
