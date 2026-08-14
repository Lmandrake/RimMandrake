# Faction engine gap audit — Stage 2

_Written by **PROJECT**, 2026-08-12, against the faction roster Stage 2 work
(now `infrastructure/state/queue/VISION.md` **V9**). Audits
`file:///D:/Luke/dev/Rimworld/design/Jawa/worldbuilding/faction_roster_v2.md` (2,433 lines,
12 faction dossiers) against what RimWorld's `FactionDef` actually accepts._

**Stage 2 asked: "is every field RimWorld needs actually decided, or only the
fiction?" The answer is not a per-faction scorecard, because the gap is not
per-faction.**

> **The roster is not underspecified. It is specified in a vocabulary that does
> not reach the engine.** Its 12 dossiers are internally consistent and decide a
> great deal — but most of what they decide is not a `FactionDef` decision, and
> the roster nowhere states which live def each faction is supposed to become.

Sources, and which is authoritative for what, is itself a finding — see §5.

---

## 1. The primary gap: no faction has a vessel

**The roster names zero defNames.** `grep -c defName faction_roster_v2.md` = **0**.

All 12 dossiers are hand-authored designs. None says whether it is meant to be a
new `FactionDef` of ours, a `PatchOperation` against a live one, or a reskin of
something already loaded. That decision is Stage 4's, but **it is the decision
every other engine field depends on**, because the field list you must fill
differs completely between "author our own" and "patch theirs".

| # | roster faction | plausible live vessel | status |
|---|---|---|---|
| 1 | Hutt Cartel Confederacy | none — `OuterRim_BinaryStarRaiders` already used as Hutt muscle by our `GamorreanPawnKinds.xml` | **unassigned** |
| 2 | Imperial Desert Directorate | `OuterRim_GalacticEmpire` and/or `Empire` (Royalty) | the two-Empire design exists; not written as a def decision |
| 3 | Outer-Rim Homestead Compact | `OuterRim_MoistureFarmers` (live, 8 `pawnGroupMakers`) | **best-placed of the 12** |
| 4 | Tusken Sand Clans | none identified | **unassigned** |
| 5 | Free Droid Enclaves | none — confirmed absent, U3 | **unassigned, and known** |
| 6 | Wookiee Freeholds | none identified | **unassigned** |
| 7 | Aquifer League | none identified | **unassigned** |
| 8 | Geonosian Foundry Hive | none identified | **unassigned** |
| 9 | Arkanian–Kaminoan Gene Consortium | none identified | **unassigned** |
| 10 | Bounty Hunters' Compact | none identified | **unassigned** |
| 11 | Indigenous Jawa Clans | the player faction | different problem |
| 12 | Junker Scrap-Warrens | none identified | **unassigned** |

⚠️ **The "plausible vessel" column is PROJECT's inference, not a ruling.** Only
#3 and #5 rest on recorded work. Do not treat the blanks as "no vessel exists" —
they mean **nobody has looked**, and 88 live `FactionDef`s were never searched
for candidates.

---

## 2. The roster's parameters mostly are not `FactionDef` fields

Every dossier carries the same 12-row **Faction settings** table. Mapping those
rows to the real schema:

| roster parameter | `FactionDef` field | verdict |
|---|---|---|
| Tech level | `techLevel` | ✅ **direct** |
| Permanent enemy | `permanentEnemy` | ✅ **direct** |
| Trader types | `caravanTraderKinds`, `baseTraderKinds`, `visitorTraderKinds`, `orbitalTraderKinds` | ✅ direct, but needs `TraderKindDef`s named |
| Settlement leadership | `leaderTitle`, `fixedLeaderKinds` | ✅ direct |
| Raid frequency | `raidCommonalityFromPointsCurve`, `earliestRaidDays` | ⚠️ curve, not a word — "Medium, distance-scaled" is not yet a value |
| Typical settlement defenders | emerges from `pawnGroupMakers` + points | ⚠️ **indirect** — a count is an outcome, not an input |
| Combat-droid share | `pawnGroupMakers` option weights | ⚠️ **indirect** |
| Target settlements | `settlementGenerationWeight`, `requiredCountAtGameStart`, `maxCountAtGameStart` **+ Faction Control config** | ⚠️ **split across two layers** (U1) |
| Settlement distribution | Faction Control `CenterPoint` / `factionGrouping` | ❌ **no def field at all** (U1) |
| **Starting goodwill** | **none — see §3** | 🔴 **no mechanism at either layer** |
| Base wealth | none | ❌ **no def field** — settlement wealth is generated |
| Caravan frequency | none | ❌ **no def field** |

**Four of twelve map cleanly.** The rest are indirect, split across layers, or
have no home at all. **That is the Stage 2 finding**: Stage 3's "someone could
write the XML from this document" test cannot be met by adding detail to the
existing table, because half its rows are not XML-expressible.

---

## 3. 🔴 "Starting goodwill" is specified 12 times and has no mechanism

Every dossier sets it — Hutt Cartel −35, and so on for all twelve. **It is not a
`FactionDef` field.** Probed across all 88 live defs and all 125 fields: **zero
hits** for `goodwill` in any form.

**And it is not in Faction Control either**, which is what settled U1. That mod's
entire settings schema is:

```xml
<ModSettings Class="FactionControl.Settings">
  <masterDensity>…</masterDensity>
  <factionDensities><li><faction>…</faction></li>…</factionDensities>
</ModSettings>
```

— `file:///C:/Users/Mandrake/AppData/LocalLow/Ludeon%20Studios/RimWorld%20by%20Ludeon%20Studios/Config/Mod_2882785581_Controller.xml`

**Density only. No goodwill, no relations.**

