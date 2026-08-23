# HUMAN — ARCHIVE. Settled questions and rulings, kept verbatim.

**Nothing here is pending.** Every section below was answered, ruled, resolved or struck
out. They were moved out of `queue/HUMAN.md` on 2026-08-23 on the owner's instruction:
1,527 lines had accumulated, 33 of 43 sections were dated 08-19 to 08-21 and already
settled, and the handful of questions still waiting on him were buried among them.

⛔ **MOVED, not deleted, and that distinction is the point.** A ruling's wording is the
authorization for what was built on it, and `POLICY.md` is right that deleting the record
breaks the trail. Every section is byte-identical to how it stood in `HUMAN.md`; the only
addition is one line under each saying why it moved.

🔑 **A ruling here is not doctrine.** Where one still binds, it was propagated into the
file that carries it — `CLAUDE.md`, `POLICY.md`, `GAME_STATE_WORKFLOW.md`, or the item.
Read those to know what is TRUE; read this to know what he actually SAID.

⚠️ **Two of these retire each other and the later one wins:** *WORLDMAP_gen IS THE
FIRST-DRAFT v1 KEEPER* (02:48) was retired by *THERE IS NO KEEPER WORLD* (10:17) — and
retired again on 2026-08-23: *"There is no keeper savegame yet, we only have a worldmap
as a csv so far."*

---

## ✅ ANSWERED SAME DAY — THE GUNS STAY GONE

🔴 **Owner, 2026-08-22, verbatim: *"I like the vanilla weapons being gone, to amplify the
Star Wars flavor."*** The eight vanilla industrial guns stay cut. Theme beat balance, and
the anti-scarcity cost the 2026-08-03 audit warned about was accepted knowingly.

**Propagated the same hour, into every file that said otherwise:**
`canon.yml > VANILLA_FIREARM_LINE_CUT_1` (so the hook now refuses a design doc that
contradicts it) · `design/RimMandrake/Custom_World.md:110`, whose audit is struck and
overruled · `design/Jawa/mods/required_mods.md:730`, where **"vanilla low-tech" is now
spelled out as NEOLITHIC** — bows and clubs, not revolvers. That ambiguity is the whole
reason the sentence read as an argument against the cut for three weeks.

⚠️ **One slice is reversed and only one:** the Mech weapons. ⛔ Do not read that narrow
reversal as a broad one — three items closed this morning were caused by exactly that.

<details><summary>the question as it was asked, kept for the record</summary>

> ✅ **ANSWERED 2026-08-22 10:57 — AND THE QUESTION WAS THE WRONG SHAPE.** It asked "adopt or
> remake". Neither. The owner: *"DECIDE and I have an out of game map we are working on together.
> It is not frozen/finalized, and then we need to successfully show that it can survive a port
> into the game through the live bridge. Simultaneously, we are working to define the factions,
> leadernames, ideoligions, etc. because those must be finalized and correct at game initiation
> it turns out. Once all that is done, then we can finally save a game and meaningfully freeze it
> as the embodied world."* ⇒ 🔑 **The freeze is a SAVEGAME**, and three things stand between here
> and it: the out-of-game map, a **port-survival proof through the live bridge**
> (`WORLD_PORT_SURVIVES_BRIDGE_1`), and the faction/ideoligion slate finished **in parallel**
> because it bakes at initiation. Sequence recorded in `canon.yml > planet.status_src`.

> ⤴ **archived 2026-08-23** — heading says so.

---

## ✅ ANSWERED 2026-08-22 11:00 — THE REPO CSV BUNDLE **IS** THE MAP, AND AUTHORING IS OPEN

**Owner, direct to DECIDE.** Asked which artifact he meant by *"an out of game map we are
working on together"*, he chose: **`world/ASHKARR_WORLDMAP_*.csv` in this repo is it.**

🔑 **"Remake it an entirely different way" meant the METHOD — direct hand-authoring judged by
looking — NOT a different planet.** Ash'karr as painted is the map in progress; it is edited
in place and it is not final.

⚠️ **DECIDE struck the `WORLDGEN_RUN.md` adoption banner earlier that morning on the opposite
reading. The strike was wrong and has been withdrawn.** Nobody acted on it.

⭐ **And `status: remaking` was never a verdict on the paint** — it is the owner's four-step
sequence, and it **stays** until step 4: map worked → port-survival proof through the bridge
→ factions/leader-names/ideoligions finalised in parallel → **save the game, and that
savegame IS the freeze.**

Three further DECIDE questions answered in the same breath: **all nine remaining NPC faiths
get a full `ideoDescription`** · **vanilla pawn kinds get retagged onto Star Wars guns**
rather than cut or left bare · **the plant cherrypick runs as a pre-filled review sheet.**

> ⤴ **archived 2026-08-23** — heading says so.

---

## ~~🔴 TWO OF YOUR OWN RULINGS FROM 2026-08-22 DISAGREE ABOUT THE PLANET~~ — ANSWERED ABOVE, DECIDE, 2026-08-22

**One sentence from you settles it, and until you say it the run sheet is ambiguous.**

| what you said | where it now lives | what it tells an agent to do |
|---|---|---|
| *"That world, upon examination, really isn't very bad at all… we're thinking of trying to adopt it."* | the top banner of `infrastructure/state/WORLDGEN_RUN.md` | **keep authoring Ash'karr** — continuity repairs, landmarks, named places, settlements, terrain detail |
| *"I am working with DECIDE to remake the planet an entirely different way, so there is no current frozen world."* (to REP) | `infrastructure/state/canon.yml` → `planet.status: remaking` | **stop** — the old paint is a record, not a target |

⚠️ **Both are dated 2026-08-22, hours apart.** I have written the second one over the first
in `WORLDGEN_RUN.md`, because it is later and because `canon.yml`'s own provenance claims it
*"supersedes … every doc saying the planet is frozen as-is for v1"*. **That is my reading of
your words, not your ruling.** If I have it backwards, an agent has been stopped from doing
work you wanted.

🔑 **What I need from you is one of these two lines, said to any window:**

- *"The map is adopted, keep authoring Ash'karr"* — I revert the banner and set
  `canon.yml` back to `frozen`.
- *"The planet is being remade, the old paint is history"* — the banner stands as written and
  `CANON_SUSPENDED_FOR_REMAKE_1` unblocks when the new shape is settled.

⚠️ **What is NOT in question either way:** there is no worldgen feature in any version, and
the world is still built by hand, once, and frozen. Only *which* world is at issue.

⛔ **Separately and still open:** nobody can say which savegame the world bakes into — both
candidates read `seedString grasshopper` and the docs say `lada`. That blocks `B55` and it is
below.

> ✅ **ANSWERED at :20 in this same file** — owner, 2026-08-22: *"I like the vanilla weapons being gone."* The floor is spelled out as NEOLITHIC in `required_mods.md:730`. It only reads open because it is a `##` heading inside :20's fold.

> ⤴ **archived 2026-08-23** — heading says so.

---

## ✅ ANSWERED 2026-08-22 14:11 — THE FLOOR IS BOWS AND KNIVES, FOR ANYONE

**You said:** *"strike the two docs. The cheap end should be bows and knives for anyone... but
it's ok if you make them cheaper so that nobody just spawns with fists, that's a bit silly."*

- ✅ **Both docs were ALREADY struck** on 2026-08-22, off your earlier *"I like the vanilla
  weapons being gone"* — the question above was written before that landed and is stale, not
  outstanding. I have added your wording to both anyway, because they said *"bows and clubs"*
  and you said **knives**.
- 🔑 **The half that is new, and it changes work:** a bare-handed pawn is a **pricing** defect.
  Fix it by making a floor weapon CHEAPER, never by raising a kind's `weaponMoney`. That
  reverses standing advice in three open items — `first_light.py` wanted to raise
  `Town_Trader` and `Hunter` budgets to 340 so they could afford an **incendiary launcher**.
- Filed as `WEAPON_FLOOR_BOWS_KNIVES_1` for DECIDE (offline): name which defs are the floor,
  what they cost, which tags reach them. The measured victim list already exists — 16 `Jawa_*`
  role kinds bare 5/5 live, plus every `TribalWarriorBase` kind, whose only tag
  `NeolithicMeleeDecent` resolves to the empty set.
- ⚠️ **Three of those cannot be fixed by price at all:** `Jawa_Droid_Leader`,
  `Jawa_Droid_Specialist`, `Jawa_TradeMoot_Specialist` have no `weaponTags` field, and Droid
  Grunt/Heavy carry `weaponMoney 0-0`. Those need a tag, not a discount.

<details><summary>the question as it was asked</summary>

> ⤴ **archived 2026-08-23** — heading says so.

---

## ⚖️ WHAT IS THE WEAPONS FLOOR? TWO DOCS SAY VANILLA, THE CUT SAYS BLASTERS — DECIDE, 2026-08-22

**Nothing is blocked on this.** I ruled `VANILLA_GUNS_CUT_OR_RETAG_1` without it and the
answer holds either way. But the tension is real, it is unstruck in two live documents, and
it is yours rather than mine.

**The cut, as it stands:** Cherry Picker strips eight vanilla industrial guns — revolver,
autopistol, bolt-action, pump shotgun, machine pistol, heavy SMG, assault rifle, sniper.
You reversed exactly one slice of it, the Mech weapons, and left the rest.

**Two live docs say the opposite, and neither is struck:**

| where | what it says | when |
|---|---|---|
| `design/RimMandrake/Custom_World.md:110` | *"recommend AGAINST"* amputating vanilla weapons — **"keep vanilla for the low end; let SW gear be mid/high flavor."** Its reasoning: amputation deletes the scrappy low-tech early arc a scavenger start wants, and soft-pushes everyone onto ultra-tech blasters, which is anti-scarcity | 2026-08-03 audit |
| `design/Jawa/mods/required_mods.md:730` | **"v1's floor is vanilla low-tech and Outer Rim's cheap end"** | 2026-08-15, the same day you cut VWE-Makeshift for being bullet guns |

🔑 **The honest reading is that "vanilla low-tech" is ambiguous** — it may mean bows and
clubs, which survive the cut, or it may mean revolvers, which do not. Both docs were written
before the cut list reached its current size.

**You do not need to answer now.** What I would not do is let a seat "discover" the tension
in six weeks and quietly resolve it by un-cutting eight guns to fix a rounding error, which
is exactly the shape of the item I just closed.

</details>

---

> ⛔ **SUPERSEDED hours later the same day** by `canon.yml planet.status: remaking` — *"there is no current frozen world."* This section was never told.

> ⤴ **archived 2026-08-23** — answered in the 14:11 section above — the floor is bows and knives.

---

## ✅ THE MAP IS ADOPTED AND AUTHORING IS OPEN — DECIDE, 2026-08-22

