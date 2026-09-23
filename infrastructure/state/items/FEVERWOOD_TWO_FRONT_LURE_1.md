# FEVERWOOD_TWO_FRONT_LURE_1 — staked living bait, and a staggered two-raider arrival

## spec

Authority: `design/Jawa/worldbuilding/biomes/fever_wood_deep_and_mud_2026-09-23.md` §5, §6l.

**Owner, verbatim:** *"I like buildable lures. Both enemies like helpless prey chained down and
wounded. Spares you... but using one before they come also increases the likelihood that one or
both comes. And if only one comes, that's not so good... they might look around. Shouldn't both
come precisely at the same time. One comes, there's tension, then maybe the other arrives too."*

## the lure — a LIVING creature, three sources, and NO device

Owner ruled three of four options (`1+2+3`) and ⛔ **DECLINED the crafted decoy.**

| permitted | note |
|---|---|
| one of your **own tamed animals** | cost felt immediately and personally |
| a **prisoner** | mood/ideology weight is the point, not a flaw |
| a **nectar-beast from your herd** | most lore-exact — the ants already steal these alive |

🔴 **There is no bloodless option, and that exclusion IS the ruling.** A reusable device would
make the gamble routine and free. ⛔ Do not add a decoy, scent flask or substitute later "for
accessibility" — it was offered and refused.

⚠️ **Known exploit to design against:** a colony may breed cheap animals as ammunition. Either
the lure cares about prey **quality**, or the cheap route needs its own cost. Unset.

## the event shape — staggered, never simultaneous

| element | ruling |
|---|---|
| using a lure | **spares you** — the raiders go for the bait |
| cost of using one | **raises the chance a raid comes at all** |
| failure case | ⚠️ **if only ONE arrives it is bad** — it finishes the bait and *"they might look around"* |
| 🔴 timing | ⛔ **NEVER both at precisely the same time.** One arrives → tension → *maybe* the other |

🔑 **The stagger is the whole design.** A simultaneous double-arrival is a spectacle you watch;
a staggered one is a wager you live inside — you end up *hoping the second column shows up*,
which is a genuinely novel thing to want mid-raid.

## already built — do not rebuild

✅ **Mutual hostility needs one bool each.** `FactionDef.permanentEnemy` makes a faction hostile
to everyone *including another `permanentEnemy` faction* — verified against the real decompile in
`FEVER_WOOD_MECHANICS_1` F9. Setting it on both the ant swarm and the feralisk brood delivers
"hostile to the player AND each other" with no further XML.
✅ **Forcing a raid's arrival edge is achievable:** `IncidentParms.spawnCenter` can be preset by
the calling IncidentWorker before `PawnsArrivalModeWorker_EdgeWalkIn.TryResolveRaidSpawnCenter`
runs. That is how "from opposite directions" is delivered.
⚠️ **Target-preference weighting was NOT found as an exposed seam** — v1 ships plain
contact-hostility only. That is F9's own stated fallback, not a new gap.
⛔ Ban 2 stands: the ants are **never an existing faction**, no Geonosian tie — a wild swarm.

## not built

The two hidden FactionDefs, the LordJob/LordToil wiring, the staggered paired-arrival
IncidentWorker, and the lure building itself. ⚠️ F9's cited victim-finder
(`KidnapAIUtility.TryFindGoodKidnapVictim`) filters `Humanlike` and is **not reusable** for
animal targets — a new predicate is needed. `RUT_HaulPawnAndExit` already compiles.

## Watch out

⚠️ The sheet already names the player-side trick this serves (§7b): *"when both come at once,
open the gates between them and stand back."* The lure is how a player *engineers* that, so the
feature is incomplete if the two columns never actually meet.
