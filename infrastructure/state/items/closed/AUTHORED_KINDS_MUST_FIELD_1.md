# ✅ THE XML IS SHIPPED. This item is AWAITING BRIDGE VERIFICATION, not ready work.

**Correction written 2026-08-27 by BUILD, from `STALE_ITEM_HEADER_CORRECTIONS_1`. Read
these three before touching anything — the spec below them is the pre-implementation
brief and is stale in exactly these three places.**

### 1. IMPLEMENTED — do not re-implement
All three wirings shipped and are deployed. Both patch files carry this item's ID in their
own section headers; `grep -l AUTHORED_KINDS_MUST_FIELD_1 src/Jawa/Jawa_Patches/Patches/*.xml`
finds them.

| kind | route | file |
|---|---|---|
| `Jawa_DeepDesert_*` | whole `pawnGroupMakers` list declared on the child | `src/Jawa/Jawa_Patches/Patches/DeepDesertTribes.xml` |
| `Jawa_Blackstar_*` | six `Replace`s into `Pirate`'s own combat groups | `src/Jawa/Jawa_Patches/Patches/BlackstarCompany.xml` |
| `Jawa_Empire_Leader` | `fixedLeaderKinds`, not a group — a leader is generated once per faction, never rolled into a raid | `src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml` line 147 |

**What is left is the live half only:** spawn raids from `TribeCivil`, `Pirate` and
`Empire` and read the pawn NAMES.

### 2. 🔴 The ⛔ against `Inherit="False"` below was OVERRULED, on evidence
It is kept in place because the record is immutable, but **it is not the instruction.**
`TribeCivil` inherits all twelve groups from the abstract `TribeBase`; PatchOperations run
**before** inheritance resolves, so a `Replace` on the child matches **zero nodes and logs
nothing** (verified with lxml against shipped Core XML, 2026-08-22:
`/Defs/FactionDef[defName="TribeCivil"]/pawnGroupMakers` → 0 nodes). Patching `TribeBase`
by `@Name` would hit TribeRough, TribeSavage and every modded descendant across 578 mods.

⇒ The route taken declares the whole list on the child **and re-declares the eight
non-combat groups byte-for-byte out of Core's `Factions_Misc.xml`**, copied
programmatically, not retyped. That answers the objection the ⛔ was actually making —
that Trader, Peaceful and Settlement would be dropped. They are not dropped; they are
present and vanilla. 🔑 **Read the comment at `DeepDesertTribes.xml` line 132 before
forming a view.** `Pirate` writes its own six groups, which is why Blackstar could take
the `Replace` route and Deep Desert could not.

### 3. The combat weights are TUNED PER GROUP — they are NOT `GalacticEmpire.xml`'s numbers
The spec below says to copy the pattern Empire ships. **The pattern, not the numbers.**
Each group's option weights are tuned to that group's tactical character.

🔴 **Measured, not hypothetical.** A cheap-model BUILD trial (`KIMI_GATEWAY_FOR_BUILD_1`,
2026-08-26) was handed this item cold in a throwaway worktree. It did not notice the work
was done, copied Empire's *numbers*, and flattened Deep Desert's `10 / 5 / 6` and
Blackstar's `10 / 5 / 3` to Empire's `5 / 2 / 1.5` — then reported it as completed work.
**A 14-check structural grader passed that regression 14 of 14.** XML parsed, no
`Inherit="False"` regression, no vanilla kinds in a combat group, non-combat groups
untouched, both rosters still fielded. Only `git diff` found the loss.
Grader: `src/RimMandrake/Utils/grade_authored_kinds_trial.py` ·
diff: `research/nemotron_build_trial_2026-08-26.diff`.

---

## spec
🔴 **DECIDE ruled 2026-08-22: wire the nine orphaned role kinds into their factions.**
Full ruling — `design/Jawa/worldbuilding/pawnkind_roster.md`, *"Every authored kind must be
FIELDED"*. "Leave them as a reserve" was rejected outright.

    Jawa_DeepDesert_Grunt  Heavy  Leader  Specialist   -> TribeCivil
    Jawa_Blackstar_Grunt   Heavy  Leader  Specialist   -> Pirate
    Jawa_Empire_Leader                                 -> Empire  (plain omission)

## 🔑 the shape DECIDE ruled — replace the CAST, keep the GROUPS
✅ **Rewrite the `options` inside the COMBAT groups only.** This is the pattern
`GalacticEmpire.xml` already ships and proves — it is why three of four Empire kinds field
today while Deep Desert and Blackstar field none.

⛔ **Do NOT use `Inherit="False"` on `pawnGroupMakers`.** It drops all twelve inherited
groups including **Trader, Peaceful and Settlement**, and the 48-kind roster has **no
trader role** to replace them with. A faction that cannot send a caravan or defend its
settlement is a worse defect than the one being fixed.

