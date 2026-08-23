# HUMAN — the owner's inbox
> 🔍 **SWEPT 2026-08-22 by REP.** Nineteen sections carry a one-line verdict directly above
> their heading: ⛔ superseded · ✅ already answered · 🔴 still live. **Three are 🔴** — the
> adopt-or-remake sentence (:38), the VQE-Ancients archite ladder (:989), and the dated def
> captures that need a cold load (:1208). Everything else here is history, and reading it as
> a pending question is the mistake this markup exists to stop.
>
> 🔑 **Six of the eight superseded sections are one chain**: freeze → adopt → remake. Every doc
> saying the map is adopted or frozen is downstream of the owner's later *"there is no current
> frozen world."*


🔴 **HAND-WRITTEN. NOT GENERATED. Nothing regenerates this file, and no hook blocks
your edits to it.** Restored 2026-08-20 on the owner's ruling, after the ledger
migration had briefly made it a rendered view.

⚠️ **Why it is not generated, and must not become so again.** Prose written TO the
owner has no home in the ledger by construction — an event carries scalars, an item
file carries spec/verify/criteria, and a briefing is neither. Rendering over this file
is what forced 593 lines of briefings into `infrastructure/state/preserved/HUMAN.md`
to survive the import at all.

🔑 **Owner DECISIONS are items and do live in the ledger.** A seat files one with
`rimflow file --for OWNER --kind decision`, and the owner works them with
`rimflow next --seat OWNER`. Those are tracked, counted on the board, and closed with
a trailer. **This file is for everything that is not shaped like an item.**

---

---

> 📦 **35 settled sections moved to `infrastructure/state/queue/HUMAN_ARCHIVE.md` on
> 2026-08-23**, on the owner's instruction. Everything answered, ruled, resolved or struck
> out lives there verbatim — **this file now holds only what is still waiting on him.**
> Nothing was deleted. A section moved only if its own heading said it was finished, or
> another section in this file demonstrably answered it, and each carries a line saying
> which.

---

## Four species still render magenta, and two rulings disagree about it — 2026-08-19, BUILD
`queue/BUILD.md`'s deploy-pass item says *"CHECK is waiting on the D-CHK2 generator fix
from you — Gand, Selkath, female Chagrian, Jawa mask"*. But D-CHK2 and B66, which folds
it, are both marked `⛔ v2` by your 2026-08-15 blanket triage. Same day, opposite
instructions, so I did not start it.

**It is smaller than the item makes it sound.** Measured today: the broken paths are 4
families, about 25 lines — `OuterRim/Genes/Headbone/ChagrianF`,
`Pawn/HeadAttachments/gand/mask_*`, `Pawn/HeadAttachments/selkath/fishyjowls_female`,
`Pawn/HeadAttachments/yelloweyes/YellowEyes_Female`, and 16 `OuterRim/GeneIcons/*BG`.
The donors still hold every texture, so nothing is lost — only unmigrated.

⚠️ D-CHK2's own offline test is WRONG as written. It says no path may start `UI/`
without the `RimMandrakeSW/` prefix; but `UI/Icons/Xenotypes/Baseliner`,
`UI/Icons/Genes/Gene_Furskin` and a dozen more are **vanilla** paths that must stay
un-prefixed. Only donor-owned paths get rewritten.

Say the word and it is an afternoon in `gen_races_mod.py` plus a re-run. Left alone
otherwise.

## BUILD, overnight 2026-08-20 — `Inhabited` is built, and it needs one decision from you

**The whole of `Inhabited` that could be built without a running game is built, deployed
and pushed.** Eight of the nine queue items are done or built; the ninth needs an answer
that is yours.

> ✅ **ANSWERED BY THE OWNER, 2026-08-20 07:37 — he enabled it.** `mandrake.inhabited` is in
> `<activeMods>`; the set is **578** and LIVE matches FULL. ⇒ **This item's blocking question
> is closed and the debug actions below are collectable on the load now running.** The only
> live decision left here is the four missing character fields, at the bottom.
> ⚠️ The def dump lapsed exactly as BUILD warned; `dump_request.txt` is armed to re-take it
> on this load. **Delete it afterwards** — the marker is not consumed.

