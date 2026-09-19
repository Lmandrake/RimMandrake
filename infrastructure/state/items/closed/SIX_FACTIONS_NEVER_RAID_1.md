# SIX_FACTIONS_NEVER_RAID_1 — SOLVED: the Raid Protection Fee mod eats the raid and opens a modal

🔴 **ANSWER, measured live 2026-08-30 (FOUNDRY, pass 3), with causal proof:**
A raid fired at certain factions does not fail — **it is replaced by an extortion dialog.**
`Leo.RaidProtectionFee` (`leo.raidprotectionfee`, "Raid Protection Fee", workshop
`3650927927`) prefixes `IncidentWorker_RaidEnemy.TryExecuteWorker` and ends with:

    Find.WindowStack.Add(new Dialog_NodeTree(val4, true, true, null));
    __result = true;
    return false;

It opens a *"pay N silver or be raided"* `Dialog_NodeTree`, **sets `__result = true`**, and
returns `false` so vanilla never runs. The raid happens only when a human answers the modal
(**Reject** → `ResumeRaid` + `SetCooldown(faction, 60000)`; **Accept** → trade, no raid).

⇒ **Not ours. Not a def. Not the ideo. Not the pawn group maker. Not a campaign bug.**
It is a mod feature that a bridge-driven firing can never answer, because nothing clicks.

## The causal proof
Live, Map_0, paused, `ticksGame` 4236, 590 mods, dialogs cleared before each firing,
`jawa/window_list_close` counting `Verse.Dialog_NodeTree` on the window stack:

| faction | Dialog_NodeTree | Lord | pawns arrived |
|---|---|---|---|
| `Pirate` | 0 → **1** | 3 → 3 | **0** |
| `Empire` | 0 → 0 | 3 → **4** | **33** |
| `Salvagers` | 0 → **1** | 3 → 3 | **0** |
| `AM_EnemyPirate` | 0 → **1** | — | **0** |
| `TribalHostile` | 0 → **1** | — | **0** |
| `DP_GenericHostile` | 0 → **1** | — | **0** |
| `Entities` | 0 → 0 | — | **0** ← separate cause, see below |

The failing factions produce **exactly one extortion dialog instead of a raid**; the working
faction produces **no dialog and a real raid**. Evidence and scripts:
`Transient/six_factions_2026_08_30/` (decompile: `decomp/ProtectionFee.cs`).

### ✅ Confirmed on OUR factions too — the title's own claim, finally tested properly
Made genuinely hostile with `jawa/faction_relations_set kind=Hostile both=true` (verified
`hostile: true` on `jawa/list_factions` before firing, so `substituted: false` on every row):

    Jawa_HuttCartel       subst=False   dialogs 0->1   lords 3->3   pawns=0
    Jawa_Junkers          subst=False   dialogs 0->1   lords 3->3   pawns=0
    Jawa_AscendantHelix   subst=False   dialogs 0->1   lords 3->3   pawns=0

Identical signature to vanilla `Pirate`: one extortion dialog, no Lord, no pawns. ⇒ **The
authored factions behave exactly like vanilla ones. Nothing about their defs, kinds, group
makers or ideo is implicated.** Relations restored to `Neutral` / goodwill `0` afterwards.

## Why every earlier symptom now makes sense
- **`executed: true` with zero pawns.** `jawa/fire_raid` sets
  `executed = incident.Worker.TryExecute(parms)`. The prefix assigns `__result = true`
  explicitly. The item was right that a Harmony patch had to be in the path — this is it.
- **Silent.** No `Log.Error`, no letter, no Lord. The mod logs nothing; it opens a window.
- **0.07 s, deterministically.** Successes take 0.3–14 s; every failure returned in
  0.06–0.08 s. It only pushes a window.
- 🔑 **The per-world FLIP.** `WorldComponent_ProtectionFee.factionCooldowns` is a
  `Scribe_Collections`-saved `Dictionary<int,int>` keyed by **`faction.loadID`** and compared
  against `TicksGame`. `OnCooldown(f)` true ⇒ prefix returns `true` ⇒ **normal raid**.
  `loadID` is assigned at worldgen, so the cooldown set differs per world and decays with
  time. **That is the entire "which factions fail flips between sessions" mystery** — and it
  is why the 122-field FactionDef diff correctly found nothing.
- **Non-humanlike factions are exempt:** `if (!HostileTo(player) || !def.humanlikeFaction)
  return true;` — matches `Mechanoid` and `Insect` raiding 8/8 all along.
- **Non-hostile factions are exempt too**, which is why every *substituted* firing "worked".

Settings: no `Mod_3650927927_*` file exists, so the mod runs on **defaults** —
`factionExtortionChances` returns **1.0 for every faction** and
`incidentSourceEnabledStatus["RaidEnemy"]` defaults **true**. Extortion is on for every
humanlike hostile faction that is not on cooldown.

## The one faction this does NOT explain
`Entities` (Anomaly, `humanlikeFaction: false`, hidden) bypasses the fee, opens no dialog,
spawns nothing, and logs nothing. It is not a raiding faction — it carries no usable Combat
group maker for this path. Benign; not pursued. Everything else is accounted for.

