# RimBridge traps: pawns, factions, raids and combat

Part of the trap catalogue indexed in [../traps.md](../traps.md); its first law and admission test are there. Append a new trap to the topic file it belongs to.

## `jawa/list_pawns` returns `kind`, not `kindDef`
**Symptom:** 8 pawns spawned, `jawa/spawn_pawn` returning `success: true` with real ids, names and coordinates; the next `jawa/list_pawns` filtered on `p["kindDef"] == "Jawa_Spawn_Hutt"` returned **0**, and "neutral pawns despawn instantly" was stated out loud. Re-run against `kind`: **7 alive**, exactly where spawned.
**Cause:** there is no `kindDef` key, so `p.get("kindDef")` was `None` for every pawn and the filter matched nothing. A `KeyError` would have been caught instantly. "Faction `none` pawns are transient" is real RimWorld behaviour, so the wrong answer sounded like knowledge and survived three follow-up calls.
**Fix:** `print(json.dumps(pawns[0])[:300])` before trusting any filter — what are the keys ACTUALLY called — plus a named control: query something you know exists and confirm the filter finds it.
**Recurs when:** any `.get()`-based filter over a dict you did not define. An empty result is a claim about your query until proven a claim about the world.


## 🔴 A parameter you PASS is not a parameter that SURVIVES — the raid faction is rewritten by ref
**Symptom:** `jawa/fire_incident incidentDef=RaidEnemy faction=Empire` returns `success: true`  *(example re-pointed 2026-08-20: the Galactic Empire's vessel is vanilla `Empire`, not ~~`OuterRim_GalacticEmpire`~~ — `infrastructure/state/OWNER_DECISIONS.md`. The trap itself is unchanged.)*, a raid arrives, and it is **somebody else's raid**. Nothing in the reply flags the swap. The screenshot taken to answer *"does the Empire read as an antagonist"* is a photograph of a different faction.
**Cause, read out of `Assembly-CSharp` rather than recalled:** `IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps the faction you supplied **only if** it is non-null **AND** `FactionUtility::HostileTo(Faction.OfPlayer)` **AND** (`!deactivated` **OR** `parms.forced`). IL_001f, IL_0036 and IL_0055 all branch to IL_0059, where `ldflda IncidentParms::faction` passes the field **by reference** into `PawnGroupMakerUtility::TryGetRandomFactionForCombatPawnGroupWeighted` — which overwrites it with a weighted random pick. `IncidentParms` is a class, so the mutation is visible to the caller and invisible to anyone who does not look.
**Fix:** `dryRun=true` first and abort on `canFireNow:false`; then fire and **read the `faction` field in the REPLY, never the one you sent** — the companion reports `parms.faction` *after* the worker ran, so the read-back is the only evidence of which faction actually came. Pass `points` explicitly too: `points<=0` takes the storyteller default, which on a fresh quicktest is tens of points and answers no design question.
**Recurs when:** any engine worker taking a mutable parms object — raids, quests, trader arrivals. ⚠️ **Generalises past `IncidentParms`, and this is the half to carry: assert on the value READ BACK, never on the value sent.** Same shape as an unknown parameter name being dropped silently, arriving from the opposite direction — there the name never reached the tool, here it reached it and was overwritten. Both report `success: true`.

## ⚠️ Nothing on the bridge orders an ATTACK
No verb issues `JobDefOf.AttackMelee`. A drafted colonist holds at `Wait_Combat`
forever; `jawa/order_pawn` issues a GOTO whether given `targetId` or the enemy's own
cell; pawns from `jawa/spawn_pawn` have **no lord** so hostiles idle; and
`Actions\Spawn large enemy raid` plus 5,600 stepped ticks never produced an engagement
at the drafted pawn. Any "what does it look like DURING an attack" item is therefore
uncollectable unattended today.
Equipping, by contrast, is solved: `rimworld/select_pawn`, then
`Actions\Equip primary (selected)...\<WeaponDefName>` (808 leaves).
⛔ `Actions\Play Animation...` does not substitute — 208 leaves, **zero** `AM_` ones.
Melee Animation's 33 `AM_Duel_*`/`AM_Execution_*` AnimDefs are in the def dump but are
not exposed to that menu; they fire from real melee jobs only.

## ⚠️ `jawa/list_pawns` cannot tell you what a pawn is HOLDING
There is no equipment/weapon field — the record is id, kind, xenotype, position,
health, flags. `rimworld/get_selected_pawn_inventory_state` reads INVENTORY, not the
equipped primary. The cheapest reliable read of a primary weapon is a **screenshot of
the Gear panel** ("Equipped: Lightsaber (normal)"), which is also independent evidence
rather than the equip call's own `success`.

## `jawa/destroy_batch` will not destroy pawns, and says so quietly

Same session. `rects` (not `thingIds`) is the required argument, and the reply ended
`"Destroyed 2 thing(s) across 9 cell(s); 2 pawn(s) left alone."` — the two pawns were
the entire point of the call. The refusal is real and it is in the message, but the
call is a `success`, so a script that checks only the flag deletes nothing and moves on.

## Nothing reaches a `VehiclePawn`'s UI or its comps — four routes, four dead ends

- `rimworld/select_pawn` refuses it by id AND by name — *"Could not find player-controlled
  colonist"* — even though `jawa/set_pawn_faction` answers *"Pawn is already in
  PlayerColony"*. It filters on colonists and a `VehiclePawn` is not one. No selection ⇒
  `list_selected_gizmos`, `open_inspect_tab` and `get_ui_layout` all have nothing to read.
  **Not vehicle-specific — this is the general `Pawn.IsColonist` gate**, confirmed later to
  block ordinary bridge-spawned humanlike pawns too; see the dedicated entry below.
- `jawa/get_defs` with `fields: "components"` returns `["VehicleComponentProperties" × 5]` —
  the reflective reader flattens list elements to their class name and does not descend.
  `jawa/get_def` returns `comps` (the `CompProperties` list), which is a **different field**
  from `components` (the damageable parts).
- No tool anywhere mentions fuel or refuel; the only two vehicle debug actions on the whole
  583-mod stack are `Ground All Aerial Vehicles` and one mod's own list action.
- `rimbridge/run_lua` does **not** rescue this. It compiles a lowered subset and executes
  *"through the normal capability registry"* — it orchestrates existing tools, it does not
  reflect into game objects.

⇒ A vehicle's fuel level and health-tab labels are **unreadable from the bridge today**.
Say UNMEASURED; do not infer one from a hauler that did or did not move.

## 🔴 `jawa/pawn_stats` — a stat that APPAREL moves must be read on a STRIPPED pawn

Measured 2026-08-26 on the tool's first real use, and it very nearly shipped a wrong answer.

`ComfyTemperatureMin` / `ComfyTemperatureMax` include worn apparel's insulation. Spawned pawns come
dressed by the generator, so reading them compares **clothes**, not xenotypes:

```
dressed   Baseliner -56.32 ... 47.50    MandrakeJawa -77.32 ... 60.28
          three xenotypes with NO temperature gene at all read -74.76, -55.92 and -88.80
```

🔑 **Three gene-free xenotypes disagreeing by 33 °C is the tell.** Strip first:

```
jawa/pawn_gear {pawn: <id>, action: "clear", clearWhat: "apparel"}
```

```
stripped  Baseliner / Ugnaught / Twilek / KelDor   -40.00 ... 45.00   (identical, no gene)
          MandrakeJawa    -50.00 ... 55.00   Small down + Small up
          RimMandrakeChiss  -60.00 ... 40.50   Large down + MaxSmall down
          RimMandrakeWookiee -60.00 ... 55.00   Furskin STACKS a further -10 on the min
```

⇒ Gene tiers, measured: **Small = ±10 · Large = −20 on min · `MaxTemp_SmallDecrease` = −4.5.**
⚠️ The same discipline applies to any stat apparel, a weapon or a hediff can move. The tool reports
the instance faithfully; the instance is just wearing something.

## 🔴 A raid census taken immediately after `jawa/fire_raid` reads ZERO — 2026-08-27, BUILD

**Symptom.** `jawa/fire_raid` returns `executed: true, "Raid fired."`; `jawa/list_pawns` run
straight afterwards shows **no new pawns**. Reads exactly like a raid that never fired.

**Cause.** The raid is in flight. Measured: a raid fired at tick T had **0** new pawns at
+60 ticks and **19** at +300, on a paused game (the pawns appear as `step_game_ticks` runs).

**Fix.** Step ticks in stages and census after each — `+60, +300, +1200` — before concluding
anything. ⛔ A zero taken immediately is not a result.

**Generalises to:** any incident with an arrival mode. `success: true` tells you the worker
ran; arrival is a later tick, and on a paused game it is a tick you must supply yourself.


## Doctrine-verify 2026-08-29: turret and explosion combat tests need three separate fixes, none of them the def

**A PAUSED explosion reads as a no-op.** `jawa/explosion_at` succeeds, an `Explosion` Thing
appears, and nothing is damaged until `step_game_ticks` runs it. Judging the result at call
time files a working tool as broken (2026-08-30, FOUNDRY).

**Turret combat tests need all three of these, or nothing engages:**
* `spawn_thing` leaves a turret **factionless** — set `PlayerColony` (or the appropriate
  faction) explicitly or it never engages anything.
* **Spawned hostiles RUSH the turret into its minimum-range dead zone.** Spawn slow or far
  targets, not adjacent ones, or the turret never fires a shot worth measuring.
* `step_game_ticks` **does run turret AI** even under a stepped pause — a slug turret fired
  during a stepped-tick test, so "paused" is not "inert" for anything already spawned and
  targetable.

**And the def dump cannot settle a numeric patch here at all:** it serialises NO projectile
block and no `DamageDef.defaultDamage`, and `jawa/get_def` has no projectile field either.
Numeric weapon-patch verification needs the mod-XML + validator + log chain, or live fire —
not a def read.


## 🔴 `jawa/set_faction_relation` CANNOT make a neutral faction hostile — 2026-08-27, BUILD

**Symptom.** `jawa/set_faction_relation {faction, kind:"Hostile", goodwill:-100}` returns
**`success: false`** with:

    kind Neutral -> Neutral, goodwill 0 -> -100.
    ⚠️ READ-BACK DOES NOT MATCH THE REQUEST — the engine overrode it.

It writes the goodwill and never flips the relation kind, leaving `goodwill -100` with
`hostile: false` — a faction that will never raid.

⭐ **The refusal is the tool working.** It verified its own write and refused to report a
success it had not achieved. ⛔ **But its own description says it "Exists to unblock aimed
raids", which is exactly what it does not do** — do not trust that sentence.

**Fix.** Use **`jawa/faction_relations_set`** instead:

```python
rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile",
                                       "goodwill": -100, "clampGoodwillToKind": True,
                                       "both": True, "sendLetter": False})
