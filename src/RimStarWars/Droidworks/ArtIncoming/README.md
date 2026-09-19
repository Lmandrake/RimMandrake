# ArtIncoming — renders rescued from a mis-route, not yet a def's art

## misrouted_droid_from_mycoidcolossus_{south,east,north}.png

A three-facing droid render that was installed into
`src/RimUtinni/MycoidColossusArtOverride/` by the bulk art install `cea007c3a`
("install every gate-passed render awaiting verdict, 95 stems"). It is a rusty
bipedal droid — antenna head, exposed cabling, pincer hands — and it was binding
to the vorrugath / mycoid colossus texPath, so that creature rendered as a droid
in game.

The owner caught it on the size re-judge sheet, 2026-09-19, verbatim:
> "What IS this graphic? Is this wired correctly? It's more like something we
> should keep for the Droidworks."

Kept here on his word rather than deleted — a real render is never thrown away as
cleanup. It is NOT wired to any def: no texPath in this folder resolves, by
design. Whoever gives it a home moves it to a real `Textures/` path under a def
that wants it.
