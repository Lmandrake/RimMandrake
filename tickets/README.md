# Tickets

One markdown file per ticket (`RIM-<n>.md`), with git as the history. Every Lodestar project has
tickets (decision D30, 2026-10-21). File one from any directory, in one line:

    python3 ~/dev/Lodestar/bin/ticket.py new --project rimmaster --type build "title"

Types: `build` (make the project or its process better), `bug` (`--likely-fix "..."`), `repair`
(ongoing repair or upgrade), `action` (a dated real-world action: `--due YYYY-MM-DD`), `note`.
Work them with `ticket list|show|move|close|drop|edit|link|need|inbox --project rimmaster`; another
project asks for work with `ticket need --from <it> --to rimmaster "..."`. Mail-born obligations stay in
the Reckoning, never here. Full reference: `~/dev/Lodestar/docs/tickets/SKILL.md`.

This repo pushes to **github.com**: no employer text here (names, mail subjects, employer specifics). The tool
refuses employer markers; pass its private flag to file a sensitive ticket in its private overlay instead.

Ids are allocated by the tool (never by hand). Do not edit `INDEX.md`; it is generated.
