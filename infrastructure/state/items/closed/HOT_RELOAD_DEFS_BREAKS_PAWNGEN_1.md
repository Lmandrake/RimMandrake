# HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1

Measured live 2026-09-03 on the 589-mod stack, quicktest map (the sea-beast review
map), game UP the whole time.

## spec

`jawa/hot_reload_defs` was called to pick up a mod added to ModsConfig after launch.
It **RAN** — the first time this has been observed through the bridge. The bridge went
unresponsive for ~5 minutes (a 589-mod def reload is most of a cold load's def phase),
then answered normally again.

After it, **every pawn spawn fails**:

```
jawa/spawn_pawn  Muffalo      none     ok=False  NullReferenceException
                 Hare         none     ok=False  NullReferenceException
                 Colonist     none     ok=False  NullReferenceException
                 Tribesperson player   ok=False  NullReferenceException
                 Villager     player   ok=False  NullReferenceException
```

Animals too, faction or none — so it is not the kind, the faction or the mod.
Vanilla's OWN debug action gives the real message that `jawa/spawn_pawn` swallows as
a bare NRE:

```
execute_debug_action  Actions\Spawn Pawn...\Colonist
  -> KeyNotFoundException: The given key 'RimWorld.HairDef' was not present
     in the dictionary.
```

### 🔑 It is NOT the def database

Checked immediately after, same connection:

```
HairDef/Shaved      found=1     BodyTypeDef/Male   found=1
HairDef/Bald        found=1     ThingDef/Human     found=1
                                ThingDef/Muffalo   found=1
```

The defs are all there. What is missing is an entry in a **Type-keyed dictionary**
that pawn generation walks — the reload rebuilt the databases and left that index
short. Naming the exact cache is the work of this item; the observable above is
certain.

### Before/after evidence

The sea-beast review agent spawned **54 pawns successfully on this same map at 19:19**,
before the reload. The reload is the only intervening event. ⚠️ **One run, not
repeated** — repeating it costs another 5-minute hang and another broken game, so treat
the CAUSE as strongly indicated rather than proven twice.

### Why it matters

`jawa/hot_reload_defs` is documented as the intended route for tier-b XML iteration
(owner ruling 2026-09-01, `skills/rimworld-modding/SKILL.md` §2). On a full mod list it
is currently a game-killer: it costs 5 minutes, hangs the bridge throughout, and
leaves a process that answers every read correctly while being unable to make a
single pawn. **Nothing reports that it broke** — the game looks healthy
(`programState: Playing`, `playable: true`, `mapDataReady: true`) until something
tries to generate a pawn.

### Also learned, worth keeping

`hot_reload_defs` does **not** pick up a mod added to `ModsConfig.xml` after launch.
ModsConfig is read at startup; the reload re-runs `LoadAllActiveMods` over the mod set
the PROCESS has, not the file's. A mod deployed and activated mid-session still needs
a restart.

## verify

Name the Type-keyed dictionary (a `DefDatabase`/`GenDefDatabase` index, or a style-item
cache) that loses `HairDef` across `HotReloadDefs`, from the 1.6 source. Then decide:
does `hot_reload_defs` get a loud refusal above some mod count, a repair call after it,
or a warning in its own description? 🔴 Re-test on the **minimal tier**, where a broken
game costs 22 seconds — never on the full list.

## criteria

The mechanism is named from source, not guessed; and `jawa/hot_reload_defs` either
repairs the index itself or refuses/warns loudly enough that nobody calls it on a full
stack expecting a working game afterwards.

## resolved — already met, no new work needed

Picked up 2026-09-03 from the FOUNDRY queue and found already done: the SAME commit
that filed this item (`f3bad330`) also retired the tool. `src/RimMandrake/Utils/rimbridge_client.py`'s
`RETIRED_TOOLS["jawa/hot_reload_defs"]` refuses the call outright with the exact
evidence this item recorded, names the sanctioned replacement (deploy → minimal-list
restart, 22s → `jawa/get_defs`), and requires `RIMBRIDGE_ALLOW_RETIRED=jawa/hot_reload_defs`
to override. `skills/rimworld-modding/SKILL.md` §2 carries the same ruling.
`infrastructure/VALIDATION_LADDER.md` was updated in the same commit.

The **"refuses/warns loudly" branch of criteria is met** — the owner's ruling (quoted
in the skill file) went further than repair-or-warn and retired the capability
outright, which supersedes the need to name the exact Type-keyed dictionary from
source. Naming it would only matter if someone meant to fix hot-reload rather than
retire it, and the owner ruled the opposite. Closing with no new commit; verified by
reading `rimbridge_client.py` directly, not by re-running the call.