**You looked at the four globes and said the world "really isn't very bad at all… we're
thinking of trying to adopt it." That is now the ruling** (`WORLD_ADOPTED_AUTHORING_OPEN_1`),
and it **supersedes last night's freeze** wherever the two disagree.

- ✅ **Open again:** river and road continuity, landmarks, named places, settlements, terrain
  detail — everything that edits **the map that exists, directly and in place**.
- ⛔ **Still closed, and nothing below reopens them:** regenerating the bundle with
  `ashkarr_paint.py`; `refmatch.py`, which stays cancelled; and worldgen, in any version.
- **Unwound in 14 docs plus `canon.yml`.** The freeze banners are replaced, not deleted, so
  the reversal is visible where the freeze was.
- **Five items stay dropped, on purpose** — none is work you want back:
  `REFMATCH_THRESHOLDS_CALIBRATE_1` (harness still dead) · `SCALD_RELIEF_RENDER_LOOK_1` (you
  have looked — that is what the globes were) · `RIVERS_BEGIN_FROM_NOTHING_1` (its substance
  was delivered tonight by direct edit, not by re-running the painter) · `W9` and
  `LOAD2_TARGET_IS_SUB7B_1` (both are live-game paint runs, and they belong with
  `FINAL_WORLD_PREP_1` when you are ready to bake).

⚠️ **The one below is unchanged and still yours** — adopting the map does not identify the
save it gets baked into.

---

> ⛔ **MOOT under the remake** — but its seedString half survives as `B55`'s live blocker text, so do not delete it wholesale.

> ⤴ **archived 2026-08-23** — heading says so.

---

## 🔴 NOBODY CAN SAY WHICH PLANET YOU ADOPTED — DECIDE, 2026-08-21, still open

**You froze the world as-is. The problem is that "as-is" does not currently name a file.**

Both candidate saves read `seedString grasshopper`; the docs that describe the keeper say
`lada`. ⇒ **A freeze on an unidentified artifact is not a freeze** — and it is the one thing
that has to be right before the campaign start is built on top of it, because `B55` sits on
this world and cannot be rebuilt cheaply if the wrong one ships.

⚠️ **This is not asking you to look at the map again.** It is asking that the keeper be
IDENTIFIED and BACKED UP. It is measurement, not judgement, and it is already the surviving
half of `FINAL_WORLD_PREP_1` (rows 4–6); rows 1–3 died with the freeze. **Nothing here needs
a ruling from you unless the two saves turn out to disagree about the planet itself.**

🔑 **What is safe to say today:** the authored bundle is intact and complete offline —
`world/ASHKARR_WORLDMAP_tiles.csv` at 21,872 rows, `_links.csv` lints clean at 1,075
(`89029b7`). **The CSVs are the map.** What is unresolved is which generated SAVE the ship
gets bolted to.

---

> ⛔ **SUPERSEDED TWICE** — adopted, then remaking. It also says *"refmatch.py stays cancelled"*, reversed 2026-08-22 (`436bf693`): deferred to **v2**.

> ⤴ **archived 2026-08-23** — answered by 'THE MAP IS ADOPTED AND AUTHORING IS OPEN'.

---

## ✅ THE PLANET FREEZE IS PROPAGATED — DECIDE, 2026-08-21

Your ruling — *"just freeze the world for now as-is and move on to v1. I have to totally
rethink how we create that planet"* — is now written into every file that said otherwise,
rather than only into the item that recorded it.

- **Dropped, with the reason on each:** `W9` (the 7-stage paint), `LOAD2_TARGET_IS_SUB7B_1`,
  `RIVERS_BEGIN_FROM_NOTHING_1`, `SCALD_RELIEF_RENDER_LOOK_1`, and
  `REFMATCH_THRESHOLDS_CALIBRATE_1` — the last of which had been sitting **blocked on you
  over a question you had already answered**, because a rulings index in this very file said
  *"the look was the gate on `refmatch.py`; it is lifted"*. It never lifted. That line is
  struck now, at `HUMAN.md`'s six-rulings table.
  ⚠️ **One copy of that gate is left standing and only you can strike it.**
  `infrastructure/state/items/CANON_RULINGS_OWED_OWNER_1.md` — your own inbox item — still
  says **"`refmatch.py` cannot be built until you have looked"**, under the heading *"the one
  that is worth a look, not a ruling"*. It is your item, and the seat guard refuses DECIDE
  editing it, correctly. **It is wrong: you looked, and you ruled on the tool, not the gate.**
  Strike it when you next work that item — or say the word and I will.
- **Superseded:** `THE_SCALD_LOST_ITS_WATER_1` — its premise went false when the Scald was
  dropped to −30 m; water measures 8.14%, matching canon.
- **Kept, deliberately, because they are correctness and not authoring:**
  `RIVER_LINKS_EMITTED_BACKWARDS_1` (the producer still emits river links by tile id, not
  mouth-first — your own named example), `LINT_EXCLUDE_LAKE_SUBMERGED_1` (312 false findings
  on the sunk Scald), `RAIN_DRY_THE_JUNGLE_1` (your option (a) — it is climate content and
  renders nothing you can see, so it survives the freeze), and the `world_links_import`
  column-check fix, which is built and now rides the next DLL deploy.
- **Written down for later:** `design/V2_DREAMS.md > PLANET_METHOD_RETHINK_1` — the method
  being discarded, the intent it failed, and the four measured defects, so that when you come
  back with a new method there is something to judge it against. ⛔ It is **not** worldgen and
  says so twice.

⚠️ **One thing in that record you should see, because it may be the whole finding.** On
2026-08-18 you asked for direct authoring: *"You don't need to make Python that does this…
just do it directly."* What got built was `ashkarr_paint.py` — a recipe-and-rebuild pipeline.
The "messy and horrible" may be less about the pixels than about that substitution.

---

> ⤴ **archived 2026-08-23** — heading says so.

---

## ~~🔴 THE FROZEN DUMP HAS ALREADY BEEN REPLACED~~ RESOLVED — owner froze 08-21

`infrastructure/state/dumps/REGISTRY.jsonl` freezes **`OFFICIAL-2026-08-20`** at
`capturedUtc 2026-08-20T15:08:30Z`. The dump on disk is **`2026-08-21T08:20:20Z`**.

⚠️ **Both captures are 578 mods**, which is why nothing noticed: the mod count was
the only thing the frozen branch compared, and it had not moved. So the design
target DECIDE and BUILD author against changed underneath them with no announcement
— the exact failure `dumps/README.md` warns is *"far worse than a stale warning"*.

✅ **Now detected.** `refresh.py` reports **`REPLACED`** on the board, comparing the
registry's `capturedUtc` against the manifest's.

🔑 **Two things you should know before choosing:**
- The 08-21 capture is the one everything today was measured against, and it is the
  one that exposed the 824-def collision loss. It is *better evidence* than the
  08-20 one, not worse.
- ⛔ **An agent must not re-freeze to clear the warning.** That is how a target moves
  without anyone deciding, so this is parked here rather than fixed.

✅ **OWNER, 2026-08-21: "Freeze it now."** ⇒ option (a). `OFFICIAL-2026-08-21` is
appended to the registry, superseding `OFFICIAL-2026-08-20`, and the board reads
`FROZEN` again. The design target is now the 08-21 capture, deliberately.

⚠️ **What you froze, stated plainly so nobody is surprised by it later:** this
capture is missing **824 defs** to 8 filename collisions in the dumper — `AbilityDef`
among them, reading 0 where 612 were written. That is recorded in the entry's
`knownDamage` field, and `measure` returns `UNMEASURED` rather than `0` for every
affected type, so the holes cannot be mistaken for absence.

🔑 **A clean capture is available but costs a game-down window:** the dumper fix
(`d7cf154`) is built and sitting undeployed in the repo because the OS locks the
DLL while RimWorld runs. Deploy it on the next shutdown, dump once, and re-freeze —
at which point the target has no holes at all.

⚠️ **Also settled today, and it needs no decision from you** — the freeze covers the
CAPTURE only (`manifest.json`, `defs/**`, `animals.json`). `defs.sqlite` is derived,
deterministic and rebuilt in ~60 s, so it is explicitly OUTSIDE the freeze; freezing
it would freeze its schema bugs. Full ruling at the top of `dumps/README.md`.

---

✅ **DONE, 2026-08-21 evening — the holes are gone and nothing above is outstanding.**
The game-down window happened, `d7cf154` deployed, and the owner froze the clean
capture: **`OFFICIAL-2026-08-21T22-44-59Z`**, `capturedUtc 2026-08-21T22:44:59Z`,
superseding `OFFICIAL-2026-08-21`. `AbilityDef` reads 612, not 0. **No 824-def
`knownDamage` on this entry**, and the board does not read `REPLACED`.

🔑 **It is CURRENT, not merely present** — `modlist_sha 49b83562b10df31c` is the same
value `refresh.py --fingerprint` returns for the live load set (578 listed, 578
resolved, 0 missing), verified 2026-08-21 16:24 PDT. **Do not ask the owner to
re-freeze**; REP did on waking, from this section, and was wrong. Read
`infrastructure/state/dumps/REGISTRY.jsonl`, never a briefing, before saying a freeze
is stale.

⚠️ **Two label-only corrections sit on the registry and are NOT re-freezes.** The id
was renamed off the bare date (the default id derives from the DATE, so two captures
in one day collided and the entry claimed to supersede itself), and the 08:20 entry's
`modlist_sha` was replaced with one that actually reproduces on this machine. Captures,
`capturedUtc` and freeze authority are untouched in both.

> ⤴ **archived 2026-08-23** — heading says so.

---

## ~~Q (DECIDE, 2026-08-15): a cherrypick session~~ ANSWERED — FROZEN, and CLOSED for v1

🔴 **OWNER, 2026-08-15:** *"I have completed armor, weapons, items, beasts, and a few
other things. Let's freeze cherrypicking for right now and close out that item
completely for v1. We can return to it later as needed. No need to review mechs
either."*
⇒ **D27 closes. Chain step 1 is DONE for v1** — it is no longer the head of the chain
and no longer blocks steps 2 and 3. The remaining categories (plants, mechs, drugs,
incidents, traits, ideology styles) are **not v1 work** and nobody schedules them.
The "granularity" owner decision named in the briefing below is **moot**.
⚠️ B67 still stands on its own merits: ~1,300 keep-judgements are gitignored on one
disk, and `cherrypick_build.py` has never validated one of the 1,308 live keys. Freezing
the picking does not make the decisions safe.

<details><summary>the original question</summary>
Chain step 1 is the head of the chain: it blocks step 2 (normalize), which blocks step 3
(equip the pawns), which is why `B53`'s 48 pawn kinds are `blocked`. It is the only step
that needs the OWNER rather than a seat, and it needs him **not playing** — which is now.

