## spec
Carries the live half of **B45 · B46 · B47 · B48 · B49 · B50 · B51** — Hutt
Cartel, Free Droid Enclaves, Wildsteam Clan, Deepwater Compact, Geonosian
Foundry Hive, Ascendant Helix, Junkers. All seven `FactionDef`s are in
`src/Jawa/Jawa_Patches/Defs/FactionDefs/` and deployed.

## verify
done offline against the 578-mod list: **8 files, 0 errors, 1 warning** — the
warning is `iconPath UI/Deities/DeityGeneric`, which is the exact path vanilla
Anomaly's `HoraxCult` uses; the texture lives in a Unity bundle, so no loose-file
checker can see it. Every one of the 45 pawn kinds named across the eight defs
resolves in the live def dump. All four naming/art fields present and non-null on
every faction. `humanlikeFaction` was MISSING on four (Helix · Deepwater ·
Junkers · Wildsteam) and was added — R3 requires it explicitly. No
`combatPower 99999` kind in any `options`, no `minTotalPoints`, no invented
`basicMemberKind`, no `<li>`-shaped `xenotypeChances`.

## criteria
each of the seven appears on the Configure Factions page, generates settlements
at worldgen, and its raids arrive as ITS OWN pawn kinds — not vanilla ones.
🔴 The vanilla-pawn failure is the one to watch: it is what `Inherit="False"` on
`pawnGroupMakers` and on `xenotypeSet` exists to prevent, and it looks like a
working faction until you read the pawn names.
⚠️ Five design values are unresolved and filed to DECIDE as
`five-design-gaps-found-auditing-the-seven-authored-factions-3c81ea`: no
`maxCountAtGameStart` on seven of eight, the Geonosian two-outposts ruling has no
mechanism, the Hutt's `ideoDescription` disagrees with the religions spec, the
Free Droid Enclaves field a biological species against a 0%-biological dossier,
and baseliners generate in five factions. None of them stops this check.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready

---

## ⏳ LIVE HALF RUN 2026-08-27, BUILD — two criteria of three MET, the third BLOCKED

582 mods, paused scratch map, bridge intact (291 tools / 166 `jawa/`).
Evidence: `infrastructure/state/evidence/bridge_session_2026-08-27_BUILD.md`.

✅ **All seven appear and generate settlements.** `jawa/list_factions`:
Hutt 4 · Junkers 4 · FreeDroid 2 · Deepwater 2 · Helix 2 · Wildsteam 1 · Geonosian 1.

✅ **Not one vanilla kind in any combat group.** Every `Combat` pawnGroupMaker across all
eight authored factions fields only our own kinds, and every kind named resolves — read from
`FactionDef.pawnGroupMakers` in the capture, which is post-inheritance and post-PatchOperation,
so it is the resolved truth rather than our XML. **The failure this item told me to watch for
is absent.** The only foreign entries are `carriers` (pack animals) and the Free Droid
Enclaves' protocol-droid trader and KX guard.

✅ **The kinds spawn correctly.** All four Hutt kinds, in-faction: **7 of 8 armed and clothed**,
species mix Klatoonian · Nikto · Aqualish · Gamorrean · Falleen · Hutt. The one bare pawn is a
vanilla `Colonist` the tool substituted — see `SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1`.

🔴 **BLOCKED: "its raids arrive as ITS OWN pawn kinds" is UNPROVEN and may be a real defect.**
An aimed raid on a genuinely hostile `Jawa_HuttCartel` — `canStageAttacks: true`, strategy and
arrival pinned, 2000 points, ~4,900 ticks stepped — delivered **zero pawns**, twice, while the
same map raided fine for other factions. Filed as `AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1`.
⇒ **Do not read this item as passed.** Group makers being correct is necessary and not
sufficient; nothing has yet observed one of these factions actually raid.

⚠️ **Two traps caught here that void earlier evidence of this kind.** `jawa/fire_raid` echoes
the faction you requested while substituting another — an aimed Hutt raid delivered 19
`AG_XenohumanPirates` — so any past reading of `resolved.faction` proves nothing. And a census
taken immediately after firing reads 0 for a raid merely in flight. Both are now in
`skills/rimbridge/references/traps.md`.

---

## 🔴 THE RAID CRITERION, MEASURED PROPERLY — 1 of 7, and the other six raid nothing

Corrected experiment 2026-08-27: **exactly one authored faction hostile at a time**, every other
returned to Neutral before each firing, 3000 points, up to 3 firings each (`fire_raid` is
intermittent). Reading the spawned pawns' own faction, never `resolved.faction`.

| faction | result |
|---|---|
| `Jawa_HuttCartel` | ✅ **27 pawns, own faction**, kinds Grunt 16 · Specialist 7 · Heavy 3 |
| `Jawa_FreeDroidEnclaves` | ⛔ no arrivals in 3 firings |
| `Jawa_WildsteamClan` | ⛔ no arrivals in 3 firings |
| `Jawa_DeepwaterCompact` | ⛔ 3 **Thrumbo**, faction `None` — wildlife, not a raid |
| `Jawa_GeonosianFoundryHive` | ⛔ no arrivals in 3 firings |
| `Jawa_AscendantHelix` | ⛔ no arrivals in 3 firings |
| `Jawa_Junkers` | ⛔ no arrivals in 3 firings |

⇒ **Only the Hutt Cartel has been observed raiding.** Across the session it did so five times
(16 · 55 · 40 · 21 · 27 pawns) always as itself and essentially always its own kinds. The other
six produced nothing in 18 firings between them, each as the sole hostile faction.

⚠️ **`fire_raid` is intermittent** (`AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1`), and the Hutt
itself needed retries earlier, so 3 firings is a weak negative per faction. **18 firings with
zero arrivals is not weak.** The asymmetry is the finding, not the individual zeros.

🔑 **One lead worth checking first:** the Hutt has **4 settlements**, as do the Junkers; the
other five have 1–2. Whether a raid source needs a settlement within range is one query against
the world, and nobody has run it.

⚠️ **One anomaly, unexplained:** the 27-pawn Hutt raid contained a single `Jawa_Empire_Grunt`,
which is not in any Hutt group maker. One pawn in 159 across five raids; recorded, not chased.

## Where this leaves the item
- ✅ all seven appear and generate settlements
- ✅ every Combat group maker fields only our own kinds, all kinds resolve
- ⚠️ **raids: proven for 1 of 7, unproven for 6** — and unproven here means "18 firings produced
  nothing", which is closer to a defect than to missing evidence.
