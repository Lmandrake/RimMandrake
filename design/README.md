# design/ — what we intend to exist

**Tier rule: this is intent, not fact.** Everything here describes something we
want, have specified, or have reasoned about. Nothing here is evidence that the
game does anything. If a document's claim can only be settled by looking at a
running game or a shipped file, its *conclusion* belongs in `observed/` or
`deployed/` and only its *reasoning* belongs here.

## The split

| | |
|---|---|
| `design/Jawa/` | this campaign. Fiction, the gravship, factions, the xenotype, art briefs. Worthless in another playthrough. |
| `design/RimMandrake/` | the method, not the content. `faction_authoring_mechanism.md` — how to author a faction — is generic; `faction_roster_v2.md` — ten Star Wars factions — is not. |

**The promotion test, the owner's words:** *"Am I likely to want this in a totally
unrelated playthrough, or will I have to fundamentally remake it — not just
reconfigure it?"* Reconfigure → `RimMandrake/`. Remake → `Jawa/`.

⚠️ **When unsure, put it in `Jawa/`.** Promoting a doc later is a `git mv`;
discovering that a "generic" doc silently assumed Star Wars is a debugging
session. The cheap error is the recoverable one.

## What does NOT belong here

- **Measurements.** A faction count read from a save is `observed/`.
- **Mod wisdom** — how to operate somebody else's mod → `vendor/wisdom/`.
- **Material we did not write**, even summarised → `research/`.
- **Anything a machine generates.** If a script writes it, it is not design.

The planned `MODLIST.md` here is **hand-authored**: a statement of which mods this tier's
documents assume exist. It changes slowly, by hand, in the commit that adds the
dependency. It is not a record of anything that ran.

⏳ **`MODLIST.md` DOES NOT EXIST YET.** This section describes what it will be,
not what is here — verified 2026-08-13, `find` returns nothing. **Do not cite it
as though it exists**; that is the same silent-failure shape as a `loadAfter`
naming a mod that was never installed. Build it or delete this paragraph.