### ⚠️ AMENDED same day — a candidate mechanism exists, and my first check was the wrong layer

**The config-file evidence above is sound for Faction Control but was the wrong
source to generalise from.** A RimWorld `Mod_*.xml` records only what has been
*changed*, never what a mod *supports*. Re-checked against the assemblies:

| mod | assembly evidence | verdict |
|---|---|---|
| **Faction Customizer** (`azravos.factioncustomizer`, 1.6 present) | `Dialog_ModifyFactionRelation`, `baseGoodwill`, `naturalGoodwillOffset` | ✅ **can set base goodwill** |
| Faction Control | `IsRandomGoodwillLoaded` only — a **compat probe for a different mod**, not a feature | ❌ confirmed |
| Sensible Factions | `biome` only | ❌ ruled out |
| *Random Goodwill* | — | **not installed** |

**§4's finding is unchanged:** no `FactionDef` field expresses goodwill, so line
42 is still wrong. What changes is where goodwill lives — **a third-party runtime
mechanism**, not a def and not a settings file.

⚠️ **The open question decides whether the 12 numbers survive.** Faction
Customizer's editor is a **`Dialog_`** acting on live world state. It carries
`ModSettings` + `Scribe_Values` + `ExposeData`, so it *may* persist across
worlds — **unproven**; no `Config/Mod_3336572602*.xml` exists, which proves only
that its settings have never been touched.

- **persists as mod settings** → the 12 numbers are authorable, keep them
- **world/save state only** → each is a manual click per world roll, and 12
  precise values become a liability in a reproducible campaign. Collapse them to
  the engine's coarse hostility booleans.

**Do not design further on goodwill numbers until that is answered.** U1's
treatment still applies — now against a named candidate rather than nothing.

**What the engine does give**, and it is coarse: `permanentEnemy`, `naturalEnemy`,
`mustStartOneEnemy`, `permanentEnemyToEveryoneExceptPlayer`,
`hostileToFactionlessHumanlikes`. Those are booleans about *hostility*, not a
signed integer of *goodwill*. **A −35 does not exist in that vocabulary.**

---

## 4. ⚠️ The roster's own claim list contains the error

`faction_roster_v2.md:42` states what is expressible:

> `FactionDef` technology level, **goodwill**, permanence of hostility, traders,
> pawn groups, settlement generation

**"goodwill" does not belong in that list.** Everything else on the line is
correct. This is the load-bearing kind of error: it is the sentence that
authorised twelve dossiers to specify a goodwill number, so the mistake is
upstream of all twelve.

**Recommended action: WORLD (who owns `design/Jawa/worldbuilding/`) strikes `goodwill` from
line 42 and adds a pointer to §3 here.** Not fixed by PROJECT — rule 9, the doc
is owned by whoever owns the subject. Filed, not edited.

---

## 5. Two method findings that outlive this audit

### "125 distinct fields" is a schema, not a checklist

`infrastructure/state/queue/VISION.md` **V9** records **88 `FactionDef`s and 125 distinct fields** as the Stage 3
checklist. Measured against the dump: **all 125 fields are present on all 88
defs** — the dump serialises defaults. So 125 is the size of the *schema*, not a
list of decisions anyone made.

**24 fields never vary at all** across the 88. Most of the rest have a dominant
default and two or three exceptions. **The real decision surface is far smaller
than 125**, and it is dominated by one field: `pawnGroupMakers`, which has 50
distinct shapes across 88 defs and is where a faction's actual behaviour lives.

**Recommendation: Stage 3 should be organised around `pawnGroupMakers` first**,
not around a 125-row table. A faction with every scalar decided and no pawn
groups cannot field a pawn — that is exactly the `OuterRim_RogueDroidColony`
finding, already recorded in §0.

### 🔴 The def dump is a POST-PATCH artifact — wrong layer for "what does the mod ship?"

**PROJECT filed a wrong finding from this and WORLD caught it in five minutes.**
Recorded here because this audit's data comes from that dump.

The dump's identity is **"what the game loaded"** — and that includes *our own
patches*. It is therefore structurally the wrong source for any question of the
form *"does the mod already do X?"*. Full write-up: `skills/rimworld-modding/references/traps-tooling.md` §"An artifact that records an OUTCOME cannot answer a question about a CAPABILITY".

**Bounded for this audit** — of the ten Star-Wars-relevant live `FactionDef`s,
our patches modify exactly one:

- `OuterRim_RebelAlliance` — **modified by `Jawa_Patches/Patches/RebelAlliance_Suppress.xml`**; dump readings invalid
- `OuterRim_BinaryStarRaiders` — only *referenced* as a `defaultFactionDef`; def untouched
- the other eight — clean of our patches

⚠️ **"Clean of our patches" is weaker than "as shipped"** — third-party mods patch
each other, and the dump is post-*all*-patches. For any load-bearing claim about
shipped behaviour, read `…/workshop/content/294100/<id>/1.6/Defs/…` directly.

---

## 6. What Stage 3 should do differently

1. **Assign a vessel to each of the 12 first.** Every other field depends on it,
   and 88 live defs have never been searched for candidates.
2. **Re-cut the Faction settings table** so its rows are engine rows. Keep the
   fiction, but stop implying the table is buildable.
3. **Resolve goodwill's mechanism, or drop the numbers.** Twelve precise values
   currently rest on nothing.
4. **Lead with `pawnGroupMakers`.** It is where behaviour lives and where the
   only confirmed vessel gap (U3) was found.
5. **Read shipped behaviour from workshop XML, never from the dump.**

**Not started here, and deliberately:** the per-faction field-by-field fill. That
is Stage 3, and doing it before step 1 would produce values for defs that may
never exist.
