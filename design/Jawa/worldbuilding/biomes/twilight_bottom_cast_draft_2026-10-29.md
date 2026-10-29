# The Twilight Deep — bottom cast, draft sheet (2026-10-29)

> **DRAFT. Nothing on this sheet is ruled.** This sheet is for the owner to tune or bless
> later. design/ is his pen, and this is a proposal written in it.
>
> - **Item:** `TWILIGHT_BOTTOM_CAST_1` (parent `TWILIGHTSEA_FLOOR_PASS_1`). Logged as
>   *delegated: design* (Conductor triage, 2026-10-29). It is **not** owner approval.
> - **Source section:** `the_twilight_deep_content_2026-09-26.md` §9, and §9.3 above all
>   (the roles). §2.2, §8.1–§8.6 and §11 Q4/Q8/Q9/Q10 are also used.
> - **Supersedes on deletion:** `the_twilight_deep_bottom_cast_draft_2026-09-27.md`
>   (commit `bb9d83c3d6`) is deleted by the same commit that adds this sheet. It is wrong
>   material: it was written before the owner's 2026-09-27 ruling below, so it has the
>   well-keeper selling skylight rights and charts and the lamp-wright selling chains and
>   techprints, and it has the net-widow fishing the shaft. Its seven names and most of
>   its prose were sound, so they are carried here and recast to the rulings.
>
> **Rulings relied on**
>
> 1. **Ban 4: the Compact is never hostile.** The FactionDef `RUT_Jawa_DeepwaterCompact`
>    sets `raidsForbidden true` [CD §9.1]. No resident fights, guards, sanctions or
>    threatens.
> 2. **Q10, houses yes to all three** (card, 2026-09-26). The houses are per-tile world
>    objects, there is a new bottom cast of 6–8, and §9.3's roles are the starting sheet
>    [CD §11 Q10; ledger note on `TWILIGHTSEA_FLOOR_PASS_1`].
> 3. **Fishing correction.** The owner typed: *"you don't fish at the bottom of the ocean, I
>    had meant the shoreline fishing"*. The floor has no fishing verb and no nets. Floor
>    fish are hunted and beds are gathered by hand [CD §11 Q4/Q9; ledger OWNER note].
> 4. **The Compact does not sell light.** The owner typed on 2026-09-27: *"The Compact does
>    NOT sell light, that's not a mechanic we accepted. Remove."* On the flora roster he
>    also typed: *"Keep the plants and the lore of their commerce relationship, no player
>    mechanic."* So there are no leases, no charts as items, no claim buoys and no poaching
>    standing. Wells are free ground and the Compact are "keepers and neighbours"
>    [light economy pass header and §4; flora pass "Ruled"; `TWILIGHT_TENANCY_PAPER_REMOVAL_1`,
>    done `3e6a74b87`]. ⚠️ Because of this, **"lease practice" in the brief is stale as a
>    mechanism.** It is taught below as **well practice**: how you live on light that is
>    lent for a week, with no paper involved (see §3).
> 5. **The waveglass.** The ceiling is *the waveglass*, the Deepwater call it *the lid*,
>    and what it sheds is *veil-fall*. Skylights drift over about a week [CD §2.1; ledger
>    OWNER notes].
> 6. **The bank works are the immobile prize.** The stake-line is both the farm's edge
>    and the safety tell. The Compact's weir never breaches because it is tended [card;
>    river pass §4].
> 7. **The vaulisk** (C3): at most one per map, and its tell is always readable. **The
>    lamp-lure danger is cut** (C2): light does not call the sea here [danger pass D3, D4].
>    **The suulk** (C4) grazes lamps, the sun-sphere included [danger pass D2].
> 8. **Lamp count stays small** (move cost is a cheap haul) [card; light pass §2.2].
>
> **Marking.** **[CD §x]** marks a fact read from the content doc. **[LP]** is the light
> economy pass, **[DP]** the danger pass, **[RP]** the river pass and **[FP]** the flora
> pass (all `the_twilight_deep_*_2026-09-27.md`, read this pass). **[prior draft]** marks
> material carried over from the deleted 2026-09-27 sheet. **(unverified)** marks anything
> no document says: my inventions, and every claim about engine fit that I did not test.
> All first-met lines are invented and carry the **(unverified)** mark.

## 1. The holdings

