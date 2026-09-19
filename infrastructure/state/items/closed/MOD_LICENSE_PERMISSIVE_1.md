# MOD_LICENSE_PERMISSIVE_1

Owner, verbatim (2026-09-08): "Please create a ticket to add the most generous
re-use license to all our mods. We're not trying to control or make money,
we're providing a great experience."

## spec
- License: **CC0-1.0** (public-domain-equivalent dedication) — the most
  permissive standard license that still exists as a named, recognizable
  license; more generous than MIT/Apache (no attribution requirement) and
  clearer in intent than "public domain" (which isn't recognized everywhere).
  If the owner would rather explicitly name MIT or Unlicense instead, that's
  a one-word swap in whichever generator this produces — record the choice,
  don't block on it.
- Apply to every mod we author under `src/RimMandrake/`, `src/RimStarWars/`,
  `src/RimUtinni/` (NOT to absorbed/ported third-party donor content unless
  its own upstream license already permits redistribution under CC0 — check
  before touching anyone else's asset or def).
- A `LICENSE` file per mod folder (or one repo-root `LICENSE` plus a one-line
  pointer added to each mod's `About.xml` `<description>` — cheaper, pick
  whichever this repo's existing About.xml convention favors, there may
  already be a per-mod boilerplate block worth extending).
- ⚠️ Do NOT touch any `<!-- -->` XML comment without parsing the file
  afterward with `xml.etree.ElementTree` — see the 2026-09-08 lesson in
  `infrastructure/state/LESSONS_INBOX.md` about `--` inside comments
  silently breaking every one of these files for the live game.

## verify
```
PROVE   every mod folder we author has a LICENSE file (or documented
        equivalent) naming CC0-1.0, and every About.xml still parses
        (xml.etree.ElementTree.parse) after the edit
EXPECT  check_declarations.py output is unchanged (this is a metadata-only
        change, it must not touch loadAfter/modDependencies)
LIES    a repo-root LICENSE alone, with no per-mod file or pointer — Steam
        Workshop uploads a mod's own folder, not the repo root
```

## criteria
Done when every RimMandrake/RimStarWars/RimUtinni-authored mod folder
declares CC0-1.0 findably from inside that folder, third-party donor content
is left untouched, and every touched XML file still parses clean.
