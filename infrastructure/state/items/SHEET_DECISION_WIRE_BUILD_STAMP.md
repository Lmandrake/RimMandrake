## spec
enact.py's `ruled_snapshot` (93d799120b) infers which build of a sheet he clicked on as "the newest snapshot built at or
before his decidedAt". That is only true if he reloaded the page after every rebuild. A tab left open across a rebuild
resolves to the NEWER build, so the lane lookup falls back to today's lanes (the old behaviour; not worse, but the
protection is lost exactly when a superset rebuild happened mid-sitting). The decisions record carries no stamp of the
build the page was loaded from.

## failing test (sketch)
Snapshot A built 09:00, page loaded; rebuild B (Y moved lanes) at 09:30; his click at 10:00 on the page from A. Assert enact
resolves against A. Today: it picks B (built before the click), so the stale key check uses B's lanes.

## verify
Have art_sheet.py's page write the loaded snapshot's `built` (or a content hash) into each slot record (`seen_build`), and
have ruled_snapshot prefer it over the timestamp inference. Old records keep the inference.