There is one per-tile Inhabited place on one bank, made of three districts (the holdings), where a channel's eddy meets a
cluster of wells. Their names are chart names [CD §9.3: *"each holding's name is a chart
name"*]. The Compact keep their charts as their own lore and hands. A chart is never an
item and never a forecast product sold to the player [ruling 4].

| holding | source of name | what stands there |
|---|---|---|
| **Nine-Well Bank** (the seat) | CD §9.3 | the chart house, the lamp-wright's yard, the child underfoot |
| **Low Lantern** (the working eddy, downstream) | CD §9.3 | the Compact's tended weir, the stake-line, the silt farm, the ford |
| **Farwake** (one dome, upslope on high dry ground) | prior draft (unverified) | the two who watch the sky; the picked wreck out in the dark past it |

Fabric per holding is 2–4 low domes (Farwake is the one-dome exception) with lit doorways, lattice-timber walls, gold
aluun-pane windows, a ghallowyn column, three noothelm at each door, bank-stakes, a ford
and a kelp plot on the bank [CD §9.2]. ⚠️ CD §9.2 also lists *"a claim-buoy in the nearest
shaft"*. That item is **void** under ruling 4 and must not be placed.

Placement shape: shape (a), one `WorldObject_Inhabited` per diveable tile, created lazily
when a hatch first opens [CD §9.2, BENCH position; Q10 ruled yes]. **Free tier:** the houses
are lit and empty, or carry a generic `RM_` water-people cast. The named cast below is
campaign content, patched on by `MayRequire` [CD §9.4].

## 2. The cast — seven residents

The fate for all of them is `Resident`. Races come from the Compact's amphibian list
[CD §9.1, §9.3]. Every teaching is a chore, a refusal, a habit or an errand. None is a
sale of light and none is a fight.

### 2.1 Vhessune — the well-keeper

- **House:** Nine-Well Bank, in the chart house, a dome whose door faces the oldest open
  well.
- **Role:** keeper. Nautolan, female, 50s [CD §9.3].
- **Teaches:** **well practice**, the reworked "lease practice" (§3). She reads the
  skylights and keeps the chart of which wells are opening and which are closing, in
  lamp-black on vaal-green vellum. She has been wrong once in thirty years, and it cost a
  family its plot [CD §9.3].
  - The player learns from what she does, not from anything she sells.
  - She never sows a waning well.
  - When a well dies, she is first to walk her stakes out to the next one that opens.
    Following her is how a player finds new light.
  - She watches the waning rim, which is the free sky-read: about 1.5 days of warning
    [LP §1.2].
  - She counts pallu to read how many days a well has left [FP ecology; CD §5 fish table's *"The
    Compact counts them to price a skylight"*; the pricing purpose is void under the owner's
    2026-09-27 ruling, so kept as lore only].
  - She will not set a plot under a well she thinks the gardener is closing, and she
    will not say why [CD §9.3, kept as behaviour].
- **First-met line:** *"The light is lent, not given. Watch the rim, not the gold."*
  (unverified)
- **Visual:** a tall, grey-green Nautolan woman with her head-tresses bound in vellum
  strips, ink-black fingers, and a rolled green chart under one arm. (unverified)
- **Defs to reuse:** `RM_Skylight`, `RM_Pallu`, `RM_TollhornCore` (she buys it and never
  sells it; plain trade good, lore only [FP ruling 4]), `RM_InhabitedPlace_WaterHold`.

### 2.2 Tharukel — the gardener-warden

- **House:** Farwake, a single dome on the high dry ground with the widest view of the
  lid.
- **Role:** watcher. Selkath, male, 60s [CD §9.3].
- **Teaches:** **the sky**: the gardener's passes, veil-fall and the laden deck,
  lid-dark. He logs the lanternwhale's passes and has never touched it. The Compact's law
  about the gardener is his to keep, and he has decided it is the only law that matters.
  He knows the shadow before it falls and stands outside to watch it every time
  [CD §9.3; §7.3].
  - His behaviour is the forecast. Hours before a pass he stands outside, still, facing
    up. Before a lid-dark he lights every lamp at Farwake [prior draft; DP D9].
  - When he steps out from under the open lid, that is the cue for the pane-shadow
    warning (about 15 seconds) [DP D1 / ruling C6].
  - He asks one diver, once, how many panes lay on their deck after a heavy shed. The
    question teaches that a laden deck must be cleared before launch [DP D8; prior
    draft].
- **First-met line:** *"When the light goes quiet, look up. Then step out from under it."*
  (unverified)
- **Visual:** a heavy, stooped Selkath who stands motionless outside his door with his
  face tipped up and a knotted pass-log cord around his neck. (unverified)
- **Defs to reuse:** `RM_Lanternwhale`, `RM_VeilPane`, the gardener event family
  `RM_GardenerOverhead` / `RM_PassingShadow` (names from LP §5; a defName grep of src
  on 2026-10-29 found neither, so both are owed or named differently).

### 2.3 Maruvenn — the net-widow, recast as the stake-widow

- **House:** Low Lantern, in the dome nearest the ford, with her stake-mallet by the
  door.
- **Role:** warden. Quarren, female, 40s [CD §9.3].
- **Teaches:** **stake-lines**, plus the undersurge tells and the fords.
  - ⚠️ Correction: §9.3 has her *"fish the shaft"* and her partner lost *"to save a
    net"*. Both are void under ruling 3. In this sheet she hand-gathers the beds, and her
    partner walked into the channel after a drifting gathering-basket. (unverified
    substitution)
  - She keeps the ford stones repaired and adds one every year. She will tell a diver
    exactly where the edge is once, and never again [CD §9.3].
  - Her one warning is the rule the river pass states: *the stakes stand where the surge
    reaches, not where the calm ends* [RP §4].
  - After that warning, her chores teach. She re-drives stakes every day, which is the
    maintenance the player will owe on their own line. Thessmoss stops dead at her stakes
    [CD §2.2; RP §4]. She weeds the tithemoss off them every morning, because a furred
    stake is a lapsed stake [FP §1].
  - She is first to move before an undersurge: she clears the crews off the inner bank
    when the murrol vanish upstream [RP §2 tells; DP D6].
- **First-met line:** *"Past my stakes the ground is the river's. I'll show you the edge
  once."* (unverified)
- **Visual:** a lean Quarren with her face-tendrils tied back, mud to the knees, a
  bundle of lamp-topped stakes over one shoulder. (unverified)
- **Defs to reuse:** `RM_BankStake`, `RM_FordStones`, `RM_BankSilt`, `RM_Tithemoss`,
  `RM_Murrol`, the channel current (`RM_GenStep_TwilightChannels`).

### 2.4 Dorrhul — the weir-keeper

- **House:** Low Lantern, on the eddy margin, with his weir's hopper outside the
  door.
- **Role:** keeper. Herglic, male, 60s. This is the §9.3 bank-farmer grown into the
  bank works [prior draft]. ⚠️ §9.3 has the bank-farmer as a Quarren. A Herglic is the
  "rarely" tier [CD §9.1 weights 0.074]. Making him a Quarren again is the sitting's
  call.
- **Teaches:** **the weir form**, plus the silt-trap and the breach. The Compact's weir
  at Low Lantern already exists and is tended. The player learns the form by looking at
  it: lattice-timber and net-cord across the eddy margin, a hopper emptied daily, a
  silt-trap behind it, and the richest sown bank around it [RP §4].
  - His errand is the Compact's own practice: *drop the bundle in upstream, collect it at
    my weir* [RP §4].
  - His inspect line: *"his weir never breaches, because it is tended"* [RP §4, prior
    draft].
  - He asks for a dredge hand when the trap clogs. Doing the job once teaches it.
  - He hates tikkarr and will not kill one. He measures a good year in ghallowyn rings
    [CD §9.3].
  - He gathers by hand at the weir's edge. The weir is not a fishing zone [RP §4,
    ruling 3].
