# Changelog

Version here must match `<modVersion>` in `About/About.xml`. Never deployed (`.md` is skipped by deploy_custom_mods.py).

## Unreleased

- A cord end that turns live or dead off screen is laid again at once (it kept its old cord until that part of the map was next redrawn).
- The same rule under every look and default look: a heap's junction boxes draw only the arms in use; a device's power strip points its lead the way the conduit comes, and gives way to the small box where a cut end shares its cell; a strip's plug points at water, a wall or a machine in its own cell; a box beside a pole brings its lead down to the pole's foot in one turn; a tied slack loop keeps off the far fitting's own run.
- Every cord end at a fitting leaves it on the fitting's line and slope, in crowded rooms too (in-game visit 1 read 19 of 399 joins off slope on the owner's review map; 0 of 393 now): one lay for every fitted end, run last, the live cut end's own. A junction box draws only the arms its cords leave by (two conduits side by side, a box in a crowd). A machine with conduit running under it is connected by that conduit, with no second lead. A conduit run that turns a corner into a machine enters its small box from the side. A machine or lamp standing at the tip of the box arm its lead leaves by takes the lead straight in. In a heap of power strips every strip is plugged into another by its own lead. A needless spur's spare loop leaves its box by an arm of its own.
- The setting "Live wires hanging out of walls drip sparks in bursts" is gone: no cord hangs out of a wall since the owner's ruling of 2026-11-16, and the switch did nothing.
- A texture asked for by a path no file system takes is refused with its text in the log instead of throwing inside the game's loader.
- A live cut end is laid to whatever stands close by: a machine, lamp, plate or box beside, ahead of or right behind the end (the lay had three rules of its own that left such cords kinked at their fitting). A join keeps off fittings it does not end at, never comes back over the one it left, and never coils at a doorway.
- A live cut end is laid by one rule and whips as a bend running out along a cord that cannot stretch: it leaves the conduit end straight, joins its cord by a round bend (broad where there is room), and never folds at the join. A short pigtail whips whole, right from its fitting; one with no room for a whipping tail lies still and only sparks (owner 2026-11-16). A lone conduit cell beside a machine ends facing away from that machine. A short lead whose fittings hold most of its cord takes its slack as a wire-tied loop.
- A run of conduit that ends inside a wall or rock enters the face exactly as a run through it does (plate, hole or outlet), with no loose or sparking end; power switch cords come in straight along the switch's stubs (owner 2026-11-16).
- Every cord leaving a plug (every wall face, device and pile plugs) or a strip plug leaves along the plug's own axis, read from one per-art stub table that the acceptance check also reads (owner 2026-11-16).
- One connection draws one cord by default: `cordsPerConnection` ships at 1, stays a slider (owner 2026-11-07).
- A live floor end's glow and thrown sparks follow its whipping tail (owner 2026-11-07).
- A fallen overhead wire lies in a slack S, so a cut span reads as down.
- Modern junctions draw the long power strip; a machine wired to conduit inside a wall draws its cord from the face; cords no longer fold into spikes.

## 1.0.0 — 2026-10-15 (release candidate, not published; repackaged 2026-10-16)

Package DLL: `Assemblies/RimMandrakeGimmeSomeSlack.dll` sha256 `5e523c88…cbce6fa3` (its `.srchash` `# dll:` line),
built from 2b215d4589. A DLL whose hash differs from this line is not the packaged one: repackage.

- 2026-10-16 repackage: every Harmony patch belongs to a Mod Settings feature, and a patch that fails to apply
  switches only its feature off (the player's own choice is kept in the settings file); Harmony applies after both
  settings files load; with Overhead lines off the anchor style menu no longer opens; a conduit end beside a powered
  device draws one cord, not a second sparking end.

- First packaged release: player-facing description, `About/Preview.png` (built by
  `src/RimMandrake/Utils/build_mod_previews.py`), modVersion, and Harmony plus all five expansions declared as requirements.
