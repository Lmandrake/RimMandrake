# BOUNDARY: pages_index, the line that links the kept pages, Design Version 0.1.0

Code: `src/RimMandrake/Utils/pages_index.py`, and its calls in `maturation_now.py`, `codebase_now.py` and `ops_watch.py` (`digest_md`).
Item: `RIMMANDRAKE_REMOVE_RELENTLESS_NOW_PAGE_CONSOLIDATE_MONITORS_HE_SAID_SLEEK`. Why the set is what it is: `plan.md` beside this file.

## ACCEPTS
- A key of `KEPT`: `fleet`, `maturation`, `detail`, `codebase`, `ops`.

## DOES NOT SURVIVE
- Another key: `KeyError` that names the key and the kept keys. A page that is not in `KEPT` gets no line; it must be added first.
- A kept page that moves on disk while `KEPT` still names its old path: the links go stale. The `--live` run of the selftest reads each
  page's head and turns red on it.

## PROMISES (tests of the same name in `src/RimMandrake/Utils/selftest_pages_index.py`)
- **crossref_names_every_other_page**: for each key, the markdown and HTML lines name every other kept page by its full Windows path
  and do not name the page itself; an unknown key is refused by name.
- **each_renderer_prints_the_line**: MATURATION_NOW, MATURATION_DETAIL, CODEBASE_NOW and the ops digest call the line with their own key.
- **fleet_config_links_the_others**: Augur's `D:\ClaudeWork\augur\config\dashboard.json` links MATURATION_NOW, CODEBASE_NOW and the ops
  digest (UNMEASURED when the config cannot be read).

## LIVE CHECK

- **live_pages_carry_the_line** (`--live` only): each RimMandrake page on disk names the other pages in its first 8000 characters.
