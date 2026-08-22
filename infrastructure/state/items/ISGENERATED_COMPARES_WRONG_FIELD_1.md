## spec
`jawa/faction_name_get` reports a faction as wearing a GENERATED name when its
`currentName` differs from its **`defLabel`**. That is the wrong comparison: a faction with a
`fixedName` is *supposed* to differ from its label — that is what a reskin is.

⇒ The flag fires hardest on the factions that are **correct**.

Measured on a live quicktest world, 578 mods:

    tool: "24 faction(s) are wearing a GENERATED name."

    wearing their own defFixedName  -> 9   FALSE POSITIVES
    no defFixedName at all          -> 15  genuinely generated

The nine: `Empire`, `Jawa_Junkers`, `PirateYttakin`, `DV_PirateKeshig`,
`AG_XenohumanPirates`, `CannibalPirate`, `BS_Muspelheim`, `BS_Niflheim`, `BS_OgreFaction`.

## why it matters more than a wrong number
`FACTION_NAMES_ARE_GENERATED_1` tells a seat to run `faction_name_set action=clear` against
whatever `generatedCount` reports. ⛔ **Driven off this flag, that repair would clear nine
names that were deliberately authored**, including the Galactic Empire's and the Junkers'.
The instrument does not merely over-report; it aims the fix at the wrong targets.

## the fix
Compare `currentName` against `defFixedName` when the def carries one, and fall back to
`defLabel` only where it does not. Report the two populations separately rather than summing
them into one `generatedCount`.

## criteria
On a world where all twelve authored factions wear their `fixedName`,
`jawa/faction_name_get` reports **0** of them as generated, and still reports the fifteen
third-party factions that carry no `fixedName`.

Evidence: `infrastructure/state/observed/2026-08-21/faction_names/`.
Register: add to `infrastructure/state/BUILDABLE.md` alongside the other instruments caught
returning a confident wrong number.
