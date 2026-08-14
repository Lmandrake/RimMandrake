# infrastructure/state/queue/OPS.md

_OPS's queue. **You own this file — write freely, nobody blocks on it.** Others
file at you by appending. Doctrine is in `agents_def.md`; the v1/v2 line is in
`V1_SCOPE.md`. **Closed items are ONE line in `infrastructure/state/CLOSED.md`,
with the hash — `git show <hash>` has the story. Never keep the body here.**_

⚠️ **`[WORLD]`-tagged items were split, not renamed.** What the world should
*contain* went to `queue/VISION.md`. This file is live-stack work: does it
function, what broke, what is the smallest test.

---

## ⭐ v1 — Row 2, the worldgen faction cut. UNEXECUTED.

🔴 **The whole body of this item is now
`D:\Luke\dev\Rimworld\infrastructure\state\WORLDGEN_FACTION_CHECKLIST.md`** —
ratified, executable, and it *corrects* the proposal that used to live here. Do
not re-derive the exclusion list from this file; it is not here any more.

**Three things a successor must not get wrong, and they are the reason this
section still exists at all:**

1. ⚠️ **A quicktest map's faction roster PROVES NOTHING about the cut.** A debug
   quicktest never visits the Configure Factions page, so every faction is
   present by default. That reading nearly triggered a needless 25–30 min
   regeneration. **State which map any faction census came from.**
2. **Faction removal is a worldgen-time choice at the screen, not a setting.**
   Faction Control's `density` is a **clumping radius** (`__result = dist <
   fd.Density;`), not a count; the English key *"setting to 0 disables the
   faction"* is a pre-1.3 leftover and is what row 2 was originally built on.
   **There is no file we can write to suppress a faction.**
3. **Before calling any missing faction a defect, grep `Jawa_Patches/` for its
   defName.** `OuterRim_RebelAlliance` was reported as a failed generation; we
   had suppressed it ourselves, deliberately, in `RebelAlliance_Suppress.xml`.
   Our own deployed patches are part of the environment.

---

## Open — offline, no game needed

| # | item | note |
|---|---|---|
| **O3** | `loadset_fingerprint()` compares *listed* against *exists* | The `ModsConfig.xml` listed-but-missing trap in code form. WORLD's finding, corroborated by PROJECT. |
| **O8** | `DroidsAreMachines.xml` FAILs `validate_patch.py` on a FALSE POSITIVE | An op under `<match>` whose xpath equals the conditional's own test **can never be a silent no-op** — if the test matched nothing the branch never runs. The patch is correct. Fix: downgrade ERROR→info for that shape. Held out of the lxml change on purpose: it flips an existing FAIL to OK. |
| **O12** | 🔴 **9 × `Error while generating pawn. Rethrowing. NullReferenceException`** — NOT waived, not in the benign list | Thrown from `AlienRace.HarmonyPatches.GenerationChanceGenderless` (`HarmonyPatches.cs:2669`) inside `GeneratePawnRelationsPrefix`. **8 of the 9 cluster on one pawn**, the droid `3C-T0`, immediately followed by `Tried to generate 2 traits for 3C-T0 over 500 extra times and failed` — a race that permits no traits being asked for two. **The droid did spawn** (Isekai Forge enhanced it after), so generation recovered. ⚠️ **The 8 were on a pawn I spawned myself in the ion test, so this may be an artefact of debug spawning rather than a live defect — establish that before waiving it.** The 9th is separate and unattributed. 🔴 **Settle it BEFORE the worldgen session**: relation generation runs for faction leaders, and a failure there is silent. |
| **O13** | `BTDGravshipQuest_GrammarFix.xml` is authored, validated and committed — **NOT DEPLOYED** | `57b6f69`. **xpath CONFIRMED against installed defs** — lxml 6.0.2.0, 34,719 def files, **exactly 1 match, in `[BTD] Gravship Blueprints: Script_BTD_DownedGravship.xml`**. Not a guess and not a static-only pass. Writing a file is not deploying it; the game reads `…\common\RimWorld\Mods\Jawa_Patches`, and nothing syncs the two. Ride the next deploy pass. **Success is a POSITIVE observation** — the Downed Gravship quest showing description text in the Quests tab. The disappearance of `Grammar unresolvable` proves nothing on its own, because the quest may simply not have fired. |
| **O11** | `det.buzzers` emits doubled apostrophes in faction names — a real upstream bug | `RulePacks_Namers_Faction.xml` has `<li>maybeApostrophe->''</li>` where vanilla leaves the RHS **empty**, so the "no apostrophe" branch became a "double apostrophe" branch: one 75% of the time, two 25%, never none. Smoking gun `Caz'vi''vi`. **A one-line `PatchOperationReplace` fixes FUTURE names only** — names bake into the save as strings. 🔴 **So it is worth doing only if it lands BEFORE the new worldgen.** After that, worthless. |

## Open — needs the live game

| # | item | note |
|---|---|---|
| **O4** | Does Faction Customizer's settings dialog persist across worlds? | One minute at the keyboard. The roster's goodwill-cap mechanism depends on the answer. |
| **O5** | Write the three expected-failure signatures **before** the worldgen session | Owner ruled it still stands (does not recall which load was which). A duplicate costs nothing; a missed one costs a load. |