~~🔴 **ONE THING BLOCKS IT LOADING, and I deliberately did not do it: `mandrake.inhabited` is
NOT in your `ModsConfig.xml`.**~~ I deployed the mod folder — it is byte-verified in sync at
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Inhabited` — but enabling a
mod changes your load set, and the 2026-08-20 ruling that **the def dump is definitive
lapses the moment a mod is added or removed.** That is your call to make, not mine, and
it interacts with the morning reload plan CHECK filed. Enable it in RimSort when you want
to look at it.

**What you would see once it is on**, all under dev mode → debug actions → category
`Inhabited`:
- `Spawn authored character` — a menu of all **269** people from the eleven cast files,
  by faction and place. Pick one; they arrive with the authored name and exactly the
  authored traits, and the log prints their `ageText` and their hook beside them.
- `Create place at current tile` / `Stuff roster (3 pawns)` / `Report roster` — the
  architecture soak. **This is the one test everything else rests on** and it is written
  up as `ROSTER_SOAK_100_DAYS_1` in `queue/CHECK.md`.

⚠️ **They will look wrong in the body and that is not a bug.** Xenotype, pawnKind, apparel
and skills are the four fields the prose does not carry, so an Ugnaught comes out as a
plain human in whatever the fallback wears. **Those four are the one open decision**, and
DECIDE's `INHABITED_OPEN_QUESTIONS_1` has the shape of it: a review sheet, pre-filled by
RACE rather than per person — there are far fewer distinct races than characters, so it is
a couple of dozen calls, not 269.

🔑 **Two things in the design were factually wrong and would have cost the whole feature
had nobody read the engine.** A roster held off-map is NOT frozen by default — RimWorld
ticks it, and the cast would have starved in a box between visits. And `Caravan`'s own
storage mode is safe only because the world-pawn garbage collector has a hardcoded test
for caravans that a mod cannot join; copied literally, every cast would have been collected
between visits. Both are fixed, both are commented at the divergence, and §3.4 of the
design doc has been corrected in place.

---

> ✅ **BOTH DEFECTS FIXED** — `FACTION_FIXEDNAME_ELEVEN_1` (`00fa712`) and `BLACKSTAR_NEVER_GENERATES_1` (`42ad3ec`).

## 🔴 BUILD, 2026-08-20 09:xx — TWO BAKE-IN DEFECTS IN THE WORLD THAT IS UP RIGHT NOW

Found read-only over the bridge. **I wrote nothing to the game.** Both are the
build-it-once-and-freeze-it class, which is why they are here and not only in a queue.

### 1. Ten of your eleven factions are wearing names the dice picked

`jawa/list_factions` on the live world, against the 578-mod def dump:

| defName | authored `label` | what the WORLD calls it |
|---|---|---|
| `Jawa_Junkers` | the Junkers | **Marina's Asteroids** |
| `Jawa_HuttCartel` | Hutt Cartel | **Southeast Thiourhium** |
| `Jawa_IndigenousTribes` | Jawa Trade Moot | **Union of Aloisa** |
| `Jawa_AscendantHelix` | Ascendant Helix | **Empire of the Sun** |
| `Jawa_DeepwaterCompact` | Deepwater Compact | **Menussia Coalition** |
| `Jawa_FreeDroidEnclaves` | Free Droid Enclaves | **Northeast Notthdos** |
| `Jawa_GeonosianFoundryHive` | Geonosian Foundry Hive | **The Latovas Union** |
| `Jawa_WildsteamClan` | Wildsteam Clan | **The Banastra Nation** |
| `OutlanderCivil` | Homestead Defense League | **Treaty of Haor** |
| `TribeCivil` | Deep Desert Tribes | **The Lánéa Nation** |
| ⭐ `Empire` | The Galactic Empire | ✅ **Galactic Empire** |

🔑 **The Empire is right for exactly one reason: it is the only faction with a
`fixedName`.** Every other def has `label` correct and `fixedName` **None**, so RimWorld's
name generator named them at world creation. **This is precisely the trap that
`GalacticEmpire.xml` exists to avoid**, and which I rewrote into
`Jawa_Patches/About/About.xml` this morning — `label` is the def's display label,
`fixedName` is the name the world object actually carries.

🔴 **AND ADDING `fixedName` NOW WILL NOT FIX THIS WORLD.** `Faction.Name` returns the
STORED name if one is set, and these have one:
```
public string Name { get { if (HasName) return name; return def.LabelCap; } ... }
public bool HasName => name != null;
```
The generated strings are already baked onto the faction objects in this save. So it needs
**two** fixes, and the second one does not substitute for the first:
  1. **rename the ten live factions in this world** — nothing on the 237-tool bridge does
     it (`jawa/` has `list_factions`, `faction_relations_*`, `set_pawn_faction`, and no
     rename), so it is a debug action or a small companion tool;
  2. **add `fixedName` to the ten defs**, so this cannot recur if the world is ever rebuilt.

### 2. Four settlements are missing, and they are all one faction's

`world/ASHKARR_WORLDMAP_settlements.csv` holds **72** rows. The live world has **68**.
The gap is not scattered — **it is exactly Blackstar Company's four**: Blackstar Field
(tile 18266), The Contract Camp (8898), Toll Rock (2236), Hardpan Yard (7497).
**Cause:** their `faction_def` is `AM_EnemyPirate`, and that faction **is not in the
world** — the world has 16 factions and it is not one of them. Every other faction's count
matches the CSV exactly, so the importer skipped these four rather than failing.
⇒ Either Blackstar needs a vessel that exists, or those four rows come out of the CSV.

⚠️ **Not a defect, checked and cleared:** 80 world objects have a null faction and the tool
warns those "die on load" — **all 80 are asteroids and one derelict station**, which
legitimately have no faction. **Zero settlements among them.** No action.

---

> ✅ **DONE** — the faction rename this says nobody can do landed at `00fa712`.

## 🔴 Vanilla Psycasts Expanded is not installed, and nothing decided to drop it — BUILD, 2026-08-20

**One line of your mod list, and it is yours to change. I have not touched `ModsConfig.xml`.**

Verified three ways just now:

| | |
|---|---|
| `ModsConfig.xml` | **578 activeMods, zero** matching `vpsy` / `psycast` — parsed as XML, not grepped |
| on disk | **subscribed**, `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2842502659` |
| dependencies | Royalty, Harmony and VEF Core are **all active**. Nothing forced it out |

⚠️ **No document records a decision to drop it, and two LIVE documents say the opposite:**

- `design/Jawa/mods/required_mods.md:632` — *"✅ KEEP: Vanilla Psycasts Expanded (VPE) … **the sole Force substrate**"*
- `design/Jawa/mods/forbidden_mods.md:63` — *"VPE is **KEPT installed** as the NPC-only 'THE FORCE' substrate"*

🔑 **This is why 61 of the 287 dangling citations dangle.** They are not 61 stale names —
they are one absent mod. ⛔ So nothing should be "fixed" in the docs; the defNames are
correct.

**What it costs if it stays out:** the docs are explicit that VPE is what makes enemy
psycasters actually cast — it ships the enemy-cast AI and a storyteller that force-spawns
them, where vanilla enemies never psycast. Without it, THE FORCE has no substrate and the
Jedi/Sith layer is inert rather than broken, which is the quiet kind of failure.

⚠️ **`force_users_build_spec.md` found this on 2026-08-13** — lines 91, 206, 996 and a
`[BUILD]` item at 1095 — and it never propagated back into `required_mods.md`, which still
reads KEEP. That is exactly the `CLAUDE.md` failure: *superseding a doc means writing INTO
the doc you superseded.*

**Your options, and I am not choosing:**
1. **Re-activate it** — one line in `ModsConfig.xml`, and the 61 citations resolve. ⚠️ It is a
   C# mod, so it needs the game down and a load to prove.
   ✅ **Re-activate, not re-subscribe — corrected 2026-08-20.** `force_users_build_spec.md:94`
   and `:995` said *"no folder in the workshop tree owns `VanillaExpanded.VPsycastsE`"*. That is
   false: folder `2842502659` is on disk. It changes the remedy from a download to a checkbox.
2. **Confirm it is out on purpose** — then `required_mods.md` and `forbidden_mods.md` are
   wrong and I will correct them, and THE FORCE needs a different substrate or a v2 tag.

I have filed the doc-currency half either way; only the mod list itself is waiting on you.


> ✅ **ANSWERED 2026-08-22 10:57 — owner: *"We are leaving in for v1. We will deal with it more
> in v2 properly."*** ⇒ ⛔ Cherry-Pick nothing out of the VQE-Ancients archite-power ladder for
> v1. Filed to `design/V2_DREAMS.md > ARCHITE_LADDER_RETHINK_2`.