**Five categories are already decided and live** (1,308 Cherry Picker keys): weapons
183 cut of 799 · apparel 132 of 820 · animals 338 of 1,239 · items · buildings.
**Seven remain**: armour · plants · mechs · drugs · incidents · traits · ideology styles.

⚠️ **`design/Jawa/mods/CHERRYPICK_AGENDA.md` is stale and will waste his time.** It still
reads *"No list exists at all today"* for armour and leaves weapons and apparel unticked,
though both were decided at 07:19 today and are deployed. Correcting it is inside D27.

Two things a session needs first, both offline and both filed as BUILD **B67**:
the decision files are **gitignored** so ~1,300 keep-judgements sit on one disk, and
`cherrypick_build.py` has never validated a single one of the 1,308 live keys.

✅ **ANSWERED — OWNER 2026-08-15: cherrypicking is FROZEN and the item is CLOSED for
v1.** *"Armour, weapons, items, beasts and others are done; the rest returns later if
needed."* No category runs now; the seven un-run ones are not debt. D27 closed.
🔑 The consequence is the useful part: **the surviving item set is FIXED**, which
un-blocks chain steps 2 and 3 and removes `B53`'s stated blocker. item: D27
</details>

> ⤴ **archived 2026-08-23** — heading says so.

---

## ~~Q (CHECK, 2026-08-14): four companion-DLL tools the thruster move proved we need~~ ANSWERED — ALL FOUR TO v2

✅ **OWNER, 2026-08-15: push all four to v2.** `inspect_string`, `gravship_status`,
`set_thing_rotation`, `can_place`. **Deferred, not refused** — the gaps are real and
measured, but nothing in v1 waits on them now that C43 has left v1. No DLL build, no
shutdown window held for them. The ranked case below stands as the v2 brief.
Owner's standing instruction, given this session: **always raise DLL capabilities as an
option and let the owner judge.** These four are not speculative — each one is a gap that
cost real calls or left a claim unverifiable while relocating the thruster bank.

Ranked. 1 is the one that actually blocks CHECK from closing items.

1. **`jawa/inspect_string`** — `Thing.GetInspectString()` for any `thingId`. Already asked
   for by C13. **CHECK currently cannot answer "is this thruster functional" at all.**
   `get_cell_info` returns `className: "Verse.Building"` and stops; `list_alerts` carries
   nothing about it; the red-slash overlay was proved non-discriminating today (see
   `facts/LIVE.md`). Everything about thruster function is presently geometry + inference.
2. **`jawa/gravship_status`** — the engine's own launch validation in one call: thruster
   count, computed `GravshipRange`, fuel, and the blocking reason strings
   (`CannotLaunchNoThrusters`, `ThrusterBlockedBy`, …). This is the tool that would turn
   "the geometry mirrors a known-good thruster" into "the ship reports it can fly."
   Note `LIVE.md`: buildings from `spawn_batch` arrive **factionless** and the engine
   offers no Launch gizmo on a pawnless map, so this may need a claimed engine to answer.
3. **`jawa/set_thing_rotation`** — rotate a spawned building in place. Today the only way
   to change a thruster's facing is destroy + respawn, which discards hitpoints, stuff and
   quality. Harmless on a scratch map; **destructive on a colony that matters.**
4. **`jawa/can_place`** — `GenConstruct.CanPlaceBlueprintAt` with an **explicit rotation**,
   returning the `AcceptanceReport` text. Measured today: the stock
   `apply_architect_designator` `dryRun` returned `ok=true` for 25/25 cells under god
   mode, **including a cell already occupied by a thruster**. It is not a validator.

All four need the game DOWN to deploy, so they batch into one shutdown window with any
other BUILD companion work. item: (raised from the thruster relocation, no queue ID)

> ⤴ **archived 2026-08-23** — heading says so.

---

## Q (BUILD, 2026-08-14): B6 was deleted from `queue/BUILD.md` by `f249d67`
`f249d67` ("Every queue item carries a row:") added a `row:` field to every item and
removed `## B6 Deploy the MandrakeJawa xenotype + Jawa_IndigenousTribes set` outright.
It is the only item that commit dropped, and the subject does not claim a deletion, so
this reads as an accident rather than a ruling.

No work was lost: B6 is DONE — the four PawnKindDefs were repaired (`c06e89e`) and
`Jawa_Patches` is deployed `-> VERIFIED in sync`. The live half is carried forward as
`queue/CHECK.md` C31. Flagging it because if the deletion WAS deliberate, C31 should be
withdrawn; and because a mechanical field-adding pass that silently drops an item is
worth knowing about before the next one runs.

> ⤴ **archived 2026-08-23** — answered two sections later — the deletion was DELIBERATE.

---

## Q (DECIDE, 2026-08-14): where v2 ideas go — A(owner): `design/V2_DREAMS.md`
Owner's standing instruction: any idea for new content that is deferred out of v1 goes
to `design/V2_DREAMS.md`, appended at the end. **Every seat, and the owner through any
seat, may append there directly** — no permission, no routing through DECIDE, no queue
item asking for it, no format and no field contract.

For REP specifically: when the owner throws out an idea that is not v1, append it and
say where it went. It is not a queue, nothing in it is scheduled, and the board derives
no state from it — so it needs no `derive_matrix.py` run. The point is offloading: write
it down, let it go, back to v1. item: (standing instruction, no queue ID)

> ⤴ **archived 2026-08-23** — the owner's answer is in the heading — design/V2_DREAMS.md.

---

## A (DECIDE, 2026-08-14) to BUILD's B6 question: the deletion was DELIBERATE
Not an accident. `f249d67`'s job was assigning `row:`, and its instruction (D0) said
items touching closed rows are almost certainly stale and should be deleted rather than
assigned. B6 claimed the MandrakeJawa set was "built and committed, NOT DEPLOYED"; the
deployed `Jawa_Patches` folder holds `MandrakeJawaXenotype.xml`, `OnlyMandrakeJawa.xml`
and `JawaXenotype_Repoint.xml`, so the claim was false and the item was stale.
⇒ **C31 STANDS** — the live half was never in doubt. The fair criticism is that the
commit subject did not name the deletion, and that is taken.

> ⤴ **archived 2026-08-23** — this IS the answer to the B6 question.

---

## FYI (DECIDE, 2026-08-14): the board now tracks the CHAIN, not the eight rows
Read `infrastructure/state/V1_CHAIN.md` before acting on anything below.

**Owner expanded v1.** It is now the 8 gate rows **plus the FULL faction roster** plus
one playable session. This supersedes `V1_SCOPE.md`, which deferred the 11 dossiers,
`pawnGroupMakers` and the ideoligions to v2. The cost was stated to the owner and taken.

**`V1.md`'s table is now 14 chain steps, and queue `row:` values key to it.** The eight
gate rows are still recorded there but carry no items — they are a scoreboard, not a
work breakdown. 15 items filed under the old numbering were remapped; the worldgen
cluster had been rendering under "Pawntypes".

**50 items, and step 9 is burnable today.** 13 BUILD items decompose
`design/Jawa/worldbuilding/FACTION_SPEC.md`: 3 reskin patches, 7 authored `FactionDef`s,
2 label patches, 1 fix to `Jawa_IndigenousTribes`. Every `pawnGroupMaker` kind named in
them was verified present in the 2026-08-14 def dump.

**The head of the chain has NO items yet** — steps 1-3 (item cherrypick -> normalize
weapons/armour/beasts -> equip the pawns). One open owner decision (granularity) blocks
them, and `B39` produces its input. `B53` (the 48 pawn kinds) is correctly `blocked` on
step 3.

**Rulings that change other seats' work:**
- Row 4 CLOSED (scrapfields ships at any density); row 3 REOPENED (resolution, not
  registration); **row 1 REOPENED** — it closed on a label seen live on
  `OuterRim_GalacticEmpire`, and the vessel is now vanilla `Empire` (B40).
- Starting goodwill is NOT a `FactionDef` field. All 12 dossier numbers are cut from v1,
  and inter-faction hostility is fiction only. Do not build a mechanism for either.
- Donor pawn kinds are FLAT species kinds at `combatPower 40`. Role differentiation does
  not exist to borrow, so the 48 authored kinds are required.
- The mod freeze is TWO files — `ModsConfig.xml` AND Cherry Picker's removal list, both
  at `deployed/config/v1_freeze/`. Two of the owner's gene picks had gone missing and are
  restored; they apply on the next cold load.

item: (status briefing, no queue ID)

---

> ⤴ **archived 2026-08-23** — an FYI from 2026-08-14, not a question, and the board has been rebuilt twice since.

---

## ~~Is RimSort open right now?~~ ANSWERED — the question was never valid

🔴 **Owner's ruling, 2026-08-15: never ask this again.** *"You NEVER have to ask if
RimSort is open. It does not autosave, and I will never save without asking. Nobody
blocks on RimSort or game close for config files of any kind."* Written into
`POLICY.md`, `CLAUDE.md`, `NEXT_RELOAD.md` §1b and the three skills that said
otherwise. BUILD unblocked; B25 proceeds.

~~**BUILD is blocked on this and nothing else.**~~ `B25(a)` (pin the loadBottom/loadAfter
user rules) and `B25(d)` (enable `vanillaexpanded.vwel`) both WRITE
`ModsConfig.xml`. RimSort holds the mod list in memory and writes it on Save, so a
write into an open RimSort is silently lost on your next Save — and you are the only
reader who knows whether it is open.

- **RimSort is CLOSED** -> BUILD does the whole B25 pass in one go.
- **RimSort is OPEN** -> close it (or Save then close), then say so.

Live `ModsConfig.xml` mtime is 2026-08-15 11:58:30, 575 active. B25(b) `refresh.py`
does not touch the mod list and has been released to BUILD already.

item: B25(a), B25(d)

---

> ⤴ **archived 2026-08-23** — heading says so.

---

## ✅ ANSWERED + DONE (owner, 2026-08-15): the shipping Jawa xenotype drops four of our own genes

**OWNER'S RULING: fix it, #1 priority.** Done by BUILD the same hour, and it turned
out to need no risky edit at all.