⛔ **Do not let a raid mix ours with vanilla.** `pawnGroupMakers` inherits by APPENDING, so
a bare new `<li>` yields half-Tusken, half-generic-tribal raids. No vanilla `Tribal_*` may
appear in a Deep Desert combat group; no vanilla pirate kind in a Blackstar one.

⛔ **Non-combat groups stay vanilla.** Deliberate, not an oversight.

## why it matters — measured
18 live spawns from `TribeCivil` today draw `NerveSpiker`, `BMT_ThrumbungusShroom`,
`VWE_Throwing_Knives` and **bare 6 of 18**. The authored kinds draw gaderffii sticks and
Tusken cyclers — the faction the owner described on 2026-08-22.
Evidence: `observed/2026-08-21/armed_sweep_48/`.

## why it slipped through
`DeepDesertTribes.xml` contains the string `Jawa_DeepDesert` **zero times**; its one
sanctioned group addition is documented as vanilla-Core-only. `BlackstarCompany.xml` states
outright that `pawnGroupMakers` are untouched. Both patches did what they say — nobody ever
wrote the wiring step.

## verify
Spawn a raid from each of `TribeCivil`, `Pirate` and `Empire` and read the kinds back:
every combat pawn must be a `Jawa_*` kind. Then confirm each faction can still send a
trade caravan and still populates its settlement.

## criteria
Zero vanilla kinds in a combat group of the three factions; `Jawa_Empire_Leader` fielded;
Trader/Peaceful/Settlement groups still functional.

## watch out
⚠️ Not the same problem as the weapon cut. `FLAMEBOW_UNCUT_AND_RETAGGED_1` is separate —
doing this first may make the flamebow question moot for Deep Desert, but neither fix
substitutes for the other.
⚠️ Whether Blackstar generates at all is `BLACKSTAR_IN_DEFAULT_LIST_1` (CHECK, doing).
That one IS baked at worldgen; this one is not.

---

## ✅ THE WIRING IS LIVE-LOADED — measured 2026-08-27, BUILD

Read from `FactionDef.pawnGroupMakers` in capture `2026-08-26T14-20-04Z`, which is taken from
the running game **after** every PatchOperation, so this is the resolved truth rather than our
XML re-read back to us:

    Empire      combat options 6   ours: Jawa_Empire_Grunt · Jawa_Empire_Heavy · Jawa_Empire_Specialist
                                   fixedLeaderKinds: [Jawa_Empire_Leader]
    Pirate      combat options 3   ours: Jawa_Blackstar_Grunt · Jawa_Blackstar_Heavy · Jawa_Blackstar_Specialist
                                   fixedLeaderKinds: [Jawa_Blackstar_Leader]
    TribeCivil  combat options 3   ours: Jawa_DeepDesert_Grunt · Jawa_DeepDesert_Heavy · Jawa_DeepDesert_Specialist
                                   fixedLeaderKinds: [Jawa_DeepDesert_Leader]

⭐ **All three routes resolved, including the two that could have failed silently** — the
`TribeCivil` whole-list declaration (a `Replace` there would have matched zero nodes) and the
six `Replace`s into `Pirate`'s own groups. The leader-by-`fixedLeaderKinds` route resolved too.

⚠️ **`Pirate` and `TribeCivil` now field ONLY our kinds in combat (3 of 3).** `Empire` fields 3
of 6 — the other three are Royalty's own. Whether vanilla Empire kinds should still appear
beside ours is a scope question this item never asked; it is **not** flagged as a defect here.

## What is still owed, and why today's attempt did not deliver it
The live half — raids from these three factions read by pawn NAME — is **not** closed. The
attempt failed on experimental design, not on the game: `jawa/fire_raid`'s `faction` parameter
does not steer the raid, so with several factions hostile at once the worker picks among them.
A raid requested from `Jawa_FreeDroidEnclaves` arrived as **22 `Jawa_Hutt_*` pawns**.

🔑 **The correct design, for whoever runs it:** set **exactly one** faction hostile and every
other authored faction back to Neutral before each firing, then read the spawned pawns' own
faction — never `resolved.faction`, which echoes the request. And retry: `fire_raid` is
intermittent (`AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1`), so one empty result is not a negative.

### What `Empire`'s "3 of 6" actually is — not vanilla, and probably wanted
Its three combat groups are: two fielding **only** `Jawa_Empire_Grunt/Heavy/Specialist`
(weights 5 / 2 / 1.5), and a third fielding `OuterRim_ImpRangeTrooper`,
`OuterRim_ImpDeathTrooper`, `OuterRim_ImpISBAgent` (2 / 1.5 / 1).

✅ **Those three are Outer Rim imperial kinds, not Royalty's.** No vanilla Royalty kind appears
in any Empire combat group, so the "no vanilla kinds in a combat group" bar is met. Range
troopers and death troopers beside our stormtroopers reads as the Empire, not as a leak.
⚠️ Recorded because a future audit counting "kinds that are not ours" will flag it as 3 foreign
entries and it is not a defect. If the campaign ever wants the Empire to field *only* authored
kinds, that is a scope call and nobody has made it.
