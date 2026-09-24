# SUMP_TAR_NASTINESS_1 — the Sump is nasty, and the tar gets on everything

Owner ruling 2026-09-24 (typed in chat, quoted in full on
`BIOME_NUISANCE_NORMALIZATION_1`): the Sump must be many kinds of nasty — stinky,
sticky, messy, little way to keep clean. This item is the Sump-NOW slice of that
principle; the planet-wide normalization is gated to the end
(`BIOME_NUISANCE_NORMALIZATION_1`).

## spec

Four mechanics, all RM-tier (`RM_TheSump` / its kit), feature-gated per the Mod
Settings law:

1. **Sticky tar onto any terrain surface** — an overlay/coating a source can apply
   to arbitrary terrain (belch events, beast surfacing, tracking). 🔑 Check what is
   already built before writing anything: the Fever Wood's `RM_ToxinSealant`
   (item + terrain, `RM_MapComponent_LivingRegrowth` gating on it) is the shipped
   terrain-coating precedent; also weigh filth-based vs TerrainDef-swap approaches
   against `RM_CompTimedTerrainBurn` (Sump kit) and the FlowWorks/liquids layer.
   `SUMP_TAR_BELCH_EVENT_1` consumes this mechanism — build them coherently.
2. **Tarred-pawn hediffs** — tar on yourself: move/work penalties, mood, hygiene-
   flavored stink, spreads filth, maybe flammability. Severity from exposure;
   removal is not free.
3. **Solvents** — cleaning items that remove tar from pawns (and coated terrain).
   A WEAK solvent is craftable in-biome from local materials; the STRONG solvent is
   deliberately NOT craftable here (the Poison Forest's acid line is the owner's
   example source — arrives by trade). Do not build the foreign side; leave the
   item hook (trade tag / def placeholder) for the normalization pass.
   ✅ REFINED same sitting (`SUMP_GASLIGHT_1` holds the verbatim rulings): the
   cleaner is an ACID and cleaning works BY the tar→green-gas reaction; the weak
   local acid renders from thrummel seepwax, ruled generous ("one raid should
   give you a lot. Not meant as a starvation mechanism"); the same acid gates
   vault extraction (`SUMP_TAR_VAULT_1`) and fuels the warbling lamp.
4. **The tar's own reward** — annoying materials pay: the sheet already calls the
   tar biologically rich; pick the reward with the roster docs (fuel/chemistry/
   preservation are the obvious axes) and make gathering it want the coping gear.

## verify

On a quicktest map: tar can be applied to a non-tar terrain and cleaned off it; a
pawn crossing gets the hediff and a weak solvent removes it; the weak solvent is
craftable from in-biome materials only; the reward loop yields something a colony
wants. All four toggleable in Mod Settings.

## criteria

A Sump colony is a constant, legible fight against the tar — losable by neglect,
priced in solvent, and worth it because the tar itself pays.

🔑 **Tuning law** (owner, 2026-09-24, typed; full quote on `SUMP_INHABITED_NOTES_1`):
the biome *rewards* players who enjoy their colony being dirty, messy,
idiosyncratic, and *frustrates* players who want neat, tidy, controlled. Tune every
knob here toward that — coping must be viable and characterful; full cleanliness
should be a losing fight, not an achievable state.