- **First-met line:** *"The river is a deed. I'm only its clerk. Bring me what it
  takes."* (unverified)
- **Visual:** a vast, slow Herglic, waist-deep in drift at a timber weir, a dredge-rake
  across his back. (unverified)
- **Defs to reuse:** `RM_BankWeir`, `RM_SiltTrap`, `RM_BankStake`, `RM_Weircomb` (the
  comb rows feed his banks [FP]), `RM_Tikkarr`.

### 2.5 Bimmelo — the child

- **House:** Nine-Well Bank. She lives in the lamp-wright's yard, but is always out on
  the bank.
- **Role:** child. Gungan, 9 [CD §9.3].
- **Teaches:** **the vaulisk tell**.
  - Every Compact child is taught it before they are taught to swim the current: *a lamp with
    no piip around it is not a lamp* [DP D4].
  - She chases her waelune anywhere on the bank, but every time she swerves wide around
    one steady gold light out in the dark. She does not break stride and does not
    explain [prior draft].
  - The full tell can be read off the thing she avoids: no piip sparks, no breathing
    pulse, and a dead ring of thessmoss around it [DP D4]. The flora pass adds more:
    hushcoral goes silent beside it, there is no gleamfloss shimmer over it, and
    tithemoss will not take on it [FP ecology].
  - She is the player's first sight of a Compact person on the floor: a child with a
    light in each hand [CD §9.3, *"It's a pretty ocean."*].
  - Optional micro-quest: her waelune rolls past the false lamp. She says the tell aloud
    once and will not follow it [prior draft]. Whether the micro-quest stays is an open
    question (§4).