# -> kind Neutral->Hostile (reverse Neutral->Hostile); list_factions then reads hostile: true
```

**Why it matters.** An incident worker silently substitutes a random faction for one that is
not hostile — so this failure does not look like a failure, it looks like a raid from the
wrong faction. Confirmed twice the same session: an aimed `Jawa_HuttCartel` raid delivered
19 `AG_XenohumanPirates`, then 12 `GiantAnt`, while `resolved.faction` echoed
`Jawa_HuttCartel` both times.

**Generalises to:** two tools with overlapping names where the narrower one carries the
broader one's promise in its description. Read what a tool DID from its read-back, never
from what it says it is for.


## 🔴 `jawa/pawn_get` nests everything in `pawns[0]` — 2026-08-27, BUILD

**Symptom.** `resp.get("equipment")` returns nothing for every pawn, printing as
*"8 of 8 BARE"*. This is the documented false reading that once produced the conclusion
"all Jawa spawn bare-handed", and it was hit again.

**Cause.** The payload is `{"success": true, "count": 1, "pawns": [ {...everything...} ]}`.
`equipment` and `apparel` live inside `pawns[0]`, not at the top level.

**Fix.** `d = (resp.get("pawns") or [{}])[0]; eq = d.get("equipment") or []`.
⚠️ And entries are keyed **`def`**, not `defName` — `{"def": "guy762_ionpistol", "stuff": null,
"isPrimary": true}`. Reading `.defName` gives `None` for a fully armed pawn.

**Generalises to:** an empty collection from a bridge read is a shape hypothesis, not a
measurement. Dump the RAW response once per tool before believing any absence.

## 🔴 `jawa/set_faction_relation kind=Hostile` cannot make an ordinary faction hostile

2026-08-30, live, 590-entry list. Setting `{faction: <any normal faction>, kind: "Hostile"}`
returns `kind:{was:"Neutral", now:"Neutral", asked:"Hostile", ok:false}` and
`hostileToPlayer:false`. Setting `goodwill:-100` instead writes the number and leaves
`kind` Neutral, so `HostileTo(player)` is STILL false at goodwill −100.

**Cause, from the engine.** The tool calls `Faction.SetRelationDirect`, and
`RimWorld/Faction.cs:641` refuses outright when both sides carry goodwill:

    if (HasGoodwill && other.HasGoodwill) { Log.Error("Tried to use SetRelationDirect for
        factions which use goodwill. The relation would be overriden by goodwill anyway."); return; }

`HasGoodwill` is `!Hidden && !temporary` — true for essentially every faction and for the
player — so the write never happens. `SetRelationDirect` is for mechanoids, insects and
permanent enemies only. And a bare `baseGoodwill` assignment does not derive `kind`:
only `FactionRelation.CheckKindThresholds`, reached through `TryAffectGoodwillWith`, does.

✅ **Use `jawa/faction_relations_set`** (`faction`, `other:"Player"`, `kind:"Hostile"`).
It picks the write path off the pair — `SetRelationDirect` only when one side lacks
goodwill, otherwise a direct record write on BOTH sides followed by
`Notify_RelationKindChanged`, which is what makes live pawns re-target.

**What it cost:** the whole 2026-08-27 evidence body of `SIX_FACTIONS_NEVER_RAID_1` —
18 raid firings recorded as "each faction was verified hostile" when none of them was.
`IncidentWorker_RaidEnemy.TryResolveRaidFaction` silently substituted a genuinely hostile
faction each time, so the item's headline asymmetry was an artifact of the harness.
The tool did report `ok:false` and `success:false`; nobody read the field.

**Generalises to:** any bridge write whose result carries a `was`/`now` read-back —
assert on the read-back, not on `success`, and not on the absence of an exception.

**Confirmed again 2026-08-31, FOUNDRY.** A script that read only `success` fired
`jawa/set_faction_relation kind=Hostile` at seven factions and had all seven silently
substituted — the tool had already answered `success: false` and *"⚠️ READ-BACK DOES
NOT MATCH THE REQUEST — the engine overrode it"* every time, with `kind {was, now,
asked, ok:false}` right there. **It is not a silent no-op — it is a refusal the caller
did not read.**


## Killing a test pawn through the bridge — single damage calls lie
`rimworld/execute_debug_action` "Damage To Death" NRE'd silently on 2 of 34 pawns, and `jawa/damage` Cut 500 on a raider reported success and left it alive. Reliable: `pawn_force_incapacitate` then kill, or loop `jawa/damage {thingId:<bare id>, amount:large, damageDef:Bomb}` until the response reads `dead:true` (amount is a request, not a delivered result). `jawa/debug_settings` takes `field`/`value`, not `name`.

## Spawning pawns — `jawa/spawn_pawn` works; the `GenSpawn` routes NPE
- **The `Spawn Pawn...` debug action NPEs on every pawn defName on a VEF-loaded list, same as `rimworld/spawn_thing`; use `jawa/spawn_pawn`.** Do not "fix" it by removing `sarg.alphaanimals`: that breaks `ScenPart_StartingAnimal` with a different NPE, because some SWBestiary defs inherit from an Alpha-Animals parent or field.