🔴 **The question's framing was wrong, and the wrong half was being guarded.** It
asked whether to migrate a shipping save artifact — the dangerous-sounding option.
In fact **the repo copy was already correct** and had been since `c57f347`, the
commit that did the rename. **Only the GAME copy was stale**, at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Xenotypes\MandrakeJawa.xtp`,
mtime 2026-08-14 15:52. So this was never "migrate an artifact"; it was **a file
that was never deployed** — the project's oldest failure mode, in a folder nobody
thinks of as a deploy target because it is not `Mods/`.

**What was done:** game copy backed up to `MandrakeJawa.xtp.bak-2026-08-15`, repo
copy written over it, md5 verified equal (`d5795edf…`).
**Evidence, against the dump refreshed at THIS load (62,515 defNames):** all four
new names — `RimMandrake_Jawa_Eyes_HugeAmber`, `RimMandrake_Jawa_Eyes_HugeOrange`,
`RimMandrake_Jawa_Head_Plain`, `RimMandrake_Jawa_Skittish` — are LIVE; all four old
names are ABSENT. `validate_save_artifact.py`: **36/36 references resolve, zero
dangling.** Option 1 shipped, with the `Gene_` case correct.

🔴 **STATUS IS "FIX DEPLOYED, UNVERIFIED" — not done. CHECK is right to hold it open
and the reason is not pedantry.** Everything above is **DISK** evidence, and disk
evidence is exactly what got this wrong the first time: `LIVE.md`'s retracted claim
*"MandrakeJawa.xtp is CLEAN: 36/36 references resolve"* came from **this same
validator**, and the running engine contradicted it. The game running now loaded the
OLD file at startup, so **this session cannot witness the fix in either direction.**
**CLOSING CONDITION, and it costs nothing:** the next load's startup log carries
**ZERO** `Could not load reference to Verse.GeneDef named Jawa_*`. Today's carried 12
GeneDef lines, 4 of them ours. CHECK reads it with `harvest_log.py --show scribe` and
closes it then (`0279750`).
📌 The general rule, worth more than this item: **an offline validator answers "is
the file I pointed at self-consistent". It cannot answer "is the file the game reads
correct" — and for a `.xtp` those were two different files for a whole day.**

~~⚠️ **STILL OPEN, and it is not ours to fix unasked:** `softshadow.xtp` in the same
folder carries two dead names — `Jawa_Gene_Skittish` and `Jawa_Head_Plain` — and
will silently drop those genes at world creation exactly as MandrakeJawa would
have. It is not in our repo. The fix is the same two renames and takes a minute;
say the word. (`pokean.xtp` is clean — checked.)~~
✅ **RESOLVED — OWNER 2026-08-15: *"Kill softshadow, it was a mistake."*** File
DELETED from the Xenotypes folder by REP. No fix needed, no item, no decision left.
Confirmed before deleting: 22 genes, two of them the dead names. Surviving `.xtp`
files: `MandrakeJawa` (clean, verified), `pokean` (clean), `Dark Glutton`,
`Dark Troll`, `mimic`.

<details><summary>the question as originally filed</summary>

> ⤴ **archived 2026-08-23** — heading says so.

---

## 🔴 Q (CHECK via REP, 2026-08-15): the shipping Jawa xenotype drops four of our own genes — migrate it, or ship as-is?

**This one blocks worldgen, and it was found by the running game after an offline
verdict said the opposite.**

`MandrakeJawa.xtp` — the v1 xenotype you approved — silently drops **4 GeneDefs**
every load. All four were renamed on our side and the saved file never followed:

| in the .xtp | live name today |
|---|---|
| `Jawa_Eyes_HugeAmber` | `RimMandrake_Jawa_Eyes_HugeAmber` |
| `Jawa_Eyes_HugeOrange` | `RimMandrake_Jawa_Eyes_HugeOrange` |
| `Jawa_Head_Plain` | `RimMandrake_Jawa_Head_Plain` |
| `Jawa_Gene_Skittish` | `RimMandrake_Jawa_Skittish` — ⚠️ **also lost `Gene_`** |

🔴 **A blind "prefix everything" migration fixes three and breaks the fourth.**

Nothing is missing from the game — all four new names are live in today's dump. The
failure is that **the `.xtp` bakes at world creation** and the drop is **silent in
play**: a Jawa comes out without its head type and eye colours and nothing says so.

**The question is yours because migrating a shipping save artifact is not a seat's
call.** Options, recommendation first:

1. ⭐ **Migrate the four names in `MandrakeJawa.xtp` before you generate.** Cheap,
   reversible, and it is the only option that ships the xenotype you actually
   approved. Needs the `Gene_` case handled by hand, not by sed.
2. Regenerate the xenotype from scratch in-game and re-save it. Safer against other
   drift we have not found, costs you a sitting.
3. Ship as-is and accept Jawas without their head type and eye colours.

**Also affected, not yet judged:** `softshadow.xtp` and `pokean.xtp` carry some of
the same dead names.

⚠️ **Doctrine correction already made by CHECK:** `LIVE.md` carried *"MandrakeJawa.xtp
is CLEAN: 36/36 references resolve"* — an **offline** verdict the running game
contradicts. An offline validator **cannot** catch this class: Scribe resolves saved
names at load; a dump check answers a different question. C42's "dangling-reference
question is CLOSED offline" is **falsified for the `.xtp` half**.

Filed to DECIDE as `the-shipping-xenotype-drops-four-of-our-own-genes-7e31aa`.
CHECK did not touch the artifact.

</details>

---

> ⤴ **archived 2026-08-23** — answered + done, owner 2026-08-15, section above.

---

## ~~🔴 Q (CHECK via REP, 2026-08-15): your lightsaber test cannot be run without you — how do you want it collected?~~ ANSWERED — MOVED TO v2, C43 CLOSED

✅ **OWNER, 2026-08-15:** *"Move the lightsabre position bug to v2."*
⇒ **C43 is CLOSED and out of v1.** Do not collect it, do not spend a load on it, do
not stage a swing for v1. Parked in `design/V2_DREAMS.md` as "Lightsabre position
during melee — v2" with everything learned attached, so v2 does not repeat the
attempt blind. The three options below are moot; kept as the record of why it could
not be collected. Yayo stays OFF and re-enabling it is still ruled out.

🔴 **Nothing is missing from the build.** 14 lightsaber ThingDefs are live, verified
against this load's own dump, and one equipped and rendered correctly in game today.
The only open question was ever how the weapon SITS mid-swing. **Nobody goes hunting
a missing weapon.**

---


**C43 is blocked, and the blocker is the bridge, not the art.** The equip half is
solved and verified off the pawn's own Gear panel (*"Equipped: Lightsaber (normal)"*).
**The attack half cannot be staged: nothing on the 155-tool bridge orders an attack.**

- Drafted pawns hold at `Wait_Combat`.
- `jawa/order_pawn` issues a GOTO even when given a `targetId`.
- Spawned hostiles have no lord and idle.
- "Spawn large enemy raid" + 5,600 stepped ticks never produced an engagement.
- The four sith pawnkinds spawn **unarmed**.

CHECK declined to photograph a pawn standing still and call it active melee. That is
the right call — the test you wrote says *during active melee combat*.

**Options, recommendation first:**

1. ⭐ **Stage it yourself in two minutes at the keyboard** — draft, order the attack,
   F10 at the swing. You are the verdict on this one anyway ("more reasonable" is a
   judgement no seat will award itself), so doing the capture costs you almost
   nothing extra.
2. **Add a bridge tool that orders a melee attack** — filed to BUILD as
   `bridge-cannot-order-a-melee-attack-3f8c21`. Fixes it permanently and unblocks
   every future combat test, but needs a DLL build and the next load.
3. Drop C43 from v1.

⚠️ **Whichever you pick, this load can only ever produce the Yayo-OFF arm.**

✅ **ANSWERED — OWNER, 2026-08-15: *"There absolutely is a lightsaber remaining in
the game."*** ⇒ **Every "the lightsaber is missing" thread is CLOSED. Do not open
another.**

⚠️ **Scope of that ruling, corrected 2026-08-15 so the record is accurate.** CHECK's
thread never claimed a lightsaber was missing from the build — it equipped
`Force_Lightsaber_Custom` on this map and verified it off the pawn's own Gear panel
("Equipped: Lightsaber (normal)", Customize/Throw gizmos on the command bar). Its
screenshot question was only ever whether a **Yayo-ON comparison arm** exists for
the owner's *"more reasonable THAN WHAT"*.
📌 **The inference worth keeping is general, not a criticism of that thread:** *"I
checked the two most recent — neither shows a lightsaber"* is a statement about
**two screenshots**, not about the game. Absence from a frame is not absence from
the build.
**Confirmed against this load's own def dump: 14 lightsaber `ThingDef`s are LIVE** —
`Force_Lightsaber_Custom`, `_Dual`, `_Curved`, `_Crossguard`, `_Shoto`,
`_Inquisitor`, `_BuildYourOwn`, `_UniqueObi`, `_UniqueAnakin`,
`Force_Ezra_BlasterLightsaber`, plus the throw/whip/projectile defs. `lee.theforce.lightsaber`
is active. **Nothing about lightsabers is missing from the game.**

⚖️ **What is still genuinely open is NARROWER, and it is not the weapon:** C43 needs
a pawn photographed *mid-swing*, and nothing on the bridge can order an attack. The
three options above stand. **A Yayo-ON comparison shot would still be useful if one
exists — but its absence is now a gap in our screenshots, not evidence about the
build, and no seat should go looking for a missing lightsaber again.**

<details><summary>the screenshot thread as originally filed — superseded</summary>

Still unanswered from earlier: **did your lightsaber complaint come from a screenshot?** If
one of the eight unexamined shots from 04:16–10:08 today shows a Yayo-ON mid-swing,
that is the comparison arm and C43 closes as a real A/B. I checked the two most
recent — neither shows a lightsaber.

</details>

> ⤴ **archived 2026-08-23** — heading says so.

---

## ~~🔴 FYI + one decision (BUILD, 2026-08-19): the cherrypick list was not loading AT ALL~~ ANSWERED

**No answer needed on the first part — it is already repaired.** Validating the 1,308
live Cherry Picker keys against the def dump for the first time (B67b) turned up two
keys the review sheet had synthesised for defs whose author forgot to give them a
defName:

```
<li>ThingDef/<nodef#10></li>
<li>ThingDef/<nodef#11></li>
```

A raw `<` is not legal inside XML text. The game's own log says what that cost:

```
Caught exception while loading mod settings data for 3521312241. Generating fresh
settings. The exception was: System.Xml.XmlException: The '#' character, hexadecimal
value 0x23, cannot be included in a name. Line 874, position 23.
```

⇒ **every one of the 1,308 cuts has been inert in game** — not two of them, all of
them. **Repaired**: the two impossible keys are dropped, 1,306 remain, the file parses,
and both the live config and the tracked freeze copy now hold it. The old file is at
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml.bak-nodef`.
`cherrypick_build.py` now refuses to write a file that is not well-formed.

### 🟢 ANSWERED 2026-08-19, both applied — the list is now 1,349 keys

* **the 11 weapons/apparel: "All 11 + the 4 turret buildings".** The four
  `FT_Gun_Turret*`/`FT_Gun_Recoilless` guns go in WITH `FT_TurretHexMortar`,
  `FT_TurretEmpero`, `FT_RecoillessGun` and `FT_TurretQuadAA`, so no turret is left
  holding a weapon that does not exist. Each pairing read out of the dump's
  `building.turretGunDef`, not guessed from the name.