- **First-met line:** *"That one doesn't breathe. Don't pick the ones that don't
  breathe."* (unverified)
- **Visual:** a small Gungan with ear-flaps flying, a waelune bobbing on a cord in each
  fist, both glowing. (unverified)
- **Defs to reuse:** `RM_Vaulisk`, `RM_TwilightScatterVauliskLure`, `RM_HoolimbrePlant`
  (the lamp it counterfeits), `RM_Hushcoral`, `RM_Gleamfloss`. Waelune is ruled a
  creature [CD Q11, BENCH position] but **has no def in src** (grep, unverified as
  absent), so the child's light is owed.

### 2.6 Sellowen — the lamp-wright

- **House:** Nine-Well Bank, in a workshop dome. One lit decoy stake stands alone at the
  holding's edge.
- **Role:** maker. Mon Calamari, male, 30s [CD §9.3].
- **Teaches:** **the suulk decoy, and the small constellation**.
  - Outside his door stands the Compact's answer to the suulk: a cheap lit stake, alone
    at the edge, with an inspect string that says why [DP D2]. It is free to copy.
  - He keeps few lamps and moves them often, which shows that a handful is enough
    [ruling 8, LP §2.2].
  - He will not have a vaulisk lure-organ through his door: the Compact will not keep the
    lamp that never breathes [DP D4].
  - ⚠️ Recast. §9.3 made him the bottom's **dealer** who *"sells light"* and holds a
    secret skylight right. Both are **void** under ruling 4. He makes aluun-pane lanterns
    and lamp-bladder strings for the Compact's own stakes and doors, never for sale. If
    the Inhabited trade role must sit on someone (`INHABITED_DESIGN.md` §1), ordinary
    goods only, and the sitting picks who (§4).
- **First-met line:** *"Light the cheap one first. The grazer always goes for the
  brightest."* (unverified)
- **Visual:** a round-eyed Mon Calamari in a pane-glass apron, with lamp-bladder strings
  looped on both arms and gold reflected in his eyes. (unverified)
- **Defs to reuse:** `RM_Suulk`, `RM_LampBladder`, `RM_HoolimbreLampClipped`,
  `RM_NoothelmLampClipped`, `RM_Aluun`, `RM_TetherChain` (shown in use, not sold),
  `RM_VauliskLureOrgan`.

### 2.7 Aldra Sohm — the diver who stayed (optional)

- **House:** Farwake. A ship's hull-lamp burns in her window, the one electric light on
  the floor [prior draft].
