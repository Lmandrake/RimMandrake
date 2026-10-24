# FAUNA_INSTALL_CHECK_RENDER_IS_JUDGED

`fauna_drive.py install` (src/RimMandrake/Utils/art_eval/fauna_drive.py, cmd_install) copies whatever
`job_png("arteval_<DEF>_<tag>_<face>")` holds NOW and installs it. It never checks that this file is the picture the
pipeline ACCEPTed: the candidate decision record carries `source_sha256` per facing, but install does not compare it
with the render's sha. If an artpipe job of the same id is re-rendered after judging (refiled row, daemon retry), an
unjudged picture is installed under a "pipeline ACCEPT + head-to-head B" reason.

Failing-test sketch: candidate decision with source_sha256.south = X; render file sha = Y != X; install must refuse.
Fix direction: in cmd_install, refuse a face whose job_png sha differs from cand["source_sha256"][face] (refuse when
the record has no shas, too). Found by full-file review of fauna_drive.py (FOUNDRY 2026-10-24).
