## spec
The Empire's vessel is Royalty's, and its vocabulary comes with it: `royalFavorLabel` is
literally `honor`, and ~140 strings under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Royalty\Languages\English\Keyed\`
say *royal*, *title*, *bestowing*, *stellarch*.

Two parts:
1. Patch `royalFavorLabel` on `FactionDef[defName="Empire"]` to the Imperial word.
   ⭐ **Also patch `royalFavorIconPath`** or the honour icon stays a royal crest.
2. Add our own `Languages/English/Keyed/` file under `src/Jawa/Jawa_Patches/` overriding the
   Royalty keys a player actually sees. **Do not translate all ~140** — only those reachable
   given `EMPIRE_GAP_AUDIT.md` §3: the titles, permits and bestowing quests are DARK, so
   most of those strings never render. Enumerate what renders first, then override that.

⛔ Not a worldgen-deadline item. Keyed strings are read at load, every load.

## verify
`grep -rn "royalFavorLabel" src/` returns a hit in `GalacticEmpire.xml`, and the new Keyed
file exists with a bounded, enumerated key list rather than a bulk copy.

## criteria
No screen the player reaches calls the Galactic Empire's currency *honor* or its officers
*royalty*.
