## spec
🔴 **The `VME_Nomad` reversal is done in code and NOT propagated into the design docs that
still argue against it.** `NOMAD_MEME_RESTORED_TRIBES_1` closed at `96f2012`; these files
are DECIDE's and BUILD may not edit them.

⚠️ **POLICY.md:436 already cites `VME_Nomad` as THE worked example of a reversal left
unpropagated.** This audit found one of the very files it names still stale. The lesson was
written down and the propagation still did not happen — which is the argument for doing it
now rather than filing it again later.

🔑 **The two-file truth, which every fix below must preserve:** the meme is **live on the
NPC tribes** (`JawaTribes.xml:129`) and **absent from the player `.rid`** (`The
Salvation.rid`, 4 memes). That is not drift — the player side is a separate open decision
under `DEPLOY_SALVATION_RID_1`, because `VME_PermanentBases_Despised` carries
`enabledForNPCFactions false` and so is free on an NPC faction and NOT free on a player one.
⛔ Do not "fix" the divergence by changing the `.rid`.

**1. `design/Jawa/worldbuilding/setup_checklist.md:103-104` — STALE, a reader re-does closed
work.** It says `JawaTribes.xml:109` *"is still the 08-20 removal comment and is therefore
WRONG; restoring the `<li>` is NOMAD_MEME_RESTORED_TRIBES_1, filed for BUILD and not yet
run."* It has run. The `<li>` is at line **129**, the removal comment was replaced with the
reversal rationale, and line 109 is now `VME_Trader`. The rest of that box is correct.

**2. `design/Jawa/worldbuilding/ideoligion/APPROVED.md` — PARTIAL.** Lines 128-130 claim the
meme is on the tribes *"and on the player ideo"*; the second half is untrue. Lines 142 and
147-148 sit under a struck header but are still literally true of the `.rid` — say so
explicitly, and record that the tribes def now validates **1/1 VALID, impact 10 over 5
memes** where that block says 7 over 4.

**3. `design/Jawa/worldbuilding/faction_religions_spec.md` — PARTIAL, two separate problems.**
- Line 632 — *"`VME_Nomad` was dropped for `PainIsVirtue`, owner's ruling 2026-08-14"* — is
  **correct but unanchored**. It is about the Deep Desert Tribes / *the Sun-Debt* (§4), and
  it is the top grep hit for the meme in the whole repo. Add the faction to the sentence.
- Lines 1125 and 1138 (§12, the Jawa faith) call **"Nomad-primary vs Tunneler-primary"** an
  open blocker and *"still a coin"*. It is settled: the shipped set is
  `AM_Structure_Scavenger · Trader · VME_Scrapper · VME_Trader · VME_Nomad`, and there is no
  Tunneler meme anywhere on disk.

✅ Checked and FINE, listed so nobody re-audits them: `design/V2_DREAMS.md`,
`design/Jawa/worldbuilding/data/ideology_palette.md`,
`design/Jawa/worldbuilding/review/religions_repair_sheet.md`, `infrastructure/agents/POLICY.md`.

## verify
`grep -rn VME_Nomad design/` returns no sentence asserting the meme is dropped from the Jawa
tribes, and no line calling the Nomad/Tunneler choice open. Every remaining mention either
names the Deep Desert Tribes or names the player `.rid` as a separate open decision.

## criteria
A reader arriving at any of these files cold cannot conclude that restoring `VME_Nomad` to
the tribes is still owed, nor that the tribes and the `.rid` have drifted by accident.