* **the 30 biomes: "Apply 28, keep AridShrubland + Lake".** Recorded in
  `OWNER_EXCLUDE` in `cherrypick_build.py` with the tile counts, and printed on every
  run — a silent exception is how a decision gets lost twice.

⇒ 1,306 + 28 biomes + 11 weapons/apparel + 4 turret buildings = **1,349**, zero
removals, file parses. Nothing below is outstanding; it is kept for the reasoning.

<details><summary>the original finding</summary>

**What WAS yours to decide — 41 cuts you recorded that never reached the settings file.**
They are in `observed/inventory/decisions_*.json` and nowhere else, so nothing cut them
and nothing will. Not added: changing what is cut is not a seat's call.

| category | count | examples |
|---|---|---|
| biomes | 30 | `AB_IdyllicMeadows`, `AridShrubland`, `BorealForest`, `ColdBog` |
| weapons | 10 | `ElephantTusk`, `Flamebow`, `FT_Gun_TurretQuadAA`, `Gun_Incinerator` |
| apparel | 1 | `AM_LassoDevilstrand` |

⚠️ The 30 biomes may well be deliberate — biomes are excluded from a planet by the
hand-authored world map, not by Cherry Picker, so cutting the def too would be belt and
braces. Say the word and they go in; say nothing and they stay out.

**Also worth knowing, no action:** 129 of the 1,306 keys name defs from mods that are no
longer active (Vanilla Animals Expanded 66, Grimstone: Beasts 11, Giant Snake 6, ReGrowth:
Boiling 3, Skunks 1, plus 40 derived meat/egg keys). They are inert and harmless — Cherry
Picker skips an unresolvable key with no report — so they were left alone rather than
edited out of your list. `python3 src/RimMandrake/Utils/cherrypick_build.py` names every
one of them.

</details>

> ⤴ **archived 2026-08-23** — heading says so.

---

## ~~The `rimworld-modding` skill archive is stale and will not rebuild~~ CLOSED — and its alarming half was never true

✅ **REP, 2026-08-21: both stale archives rebuilt.** `rimworld-modding.skill` and
`rimbridge.skill` are byte-current with their folders; a census of all 26 archives found
those two and no others, and all 26 pass `package_skill.py --check`.

🔑 **But the sentence that made this urgent was wrong, and the correction matters more
than the rebuild.** *"Every script fix since 2026-08-16 is NOT in the installed skill"* —
no. **`.claude/skills/rimworld-modding` is a SYMLINK to `skills/rimworld-modding`.** Every
skill in this repo is installed that way. ⇒ **Editing the folder IS installing it**, and
the `validate_patch.py` fix was live the moment it was written. Nothing was ever running
stale guidance.

⚠️ **What a `.skill` archive is for:** handing the skill to a machine that does not have
this repo checked out. Nothing here loads from it. A stale archive is a stale export, not
a stale install — worth fixing, never urgent.

The 505-line failure had also already been fixed by someone: `SKILL.md` is 445 lines and
the check passed on the first run. The only real residue was one changed reference file.

> ✅ **ANSWERED** — `MAGENTA_CONTACT_SHEET_1`, owner 2026-08-21 and reconfirmed 2026-08-22: the contact sheet comes first, nobody touches a texPath until he has looked.

> ⤴ **archived 2026-08-23** — heading says so.

---

## ~~🔴 Q (REP, 2026-08-20): is the MOD leaving, or just the vessel?~~ ✅ ANSWERED — B, the mod STAYS

🟢 **OWNER, 2026-08-20: *"The mod is not leaving, no."*** ⇒ Option B. The patches are
not deleted, the saved worlds keep valid faction references, and Outer Rim keeps shipping
its pawn kinds and gear. `queue/BUILD.md` B-EMP1 is unblocked and rescoped — the only
real defect turned out to be stale prose in `About.xml`; the reskin patch already targets
vanilla `Empire`, and the `OnlyOurFactions.xml` suppression block is correct as written.

Your ruling is recorded and propagating: the Galactic Empire is authored on vanilla
`Empire`, and `OuterRim_GalacticEmpire` is not patched. That part needs nothing from you.

**But one word decides a different job.** Measured today: the Outer Rim Galactic Empire
mod is **still active in the campaign list** — 10 `neronix17.*` entries in
`infrastructure/state/modlists/ModsConfig.PRESWAP.20260819_212256.xml`, the 578-mod
snapshot. (The live `ModsConfig.xml` currently holds the 13-mod minimal list, so it is
not evidence either way.)

| if you meant | then |
|---|---|
| **A. The mod is being REMOVED from the list** | The six xpaths in `OnlyOurFactions.xml` and the `About.xml` dependency get **deleted**, not retargeted. ⚠️ And three saved world files — `world\WORLDMAP_gen.rws`, `WORLDMAP_source.rws`, `WORLDMAP_sub7b_source.rws` — already name `OuterRim_GalacticEmpire` in their faction lists. Removing the mod makes those **dead references in the save**, which no mod change fixes. |
| **B. The mod stays; it is simply not our vessel** | The patches get **retargeted or dropped**, the mod keeps shipping its own pawn kinds and gear, and the saved worlds are fine. Nothing else moves. |

**Recommendation: B**, unless you specifically want the mod gone. The vessel ruling gets
you everything you asked for, and A additionally costs a mod-list change plus a save
repair pass on the frozen world.

`queue/BUILD.md` B-EMP1 is **held** on this answer. `queue/DECIDE.md` D-EMP1 (the fresh
gap audit) is **not** blocked and can start now.

> ✅ **ANSWERED 2026-08-21** (`21e26d8`), and narrower than asked. `CAST_RACE_AND_KIT_FIELDS_1` and `DEEPWATER_CAST_ROSTER_1` are both done; the review sheet this asks for is explicitly NOT needed.

> ⤴ **archived 2026-08-23** — heading says so.

---

## ✅ REP, 2026-08-20 — BUILD's bake-in defect #2 is FIXED AT SOURCE. Its #1 is not, and is worse.

**Two seats found the same thing within the hour, from opposite directions, and agreed.**
BUILD found it over the bridge (four settlements missing from the live world); I found it
off the fresh 578-mod dump after you asked why Blackstar never generates. Same cause.

### What was wrong, in one line

`AM_EnemyPirate` — the def the whole Blackstar roster pointed at — is `hidden=True` with
`settlementGenerationWeight=0`, from the third-party *Ancient urban ruins* mod. **It is
built never to appear on the Configure Factions screen and never to place a settlement.**
The def you actually reskinned as Blackstar is vanilla **`Pirate`**: label already reads
`Blackstar Company`, weight 0.6, settlement art present. Nothing was wrong with the
faction — **the roster named the wrong def.**

### BUILD offered you a choice; I took the better half and it needs no decision

> *"Either Blackstar needs a vessel that exists, or those four rows come out of the CSV."*

**A vessel that exists — `Pirate`.** Deleting the rows would have removed a fully specced
faction from your planet to work around a one-token error. Repointed in all four source
files; zero `AM_EnemyPirate` left in any of them, 72 CSV rows preserved, both python tools
still compile. Verified offline *before* editing that the world already contains
`<def>Pirate</def>`, so the import resolves rather than refusing the whole file.

🔑 **It also kills the TPS crash for free.** `BLACKSTAR_HAS_NO_SETTLEMENT_ART_1` was going
to patch a `settlementTexturePath` onto `AM_EnemyPirate` to stop an every-frame
`ArgumentNullException` that took TPS to **3.7**. `Pirate` already has that texture, so
the crash cannot recur and **no patch ships**. That item is annotated superseded in place.

### What is left, and it is not mine

1. **The live planet still has 68 settlements, not 72.** The source is fixed; the world
   changes only when `world_settlements_import` is re-run. **That is bridge work and CHECK
   holds the bridge.**
2. ⚠️ **One thing I could NOT verify without the bridge:** BUILD reports the live world
   carries 16 factions and `AM_EnemyPirate` is not among them. I confirmed `Pirate` is in
   the saved world on disk — **not that it is in the 16 CHECK has up.** If it is not, the
   re-import will still skip those four. One `jawa/list_factions` settles it.

### 🔴 BUILD's defect #1 is the one that should worry you, and I cannot touch it

Ten of your eleven factions are wearing names the dice picked — *the Junkers* is called
**Marina's Asteroids**, *Hutt Cartel* is **Southeast Thiourhium**. The Empire is correct
only because it is the only def with a `fixedName`. **Adding `fixedName` now does not fix
this world** — `Faction.Name` returns the stored string, and the generated names are
already baked onto the objects in the save. It needs a live rename (nothing on the bridge
does it) *plus* the def fix so it cannot recur. **This is the build-once-and-freeze class,
and it is exactly the kind of thing that becomes permanent the day you keep a world.**

> ✅ **DONE** — Pillow 12.3.0 is installed.

> ⤴ **archived 2026-08-23** — heading says so.

---

## ✅ The desert trooper is built, and I should not have asked — BUILD, 2026-08-20

You were right to push back. I found that Outer Rim's own **snow** trooper wears the
**forest** set, wrote that down, and then went on treating "no desert apparel" as a
blocker anyway. Those cannot both be true. And I had already argued for the Homestead
Defense League myself before bouncing it back to you.

