# deployed/ — what the game is actually configured with

**Tier rule: this mirrors state that lives outside the repo.** Compiled mods, XML
patches, and key game config files copied out of the game install so they are
tracked, diffable and recoverable. `mods/` carries the `Jawa/` vs `RimMandrake/`
split; `config/` does not — a `ModsConfig.xml` belongs to the *install*, not to a
reuse category.

## `MODLIST.md` here is GENERATED. Never hand-write it.

Emitted by `harvest_log.py --emit-modlist` at the post-load moment, carrying the
game version, the capture time, the `observed/<stamp>/` it pairs with, the loadset
fingerprint, and the ordered `loadOrder | packageId | name | workshopId`.

**A hand-written record of a measured event is the defect class this project spent
a day removing.** The other tiers' modlists are statements of intent and are
hand-authored on purpose; this one is a record of the last runnable instantiation
actually tested, and a human typing into it makes it a claim rather than evidence.

If the def dump was not armed for that load, the emitter says so rather than
emitting a short list — a truncated list that looks complete is worse than an
absent one.

## The relationship to `src/`

`src/` is what we wrote. `deployed/` is what is installed. **They drift**, and the
drift is the point of tracking this tier: a `-` line in the deploy plan means
somebody hand-edited the deployed copy, and you `--pull` before you `--apply` or
you destroy their edit.

## What does NOT belong here

- **Source** → `src/`. This tier holds build outputs and copied config.
- **Third-party mod source** → `vendor/`.
- **Anything a running game produced** — logs, saves, def dumps → `observed/`.