## 🔴 The harness defect that produced three retracted tables
**`jawa/fire_raid` at a faction that is not hostile silently substitutes another faction**
(`actual.substituted: true`). In the 2026-08-30 pass-3 census, all ten `hostile=False`
factions — every `Jawa_*` among them — reported `substituted: true` and "succeeded" as
somebody else. **Only `hostile=True` rows are real tests.** Read `actual.substituted`
before believing any row. This is the same defect that voided 2026-08-27, in a new costume.

Real, non-substituted results on this world: `Empire` · `Mechanoid` · `Insect` ·
`AncientsHostile` · `HoraxCult` raid; `Pirate` · `Salvagers` · `AM_EnemyPirate` ·
`TribalHostile` · `DP_GenericHostile` are extorted; `Entities` is inert.

## Hypotheses killed, with the measurement that killed each
- ⛔ **The ideo / meme xenotypeSet hypothesis** (the item's own leading candidate).
  `jawa/faction_ideo_get` on all 15 factions: **every one shares the identical ideo** —
  `Astropolitan`, `ideoId 18`, **`memeCount 0`**, `classicMode true`. Failing and working
  factions have byte-identical ideo input, so `PawnGenerator.XenotypesAvailableFor` cannot
  separate them. Dead.
- ⛔ **`ChoosePawnGenOptionsByPoints` weight-zero.** Never reached — the raid is cancelled
  above it, at `TryExecuteWorker`. (The silent-zero path is real in vanilla and worth
  remembering, but it is not this.)
- ⛔ **FactionDef lists.** `pawnGroupMakers` count, `techLevel`, `permanentEnemy`,
  `raidsForbidden`, `hidden`, `humanlikeFaction`, `earliestRaidDays`, arrival-layer lists
  read live for all 11: `Pirate` has 8 group makers and fails, `AncientsHostile` has 1 and
  works. Nothing separates them.
- ⛔ **`Faction Raid Cooldown`** (`mlie.factionraidcooldown`) patches
  `FactionCanBeGroupSource`, which `TryResolveRaidFaction` **never reaches** when
  `parms.faction` is pre-set. Cannot affect an explicit firing. *(It can still gate the
  storyteller's own selection — untested, see below.)*
- ⛔ **VE Outposts `InterceptRaid`** — no outposts exist in this world.
- ⛔ **MultiRaiders / SWCP / Rimesis / TabulaRasa** group-maker patches — all downstream of
  a cancellation that happens before them.

## Step 4 — the storyteller path: NOT cleanly testable here, and I am not asserting either way
`jawa/storyteller_fire RaidEnemy` returns **`canFireNow: false` for every faction**, working
ones included (`Empire` as well as `Pirate`), on this 3-colonist scratch quicktest whose
default threat points are 232 against the 3000 requested. The gate is not faction-specific,
so it proves nothing about the escalation. **What can be said from the source:** the
`ProtectionFee` prefix sits on `TryExecuteWorker` and does not care how the incident was
chosen, so a storyteller-chosen raid from a humanlike hostile faction off cooldown will get
the same extortion dialog — which in real play is the mod **working as designed**, because a
human is there to answer it. Proving that needs a real colony with enough threat points.

## Consequences
- **Campaign: no defect.** In play the player sees the dialog and chooses. Reject → the raid
  proceeds and the faction goes on a 60000-tick (~1 in-game day) cooldown, after which it
  raids normally again.
- **Bridge testing: a real trap.** Any unattended `fire_raid` at a humanlike hostile faction
  off cooldown reports `executed: true`, spawns nothing, and leaves a `forcePause: true`
  modal on the stack. This is the `stale-modal-blocks-every-later-call` lesson recurring:
  **the variable was a window nobody checked.** Cleared with
  `jawa/window_list_close {action:close, typeName:Dialog_NodeTree, closeAll:true}`.
- Follow-up filed: `FIRE_RAID_REPORTS_MODAL_1` — `jawa/fire_raid` should diff the window
  stack across the firing and report a dialog that swallowed the raid instead of
  `executed: true`.

## criteria
- [x] The 2026-08-27 table is retracted, with its harness defect named.
- [x] `Jawa_DeepwaterCompact` — `raidsForbidden: true` keeps it out of
      `PawnGroupMakerUtility.UsableFactions` and so out of STORYTELLER selection. Not a bug.
- [x] **The mechanism.** `Leo.RaidProtectionFee`'s prefix on
      `IncidentWorker_RaidEnemy.TryExecuteWorker` replaces the raid with a `Dialog_NodeTree`
      and returns `__result = true`. Proven causally by window-stack diff, explained down to
      the saved per-world `factionCooldowns` that made the polarity flip.
- [x] Ours or a mod: **a mod**, and one that is behaving as designed.
- [x] State restored — dialogs closed, map cleared, game paused at tick 4236,
      `ModsConfig.xml` never modified (no minimal tier was needed; no restart was needed).