- **Role:** outlander. Human, female, 40s [CD §9.3].
- **Teaches:** **what the Compact is**, and the designed absence. She came down on a
  ship years ago and never went back up. She says out loud what the others will not: that
  the Compact keeps the last ordinary sea, and the surface has no idea [CD §9.3].
  - The picked wreck in the dark is her ship, stripped by the Compact over the years with
    her consent. That puts a face on the line *"cleaned up most of the scavenge"*
    [CD §1, §8.6; hook from prior draft].
  - She is the one voice allowed to explain plainly ("watch the child", "the stakes are
    for the flood").
- **First-met line:** *"You came down by ship too. Everyone does. Some of us don't go
  back."* (unverified)
- **Visual:** a weathered human woman in a patched surface dive-suit, the helmet long
  gone, her hair gone green-gold from the light. (unverified)
- **Defs to reuse:** `RM_PickedWreck`, `RM_SeaDiveHatch` (her ship came by the
  ship-only route [CD §0]).

## 3. Mechanism coverage

| mechanism | primary teacher | delivery | reinforcer |
|---|---|---|---|
| **weir form** [RP §4] | Dorrhul | the pre-built tended weir, the upstream-drop errand, a dredge hand | Maruvenn: a lapsed stake-line is the breach's first domino |
| **stake-lines** [CD §2.2, RP §4] | Maruvenn | one warning, then daily re-driving and weeding; thessmoss draws the line | Dorrhul: his farm sits inside her stakes |
| **vaulisk tell** [DP D4] | Bimmelo | the swerve; the tell said once | Sellowen: the never-breathing lamp is kept out of houses |
| **well practice** (was "lease practice") [LP §1.2, §4] | Vhessune | never sows a waning well; first to walk out to a new one; counts pallu | Tharukel: a pass sometimes closes a well in front of everyone [LP §1.3] |
| suulk decoy [DP D2] | Sellowen | the lone lit stake | — |
| undersurge tells [RP §2, DP D6] | Maruvenn | first mover off the inner bank | Dorrhul's hopper |
| sky / laden deck / lid-dark [DP D1, D8, D9] | Tharukel | behaviour as forecast; the pane-count question | Vhessune |
| designed absence [CD §8.6] | Aldra Sohm | her wreck | — |

## 4. Collisions, ambiguities, questions for the sitting

**Name check.** I ran `git grep -i -w` over the whole repo on 2026-10-29 (excluding
`conversations/`):

- **Exact matches:** none for Vhessune, Tharukel, Maruvenn, Dorrhul, Bimmelo, Sellowen,
  Aldra, Nine-Well Bank, Low Lantern or Farwake. The only exact hits for "Sohm" are inside
  two binary PNG files under `_artsrc`/`ArtIncoming`, which is noise.
- **Near-collisions** (stem searches over `src/` and `design/Jawa/bridge/`):
  - ⚠️ **Vhessune** shares the *vhess-* stem with `vhessa` (a Cracked Lands fish,
    `RUT_CrackedLandsFish_Items.xml`) and with `RUT_Vhessk` (a race). The names differ,
    but they look and sound alike.
  - ⚠️ **Farwake** is close to `RM_Farwick`, a Twilight plant on the same floor.
  - ⚠️ **Dorrhul** looks and sounds like `RM_Dorrak`, an RM creature
    (`src/RimMandrake/BlueDesert/Defs/ThingDefs_Races/RM_BlueDesertFauna.xml`). A rename is
    suggested, not forced.
  - The sitting can rename any of them.
- **Star Wars canon:** none of these names is a canon name as far as I know. Measured
  2026-10-29 on the Wookieepedia search API: all seven names plus Farwake, Nine-Well and
  Low Lantern returned no canon match (control searches 'Quarren' and 'Nien Nunb' did
  return results). The one near look-alike is Bimmelo next to 'Bimm' (a Legends species).

**Questions for the sitting:**

1. **Lease practice → well practice.** The brief named "lease practice" as a mechanism,
   but the 2026-09-27 ruling removed leases. Is "well practice" (live on lent light, move
   on with it) the right replacement, or should the slot go?
2. **Who carries the Inhabited trade role, if anyone?** Ordinary goods only. Light is
   never sold.
3. **Keep the seventh (Aldra Sohm)?** Or cut to six and let the biome teach without
   words?
4. **Three districts or one?** The three holdings are districts of one per-tile place.
   Is that right, or one holding for all seven? Repetition rule: do the same seven named
   people, and Aldra's one wreck, repeat on every diveable tile, or is there a per-tile draw?
5. **The child's micro-quest** walks the player past the vaulisk behind a nine-year-old.
   Keep it, soften it, or keep only the swerve?
6. **Dorrhul's race:** Herglic (this sheet) or Quarren (§9.3)?
7. **Where the cast goes once blessed:** into `design/Jawa/bridge/INHABITED_CAST_DEEPWATER.md`
   as place THE BOTTOM, with the XML regenerated by `cast_to_xml.py` [CD §9.3]. Nothing
   is filed or built from this sheet until he says so.