## Open — `[v2]`, not now

| # | item | note |
|---|---|---|
| **O10** | Vibro versus lightsaber on the same target — the L14 thesis | Echani Foil (AP **1.33**) vs Excellent durasteel heavy armour (Sharp 1.05) → effective armour **zero**; the saber got only 27.5 through the same suit. Add a Yautja blade (AP 0.60) to land a tier between them. |

⚠️ **Do not regenerate the armoury patches from a contaminated dump** without
reading `src/RimMandrake/Utils/patch_provenance.py`. The generators anchor
through `observed/2026-08-13/inventory/patch_ledger.json` and print a provenance
banner; `unknown` anchors means **stop**.

---

## 🔴 The game-down batch — mod-list work, mine exclusively, free right now

**A mod-list change only lands on a restart, so all of this is free while the
game is down and costs a ~25 min cycle afterwards.** Collect every seat's pending
request and do them in ONE pass before the next launch.

| ☐ | item | why |
|---|---|---|
| ☐ | Pin the 6 `loadBottom`+`loadAfter` userRules | Order is correct **today** but rides a tie-break, not a constraint. `loadBottom` outranks `loadAfter` — keep it only on `rimdefdump`. |
| ☐ | Retire `mandrake.missingartfixes` (`ModsConfig.xml:560`) | All 7 textures md5-identical to the per-donor successors; blocking dep cleared. |
| ☐ | Run `refresh.py` | Wants the game down. |
| ☐ | **O-v2 — Cherry Picker: remove mechanoid defs AND the `Mechanoid` faction** | Owner's explicit ask. Answer three things: (1) **does the game still load?** (2) does `Samael.NPCMechsAndAnimals` survive and keep its ANIMALS half — `Patches/NPC_Mechs.xml`, 13 ops into `Empire`/`Outlander*`/`Pirate*`/`TradersGuild`? We want the mech half gone, the animal half kept. (3) is that mod configurable — a settings toggle would be cheaper than cherry-picking. ⚠️ **Do NOT remove Alpha Mechs (`sarg.alphamechs`)** — owner wants its cleaners and its animal-looking things available to look at. **Tension to REPORT, not resolve:** Alpha Mechs hangs off `FactionDef[defName="Mechanoid"]/pawnGroupMakers`, so cutting that faction takes its raids too. ⚠️ `matathias.ruthlessmechanoids` is **not** a mech mod — it is the gravship pursuer redirect; leave it on. |
| ☐ | **O-v3 — Enable `vanillaexpanded.vwel` and dump its weapon ThingDefs** | Owner's ask; ws `1989352844`, installed and inactive. **Not a generic weapon pack — owner ruled it narrative:** these are the gravship's legacy armoury, `design/Jawa/worldbuilding/ship_legacy_armoury.md`. **Dump the two tiers SEPARATELY** — `salvaged` (pistol/rifle/shotgun/sniper + `unstable` projectile variants) and `ultratech` (incl. a laser sword and a tesla gun). The split is load-bearing for the design. |

⚠️ **RimSort writes `ModsConfig.xml` too — read its mtime before you write**, or
you clobber a re-sort you cannot see. Measured: the file moved twice in twenty
minutes with the game down.

---

## Standing facts — do not re-derive

**Counts, with their derivation, because quoting a bare number is my
characteristic failure mode:** `grep -c "<li>" ModsConfig.xml` = **585**, minus
**5** `<knownExpansions>` = **580 active**. The def index holds **84,848 rows**
across 436 types but **73,396 UNIQUE** defNames — a name can appear under more
than one type file. **Say which one you mean.**

**`live_mod_inventory.md` is the single source of truth for mod identity** —
existence, packageId, Workshop ID, author, versions. It is GENERATED; regenerate,
never hand-edit. Any doc claiming 562 or 573 active is stale.

⚠️ **`--defnames` does NOT validate xpaths**, only that a defName exists. All 43
patch files passing 0 errors against the live index is real but narrow — an xpath
matching nothing still passes. **Only `--defs` catches that.**

🔴 **Steam Cloud restores deleted saves on launch.** Cloud must be DISABLED for
RimWorld before deleting or the next launch undoes it. Owner's call; not touching
it. Full entry: `traps-mods-and-managers.md`.

**Blockers to play that are not mine to clear:**
1. **Gravship radius unresolved** — Bigger Gravships set to 34 in
   `Config/Mod_3522759531_GravshipSizeSettings.xml`, but it bakes radii into defs
   at **startup**. If this session's defs carry the ~25.9 defaults, **a ship built
   now will not lift and nothing logs why.** BRIDGE owes the `get_def
   GravFieldExtender` call that settles it. **Do not build a ship until then.**

**Do not re-litigate:**
- **V2 Ideology — `[v2]`, owner-deferred. STOP WORK.** Unverified, not failing.
- **Warcasket Heat stays `Cap(0.90)`** — owner: *"They're terrifying."* Wanted.
- **Warcasket deploy: "ship neither."** Both retune files stay in the repo
  undeployed, **permanently — intended state, not drift. Stop reporting it.**
  Asked three ways and answered; re-opening costs the owner twice.