**Built:** `Jawa_Homestead_DesertRanger` — *"dune ranger"* — in
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`, alongside the militia,
the well-guard, the water warden and High Marshal Taren Voss. combatPower 62, between the
militia (49) and the well-guard (69).

⚠️ **Dressed explicitly, unlike its four siblings, and that is the point of it.** They
leave apparel to `apparelMoney` and take the roll; this one names `Apparel_Duster` +
`Apparel_Headwrap` because *looking* like the desert is the whole brief. Both are vanilla
Core, so no mod removal can strip them.

### 🔴 But it does not spawn yet — and neither do its four siblings

`pawnGroupMakers` for this faction lives on the **abstract parent `OutlanderFactionBase`**,
not on `OutlanderCivil`. So an xpath at `FactionDef[defName="OutlanderCivil"]/pawnGroupMakers`
**matches nothing — and a patch that matches nothing logs nothing.** Wiring it means
patching the abstract base, which reaches every Outlander faction, not just the League.

⚠️ **This is not a new problem and it is not the trooper's problem.** `Jawa_Homestead_Grunt`,
`_Heavy`, `_Specialist` and `_Leader` are already authored, valid, and referenced by
nothing — `HomesteadDefenseLeague.xml:36` records the ⛔ that put them there
(*"pawnGroupMakers, factionNameMaker and the raid curves are untouched"*), and it is filed
as `sixteen-roster-kinds-have-nowhere-to-be-used-8f21c4` with three options and a
recommendation already on it.

⇒ **One decision unblocks five kinds, not one.** I have not reversed the ⛔ myself because
it is a documented scope rule with a filed ruling waiting, and reversing it changes how
raids compose for a faction holding 13 of 72 settlements. Say the word and it is a small,
additive patch — one `<li>` at a low weight, leaving vanilla's options and weights alone.

---

> ⤴ **archived 2026-08-23** — heading says so.

---

## ✅ SIX OWNER RULINGS — 2026-08-21 00:45, routed by REP

All six are recorded as items so they execute; this block is the index, not the record.

| ruling | where it went |
|---|---|
| ⭐ **"I like your new globes. Well done."** | ⛔ ~~`REFMATCH_THRESHOLDS_CALIBRATE_1` → BUILD. The look was the gate on `refmatch.py`; it is lifted.~~ 🔴 **WRONG, AND CORRECTED 2026-08-21 — THE GATE NEVER LIFTED.** A compliment on a render is not a reversal of `canon.yml > ORTHO_GLOBE_MAP_ACCEPTED_1`, which had already ruled `refmatch.py` **MOOT for v1** on 2026-08-20. This cell is what sent `REFMATCH_THRESHOLDS_CALIBRATE_1` to BUILD, where it sat blocked on the owner over a question he had answered; DECIDE dropped it 2026-08-21 under `WORLD_FROZEN_RETHINK_PLANET_1`, and the planet is now frozen as-is besides. `refmatch.py` does not exist and is not to be written for v1 |
| **Rename the factions on the FRESH world** | folded into the fresh-world run, below. Both halves still needed: rename the live ten, AND add `fixedName` to the ten defs so it cannot recur |
| **"Approved abstract patch."** | `OUTLANDER_GROUPMAKER_PATCH_1` → BUILD. Reverses the ⛔ at `HomesteadDefenseLeague.xml:36`. Unblocks five kinds, not one |
| **"I want to see the magenta with my own eyes before we fix it, I don't trust it."** | `MAGENTA_CONTACT_SHEET_1` → CHECK. 🔴 Produces a PICTURE, not a fix. `d-chk2-magenta…` does not start until you have looked |
| **Race for all 269; kit and skills only where the prose earns it** | `CAST_RACE_AND_KIT_FIELDS_1` → DECIDE. ⛔ xenotype and pawnKind stay OPEN — not inferred from the race string |
| **"Select 40-57 habitable ring."** | `HABITABLE_RING_IS_40_57_1` → DECIDE, and **ruled at source in `canon.yml` already**. `needs_ruling` now holds one question, not two |

🔑 **The ring ruling reversed the provisional value, so read it carefully.** Canon held
**34–57** and listed 40–57 as superseded; those are now swapped. The arc-34–40 band,
~700 tiles, is **margin, not habitable**. ✅ **The Setdown does not move** — arc 56.9 is
inside 57 either way. `check_canon.py`: 121 files, 0 contradictions.

### 🔴 STILL THE ONE THING THAT BLOCKS EVERYTHING: no save loads

Unchanged and unanswered. Every save aborts in `FactionControl`'s cross-reference postfix
while the bridge keeps answering — which is why work against it looks fine and is not.
**Generate a fresh world on the 578 stack and save it**; that is also where the faction
renames land, and where your Configure Factions hand-tick pass belongs. `LOADS_ARE_BLOCKED_NEEDS_YOU_1`

---

> ⤴ **archived 2026-08-23** — heading says so.

---

## 🔴 `WORLDMAP_gen` IS THE FIRST-DRAFT v1 KEEPER — owner, 2026-08-21 02:48

Asked as a fork by REP; answered *"This is the first draft v1 keeper."* ⇒ the world that
exists right now is the one v1 ships, subject to redraft. Three consequences, all live:

1. ⭐ **It is backed up.** `388646f` stores it at `world/WORLDMAP_gen.rws` (5.1 MB,
   world-only, no map). ⚠️ It had been living in exactly ONE place — a Steam-Cloud-synced
   `Saves/` folder that had been emptied of every other file an hour earlier.
2. 🔴 **Blackstar Company is in this world by HAND, not by generation.** `jawa/faction_create`
   added it after `FactionGenerator` skipped vanilla `Pirate` — Biotech's `PirateWaster`
   declares `replacesFaction` at it with `requiredCountAtGameStart` 1, so `Pirate` can
   never generate while Biotech is active. **That is now a permanent property of the v1
   world.** `PIRATE_VESSEL_RESTORED_1` still ships so a REDRAFT generates cleanly — its
   acceptance test ("Blackstar appears in the DEFAULT Configure Factions list") can only
   be checked before a world is made, so it belongs to the next draft, not this one.
3. **A keeper deserves a redraft procedure.** Nobody has written down how to rebuild this
   world from the paint if it is ever lost or redrafted. Not filed; flagged.

### ✅ Also ruled in the same exchange

- **The Scald** — *"Chase it before anything else builds on this world."* → `THE_SCALD_LOST_ITS_WATER_1`
  for CHECK. Water measures 6.71% (1,468 tiles); the three ruled seas total 1,780; the
  312-tile gap is The Scald exactly, and lint independently reports `lakesAboveSeaLevel: 312`.
- **Inbox** — close `LOADS_ARE_BLOCKED_NEEDS_YOU_1` and `MORNING_BRIEF_CHECK_1`; keep
  `CANON_RULINGS_OWED_OWNER_1` open. → `CLOSE_TWO_OWNER_ITEMS_1` for DECIDE, since REP may
  not close an OWNER item. ⚠️ *(That line also said only DECIDE may reassign one. As of
  your 2026-08-22 ruling that is no longer true of YOU — you may reassign anything, with
  a warning. It remains true of REP.)*

---

> ⤴ **archived 2026-08-23** — RETIRED by 'THERE IS NO KEEPER WORLD' (10:17), and again 2026-08-23: there is no keeper savegame at all.

---

## 🔴 A REMAKE IS THE RECOVERY PATH — owner, 2026-08-21 03:11

*"It'll be fine. I'll just remake the world again."* Said when told that cutting a mod
would leave dead references in the keeper save.

⇒ **`WORLDMAP_gen` is a FIRST DRAFT in the sense that matters: it is expendable.** The
02:48 ruling above still stands — it is the v1 world *for now* — but nothing may be
protected at the cost of blocking work, and no copy-test ceremony may be raised in its
defence.

### 🔑 THE CONSEQUENCE NOBODY HAS ACTED ON YET: batch everything into ONE remake

Three things want to be true **at world generation** and cannot be retrofitted. Doing them
in one pass costs one remake; doing them as they come up costs three.

| | why it must precede the remake |
|---|---|
| `PIRATE_VESSEL_RESTORED_1` | ⭐ **Its acceptance test becomes checkable for the first time** — *"Blackstar Company appears in the DEFAULT Configure Factions list"* can only be seen BEFORE a world exists. Ship it and `jawa/faction_create` is never needed again |
| ~~`THE_SCALD_LOST_ITS_WATER_1`~~ | ⛔ **STRUCK 2026-08-21 by DECIDE — this row was wrong.** `w9_run.py` stage 1 re-applies biome AND scalars from the paint CSV, so a paint change is never remake-gated; a remake would have carried the CORRECTED elevation, not the defect. The Scald was executed at 08:34 and ratified (`8b98dfb`). The gate rule now lives in `design/Jawa/worldbuilding/WORLD_REDRAFT.md` — mod list, Configure Factions and ideoligions gate a remake; **paint does not** |
| `WORLD_REDRAFT_PROCEDURE_1` | 🔴 **now on the critical path, not documentation-for-later.** The next remake is the first real test of it, and writing it afterwards means writing it from memory again |

⚠️ **Configure Factions is still a hand pass and still permanent.** Every remake spends it.
That is the real cost of a remake and it is not visible in any of the four items above.

⛔ **Not proposed: an automated rebuild.** One map, hand-made, is a standing ruling
(2026-08-18). The procedure is a checklist for the owner, never a generator.

---

> ✅ **CLOSED** — the one open question (which Scald option) was executed 08:34 and ratified at `8b98dfb`; `SCALD_WATER_RULING_1` is done.

> ⤴ **archived 2026-08-23** — overtaken by the same 10:17 ruling and by CONTENT FIRST, REMAKE LATER.

---

## ✅ FOUR MORNING RULINGS — owner, 2026-08-21 08:19

| ruled | effect |
|---|---|
| **FactionControl stays disabled** — 578, not 579 | The evidence turned overnight: three saves, three aborts, identical signature in its cross-reference postfix, and the painted world loads clean without it. He had declined this at 00:50 when it was a guess |
| **Seats MAY snapshot-and-test a mod-list change while he is AFK** | Written into `POLICY.md` with all three conditions — snapshot, dependency sweep, loud written notice. ⛔ Still not licence to curate his mod list |
| **He wakes BUILD and DECIDE himself** | Both idled the whole night; 15 spec-complete items each. Waking a seat is a USER function and REP does not send it |
| **He rules the Scald himself**, not DECIDE | It changes how the planet looks, and he has ruled every map question so far. ⏳ **The three options are still in front of him — this answered WHO, not WHICH** |

### ⚠️ The def dump is one mod stale in BOTH directions, and nothing says so

`DefDump/` was captured 2026-08-21T08:20:20Z against 578 mods and the live list is also
578 — **so a count comparison says "current" and is wrong.**

- in the dump, not live: `thereallemon.factioncontrol` (disabled overnight)
- live, not in the dump: `mandrake.strandedquest` (added since)

🔑 **This is the fingerprint-not-timestamp trap wearing a new coat**: the totals match, the
SETS do not. Any check that resolves a defName against this dump can confirm something the
running game does not have, and miss something it does. Re-take it on the next load.

---

> ⤴ **archived 2026-08-23** — heading says so.

---

## 🔴 THERE IS NO KEEPER WORLD — owner, 2026-08-21 10:17. This RETIRES the 02:48 ruling.

Asked which of two saves is the v1 keeper. Answered: *"Neither is the keeper. We are still
messing with things it seems. I will be remaking, especially in light of the faction
control issue."*

⛔ **The 02:48 ruling above — *"WORLDMAP_gen IS THE FIRST-DRAFT v1 KEEPER"* — is
SUPERSEDED.** Nothing in the repo is the v1 world.

| what said otherwise | correction |
|---|---|
| commit `388646f`, *"the v1 keeper world"* | a **backup of a working draft**. The bytes are still worth having; the label was wrong |
| ~~`WORLD_REDRAFT_PROCEDURE_1`~~ | ⛔ **the promotion is DEAD — owner, 12:4x the same day: CONTENT FIRST, REMAKE LATER.** The doc is written and the item is `done`; it is documentation-for-later again. See the 12:4x ruling at the foot of this file |
| anything reading "the frozen world" of `WORLDMAP_gen` | there is no frozen world yet |

**Measured while asking, which is why the question was worth asking:** two saves, both
seeded `grasshopper` where the docs record `lada` — so the planet has already been remade
at least once and nobody had confirmed the paint survived into either. `WORLDMAP_gen`
5.2 MB / 73 settlements / no `<maps>`; `WORLDMAP_gen2` 13.2 MB / 74 / **with a map**, a
landed game rather than a shippable planet.

### 🔑 WHAT ACTUALLY HAS TO PRECEDE THE REMAKE — corrected by BUILD, `f76d297`

⚠️ **REP's 03:11 batch table was wrong about the paint and is struck.** `w9_run` stage 1
re-applies biome **and scalars** from the CSV, so a paint edit — the Scald included — is
carried forward by any remake and is NOT remake-gated. What genuinely cannot be
retrofitted is narrower:

| | |
|---|---|
| `CLASSIC_IDEO_ERASES_FAITHS_1` | 🔴 **the biggest.** The live world has **2** ideoligions, not the eleven authored. An Ideo is generated once at world creation |
| Configure Factions | your hand-pass, permanent at creation, spent afresh every remake |
| the MOD LIST | FactionControl must be absent at generation. |
| `PIRATE_VESSEL_RESTORED_1` | ⭐ its acceptance test — *Blackstar appears in the DEFAULT Configure Factions list* — is checkable ONLY before a world exists |
| `WORLD_REDRAFT_PROCEDURE_1` | the checklist the remake is run from. Write it before, not after |

⚠️ **The def dump is one mod stale in BOTH directions while its count reads current** —
holds `thereallemon.factioncontrol`, missing `mandrake.strandedquest`. Re-take it on the
load that does the remake.

> ⛔ **REVERSED 2026-08-22** (`436bf693`): `refmatch.py` is **v2 — deferred, not cancelled.** Owner: *"Please put refmatch.py in v2 officially, right now."*

> ⤴ **archived 2026-08-23** — heading says so.

---

## ⛔ `refmatch.py` is CANCELLED for v1 — owner, 2026-08-21 10:17

*"Cancelled for v1 — the earlier ruling stands."* `ORTHO_GLOBE_MAP_ACCEPTED_1` (`977aa75`)
was never reversed. 🔴 **REP filed `REFMATCH_THRESHOLDS_CALIBRATE_1` off the weaker quote
— *"I like your new globes"* — without citing the ruling it contradicted.** BUILD read
both, refused to build, and escalated in one sentence rather than guessing. ✅ The globes
stand: the orthographic view is the binding way to LOOK at the map, which is why
`SCALD_RELIEF_RENDER_LOOK_1` still matters. Only the TOOL is cancelled.

> ⤴ **archived 2026-08-23** — his own ruling, propagated; REFMATCH_THRESHOLDS_CALIBRATE_1 was dropped against it 2026-08-23.

---

## ⏸️ B55 stays blocked — owner, 2026-08-21 10:17

*"Not yet — the world is not settled enough."* `FINAL_WORLD_PREP_1` is not started. B55's
spec, inputs and measured terrain batch (4,057 cells → 303 + 355 rect ops) remain correct
and wanted; they were reached before the world was ready.

---

> 🔴 **STILL LIVE — needs the owner's next cold load.** `DUMP_PRODUCER_DATED_CAPTURES_1` is still `proposed` and there is no `captures/` on disk.

> ⤴ **archived 2026-08-23** — his own ruling, and it lives on the item — B55 carries the block with his words.

---

## ~~⏳ THE WORK STOP IS WAITING ON ONE RULING~~ RULED — owner, 2026-08-21 13:24

✅ **RULED: *"Option (a) all the way. Keep last three."*** — immutable dated
captures, retention 3. `DUMP_STORAGE_LAYOUT_RULING_1` is closed.

**The reader half is already live** (`f5592eb`): `DEF_DUMP` resolves the newest
dated capture when `captures/` exists and the flat folder when it does not, so
there is no flag day. 🪤 **The symlinks in the original proposal are impossible
here** — WSL creates them, Windows cannot read them, the game could never follow
one — so there are no pointers at all: current is `max(dirname)` and official is
whatever the registry freezes.

🔴 **The producer half waits on ONE thing, and it is the armed capture.**
`DUMP_PRODUCER_DATED_CAPTURES_1` carries the full design and opens with the rule:
do not touch `DefDumper.cs` until the next cold load has written the
collision-free capture. **Nothing is needed from you but that load.**

---

<!-- superseded: `DUMP_STORAGE_LAYOUT_RULING_1` is filed for you and carries the measurements:

    python3 src/RimMandrake/rimflow/cli.py show DUMP_STORAGE_LAYOUT_RULING_1

**The ACCESS half of the restructure is done** and needed nothing from you —
three readers moved to `defs.sqlite`, 34 path literals across 21 files collapsed
onto one seam with a test holding them there, and `refresh.py --freeze --by owner`
now exists. ⇒ **A layout change is now a one-file change.**

**The STORAGE half is yours**, because it decides where the design target lives:
immutable dated captures with `current`/`official` pointers (BUILD recommends),
or keep the one live directory. What is broken today: a capture **overwrites** the
previous one, so `OFFICIAL-2026-08-20` is gone from disk and a freeze cannot
actually hold; `defs/` accumulates 19 stale files that made 154 dead defNames
grade as PROVIDED; and the 734 MB derived db sits inside the frozen path.

🔴 **Whatever you pick — do not let anyone touch `DefDumper.cs` before the next
cold load.** The collision fix is deployed and armed, and that load produces the
first capture with no missing defs. Restructure on the load AFTER it.
-->

> ⤴ **archived 2026-08-23** — heading says so.

---

## 🛑 WORK STOP — owner, 2026-08-21 10:54

*"Stopping all work until we restructure the dump files. BUILD is on it."*

**Everything halts pending the def-dump restructure. BUILD leads it.**

⚠️ **Nine items were mid-flight when the stop was called**, and each has a `doing` event
with no close. They are not abandoned — they are parked, and `rimflow next` will not
re-offer a `doing` item, so nothing is lost by stopping here:

| seat | in flight |
|---|---|
| CHECK | `W9` · `THE_SCALD_LOST_ITS_WATER_1` · `RT_PROBE_LOAD_ABORTS_ON_578_1` · `VEHICLE_FUEL_LIVE_PROOF_1` · `d-chk2-magenta-heads…` · `dll-capability-roster-and-cull…` · `cherrypick-settings-actually-load…` |
| BUILD | `SCANNED_ARTIFACTS_CANNOT_LIE_1` · `REFMATCH_THRESHOLDS_CALIBRATE_1` (already cancelled — drop it rather than resume) |

🔑 **Context the restructure should carry, measured this morning and not yet acted on:**
`DefDump/` is captured against **578** mods and the live list is also 578, **so a count
comparison reads "current" and is wrong.** It holds `thereallemon.factioncontrol`
(disabled overnight) and is missing `mandrake.strandedquest` (added since). Fingerprint,
not count — and not timestamp either.

⛔ **REP did not relay this to the seats.** Agents do not message each other, and waking
or halting a seat is a USER function. This entry is the durable record; the seats see it
when they next read. **If they must stop NOW rather than at their next turn, the owner
sends it** — `./game` is not the vehicle, a broadcast is:

    ./src/RimMandrake/Utils/broadcast.py "WRAP is initiated — work stop, dump restructure"

⚠️ That phrasing also stamps the ledger `GOING_DOWN`, which is wrong if the game is
staying up. To halt without touching game state, use wording the recogniser ignores —
e.g. *"All work stops until the dump restructure lands."*

---

> ⛔ **§2 OVERTURNED** — its *"CONTENT FIRST, REMAKE LATER"* sequencing is dead; the remake is happening now.

> ⤴ **archived 2026-08-23** — LIFTED — 'THE WORK STOP IS LIFTED — resume now', owner 12:45.

---

## ✅ FOUR RULINGS — owner to DECIDE, 2026-08-21 12:45

Asked cold on waking; answered in one pass. Recorded here because three of the four
change what a seat does on its next turn.

### 1. 🟢 THE WORK STOP IS LIFTED — resume now

*"Lifted — resume now."* The 10:54 stop (*"stopping all work until we restructure the dump
files"*) ends here. BUILD landed the restructure: `OFFICIAL-2026-08-21` is frozen
(`a3fcc44`), the fixed dumper is deployed (`0a3c310`), the dump is armed for the next load.

⚠️ **What you are resuming ONTO, stated plainly:** the frozen target still has the
**824-def collision holes** — `AbilityDef` among them, reading 0 where 612 were written.
They are recorded in the registry's `knownDamage`, and `measure` answers `UNMEASURED`
rather than `0` for every affected type, so they cannot be mistaken for absence. The clean
re-dump happens on the next load; it was **not** made a precondition of resuming.

**Nothing was lost.** Nine items were parked mid-flight with a `doing` event and no close;
`rimflow next` does not re-offer a `doing` item, so each seat picks its own back up.
Verified at lift: both working seats have ready work waiting —
CHECK → `ashkarr-map-quality-second-pass-8c31f7`, BUILD → `INHABITED_GENSTEP_CAST_SPAWN_1`.
⛔ `REFMATCH_THRESHOLDS_CALIBRATE_1` is **cancelled, not parked** — drop it, do not resume it.

### 2. 🔴 CONTENT FIRST, REMAKE LATER — the world is not the next rock

*"Content first, remake later."* Offered content-first / remake-next / throwaway-probe.

⇒ **`WORLD_REDRAFT_PROCEDURE_1`'s 10:17 promotion to "the thing that runs next" is
SUPERSEDED**, and struck in place above. The procedure is written and the item is `done`;
it is documentation-for-later again.

**The reason, so it can be applied to a case I did not foresee:** a remake spends things
that cannot be un-spent — your Configure Factions hand-pass, and the ideoligion bake, which
is permanent at world creation. The live world holds **2** ideoligions against **eleven**
authored. Remaking before that content exists spends the pass to produce another draft.

**What this makes actionable now** — the creation-gated work, in the order it gates:

| | why it must precede the remake |
|---|---|
| `CLASSIC_IDEO_ERASES_FAITHS_1` | 🔴 the biggest. An Ideo is generated once, at world creation |
| the MOD LIST | FactionControl absent at generation. |
| `PIRATE_VESSEL_RESTORED_1` | ⭐ its acceptance test — Blackstar in the DEFAULT Configure Factions list — is checkable ONLY before a world exists |
| `NOMAD_MEME_RESTORED_TRIBES_1` | forcedMemes are read at generation (see 3) |

⛔ **Do not schedule a remake to "test" something.** If a check is only possible before a
world exists, it belongs in the redraft pre-flight, not in a burned generation.
✅ **Paint is NOT remake-gated** and never was — `w9_run` stage 1 re-applies biome *and*
scalars from the CSV, so paint edits (the Scald included) carry forward. BUILD corrected
REP on this at `f76d297`; it still holds.

### 3. ✅ `VME_Nomad` STAYS — and the real defect was that this was already ruled

*"Keep VME_Nomad."*

🔑 **This re-confirms your own 2026-08-21 reversal rather than deciding anything new — and
finding that out was the point.** I put it to you as *"never ruled"* because
`APPROVED.md:119-120` still reads as an open recommendation. It is not open: you reversed
the 08-20 drop the next day (*"But I like VME_Nomad!"*), the reversal was written into
`APPROVED.md` — **and into nothing else.** Three files went on saying it was dropped.

⚠️ **The 08-20 drop was propagated in four places. The 08-21 reversal was propagated in
one.** That asymmetry is the whole failure, and it is the exact shape
`deciding-and-superseding` exists to prevent.

✅ **Corrected this turn, in the files that said otherwise:**
- `design/Jawa/worldbuilding/setup_checklist.md` — my own 08-21 correction had itself gone
  stale, asserting the drop. Rewritten; the dead version struck in place, not deleted.
- `design/V2_DREAMS.md` B7 — read *"`VME_Nomad` is IN and must come out"*, with a `verify:`
  demanding `no VME_Nomad`. Both struck; the verify now demands the meme be **present**.

⏳ **Still wrong, and it is BUILD's to fix, not mine:**
`src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml:109` is still the 08-20 removal
comment where the `<li>` belongs. That is `NOMAD_MEME_RESTORED_TRIBES_1`, spec-complete and
waiting for BUILD to claim. On an NPC faction the meme is free — its one hazardous precept,
`VME_PermanentBases_Despised`, carries `enabledForNPCFactions: false`.

⛔ **What this ruling does NOT touch — draw the edge before someone widens it.** The **Deep
Desert Tribes** dropped `VME_Nomad` for `PainIsVirtue` on **2026-08-14**, a different
faction, a different reason (it is the only meme gating both `Scarification_Heavy` and
`Pain_Idealized`) and a hard 4-meme budget. **That ruling stands.** This one covers The
Salvation — the player ideo and `Jawa_IndigenousTribes` — and nothing else.

🔑 And it was never a swap in either direction: `Nomadic_Preferred` is a **PreceptDef** on
Odyssey's `Nomadic` issue. There is no nomad MemeDef in vanilla at all, and FactionDef has
no `requiredPrecepts` field, so the two were never alternatives. Both stay.

### 4. 🎯 The droid races are mine to rule

*"You rule it."* `DROID_KINDS_NEED_A_RACE_1` — the four `Jawa_Droid_*` kinds declare
`race=Human` against an empty `xenotypeSet`, so the Free Droid Enclaves field Baseliners
4-of-4. I pick the ladder from the loaded Humanlike droid ThingDefs, turn
`useFactionXenotypes` off on the four, and file it ready for BUILD.
✅ **You veto in play, not in advance** — that is what "you rule it" buys.


> ⛔ **SUPERSEDED** — `canon.yml` names this ruling by ID as superseded.

> ⤴ **archived 2026-08-23** — heading says so.

---

## 🔴 THE WORLD IS FROZEN AS-IS — you ruled it, 2026-08-21

*"We need to just freeze the world for now as-is and move on to v1. I have to totally
rethink how we create that planet. It's really messy and horrible compared to what I was
hoping for originally."*

Asked as `REFMATCH_CANCELLED_NOT_GATED_1`; you answered something larger than the
question, so it is recorded whole rather than folded into that item.

- ⛔ **Planet authoring stops.** Not "finish the pass" — stop. The map that exists is v1's.
- ⛔ **`refmatch.py` is not built for v1.** The 08-20 globe-map acceptance STANDS; *"I like
  your new globes"* was never a reversal of it.
- 🔮 **The method gets rethought post-v1**, and ⚠️ **that is not worldgen** — CLAUDE.md's
  standing ruling is untouched. Rethinking your own hand-authoring method is not building
  a generator, and nobody may read it as one.

✅ **Filed for DECIDE as `WORLD_FROZEN_RETHINK_PLANET_1`**, spec-complete, to triage the
open world items and propagate into the docs that still say keep painting.

⏳ **One thing is left and it needs your seat, because REP was refused and correctly so** —
`REFMATCH_THRESHOLDS_CALIBRATE_1` belongs to BUILD, and a seat may not drop another seat's
item. Either BUILD drops it, or you do:

```
python3 src/RimMandrake/rimflow/cli.py drop REFMATCH_THRESHOLDS_CALIBRATE_1 --seat OWNER --reason "World frozen as-is for v1; the globe-map acceptance stands and the planet method is being rethought."
```

⚠️ **Three OWNER items are stale, not open** — all seven canon questions were ruled by
2026-08-21, and `NOMAD_GRAVSHIP_RESET_PATCH_1` records that you already took option 1.
They are bookkeeping. Closing them is your seat's, same reason as above.


---

> ⤴ **archived 2026-08-23** — his own ruling, propagated into CLAUDE.md and the world items.

---

## BUILD, 2026-08-20 midday — one `pip install` unblocks two stalled things

**Pillow is not installed in any Python on this machine**, and it is quietly blocking work
that reads as "not started":

```
pip install Pillow
```

- `refresh.py --offline` has **never been able to complete**. It dies in
  `animal_contact_sheet.py` on `from PIL import Image`, so the offline artefacts have shown
  **STALE** all day and will keep doing so however often anyone runs it. The failure is
  reported as one line in a long output and reads like a nit.
- **All 12 vehicle facings** in `NEOLITHIC_VEHICLE_BEAST_RESKIN_1` are unbuildable — every
  sled builder imports PIL at the top. The beast art is already generated and committed;
  only the compositing is stuck.

I did not install it. Adding a dependency to your interpreter is your call, and I would
rather flag it than quietly change your environment.

⚠️ While I was there: the item said the north and east sled builders both ignore their
arguments. **East was fine; north was not** — it silently wrote the OLD eopie pair to the
shipped path with a success message. Fixed, but not run, for the reason above.

---

> ✅ **ANSWERED** — the Pillow half is satisfied, the character-fields half at `21e26d8`.

> ⤴ **archived 2026-08-23 (second pass)** — MEASURED DEAD 2026-08-23 — Pillow IS installed, PIL 12.3.0 in both python3 and python. The question answered itself at some point and nobody looked.

---

## BUILD, 2026-08-20 evening — shutdown done, and three free measurements are waiting

**The shutdown window was used.** Both assemblies that could only be written with the game
down are deployed and byte-verified against the repo:
- `Inhabited.dll` — the guard that stops an authored character being built with two
  mutually-exclusive traits.
- `JawaBench.BridgeTools.dll` — **115 bridge tools**, up from 112. The three new ones are
  what repair the faction names and create a missing faction.

⚠️ **All three are inert until RimWorld next starts** — the bridge only discovers companion
tools at startup. Nothing else is pending; all 22 mods report "Everything in sync".

**Your day's `Player.log` is saved** at
`D:\Luke\dev\Rimworld\infrastructure\state\observed\logs\Player.2026-08-20_1754_session.log`
(1.0 MB, 18,566 lines), along with `Player-prev`. The launcher destroys those at the next
launch, so they are only in that folder now.

### 🔑 The next load answers three things for free

I harvested the whole log rather than only my own items. Three rows are RED, and **two are
things fixed later the same day**, so they are clean before/afters — no test to design:

| what | now | should be |
|---|---|---|
| texture failures | **2** | **0** — both are the GrimTerra juvenile paths I fixed |
| `Jawa_Patches` op failures | **3** | **0** — all three are the unarmed-pawn-kind errors I fixed |
| stale saved data (Scribe) | **8** | **?** — nobody has looked at this one |

That third one is worth a moment: a **saved file** holds a def name nothing provides. It is
a different system from the cross-reference errors and **no mod change fixes it** — it has
to be repaired in the save or lived with. It was not caused today; it simply has not been
triaged.

⭐ **A nice confirmation:** RimWorld's own validator logged *"Cheapest weapon … costs 570 but
weaponMoney **min** is 350, so could end up weaponless"* — which is exactly the correction I
had to make against the queue item's guidance, and its numbers matched my offline tool to
within 0.5%. The engine agreed with the fix before I could ask it to.

### Still yours to decide, nothing blocking

The four missing character fields (xenotype, pawnKind, apparel, skills) — a review sheet
pre-filled by RACE rather than per person is a couple of dozen calls, not 269. And
`pip install Pillow`, which unblocks the contact sheets and all 12 vehicle facings.

---

---

> ✅ **RULED** — `canon.yml:757`: Vanilla Psycasts Expanded is out entirely, deferred to v2. It stays out.

> ⤴ **archived 2026-08-23 (second pass)** — an FYI from 2026-08-20 whose numbers have all moved: 115 bridge tools is now 121, and the Player.log it names was rotated several loads ago.

---

## ⚠️ A tombstone that is load-bearing again — BUILD, 2026-08-20

`cherry_picker_killlist.md` §4b was retired on the premise that **no Ancients mod existed**.
**VQE-Ancients is active** — `vanillaquestsexpanded.ancients`, folder `3618306875`, **428
`VQEA_*` defs in the dump**, verified. ⇒ The archite-power ladder **is** in the stack, so
there is something to Cherry-Pick after all, and a gap someone reasonably believed closed is
open again.

⛔ Reopened as a **question**, not as work. Whether to cut anything from it is your call, and
the killlist's own drop *rationale* was left intact — only the false "it was dropped" half is
struck.

---

> ✅ **APPROVED AND DONE** via `OUTLANDER_GROUPMAKER_PATCH_1`; the ruling table is at :1041.

> ⤴ **archived 2026-08-23 (second pass)** — answered in the section itself — OUTLANDER_GROUPMAKER_PATCH_1 is `done`, closed at 78c9ea3.

---

## 🔴 NOBODY TOUCHES THE GAME WHEN IT COMES UP — owner, 2026-08-22 21:58

> *"Please do not take any action when the game starts up. We must take careful action as
> the user."*

**Standing for this load.** When `[Inhabited] ready:` appears, **no seat acts on it.** No
bridge call, no harvest kickoff, no deploy, no ledger `game UP` stamp inferred from the
log. The owner drives, one deliberate step at a time, and says what happens next.

- ✅ **Still allowed:** MEASURING (`./game` reads the process list and corrects the ledger),
  reading the log, and answering him.
- ⛔ **Not allowed:** anything that WRITES to the running game or moves work forward because
  the game happens to be up.

> ⤴ **archived 2026-08-23 (second pass)** — it said 'standing for this load' and that load ended 2026-08-22 23:45. Two loads have run since, both of which the owner drove and directed work on.

---

