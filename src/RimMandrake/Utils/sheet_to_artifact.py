#!/usr/bin/env python3
"""sheet_to_artifact.py — turn a served review sheet into a publishable
claude.ai artifact page, so the owner can review it from his PHONE.

WHY THIS EXISTS
    `serve_sheet.py` is the ruled default and stays the default: it binds a
    local port and opens his browser on a tokened URL. That URL is useless off
    this machine. When the review has to happen on a phone, the sheet has to
    become an artifact, and an artifact has no sidecar to POST to.

WHAT IT DOES
    The sheet template already has THREE persistence backends behind one
    interface (`load()` / `save(ops)`): ServerBackend, FileBackend,
    LocalBackend. This adds a FOURTH — ArtifactDbBackend — writing to the
    artifact's own `db` capability, and wires it as the FIRST choice at boot
    so a phone gets it and this machine still gets the sidecar.

    It writes one db document per touched row, in exactly the shape
    `merge_artifact_db.py` already reads back:

        decisions/<safe-id>  ->  {rowId, rec, savedAt, savedBy}

    so the remote sitting folds into the repo's decisions.json with the
    existing tool. Nothing new to invent on the way home.

🔴 The page is NOT the record. The repo's decisions.json is. A remote sitting
   is merged back with `merge_artifact_db.py --apply`, which REFUSES an empty
   dump — an empty merge must never read as "reviewed".

⚠️  `savedBy` is stamped `artifact-db`, never the sidecar's own stamp, and
    never `review-sheet-page`. Provenance stays honest: a consumer can always
    tell a phone sitting from a desk sitting from a pre-fill.

    python3 sheet_to_artifact.py --sheet S.html --title "Name" --out OUT.html
"""
import argparse
import os
import re
import sys

# The db path grammar admits letters, digits and _ - . ~ : @ + only. Row ids
# here are defNames and job ids, but never assume: anything else is escaped to
# a hex code, which keeps the mapping injective. The TRUE row id rides in the
# document body, which is what merge_artifact_db.py actually reads.
BACKEND_JS = r"""
/* ─────────────────────────────────────────────────────────────────────────────────────
   ArtifactDbBackend — persistence for a sheet published as a claude.ai artifact.

   Fourth backend, same interface as the other three: load() and save(ops).
   There is no sidecar on a phone, so the artifact's own db capability holds the
   verdicts until merge_artifact_db.py folds them back into the repo's decisions
   file. One document per TOUCHED row; rows nobody touched are never written, which
   is what keeps the merge per-row instead of all-or-nothing.
   ───────────────────────────────────────────────────────────────────────────────── */
class ArtifactDbBackend {
  constructor(db) { this.db = db; this.name = 'artifact-db'; this.writes = 0; }

  /* null when this view cannot run db — not served, not granted, or failed to
     load, deliberately indistinguishable. The caller falls through to the next
     backend, exactly as if we were never here. */
  static async connect() {
    try {
      if (!window.claude || typeof window.claude.use !== 'function') return null;
      const db = await window.claude.use('db');
      return db ? new ArtifactDbBackend(db) : null;
    } catch (e) { return null; }
  }

  /* A db path segment admits letters, digits and _ - . ~ : @ + only. Escape
     everything else rather than trusting row ids to be tame.

     '-' is deliberately EXCLUDED from the pass-through set below, even
     though the db grammar allows it: the escape marker itself is "-x" plus
     4 hex digits, all drawn from the allowed alphabet, so a row id that
     already CONTAINS a literal "-x" + 4 hex digits (e.g. "foo-x0020bar")
     would pass through unescaped and collide with the escaped form of a
     DIFFERENT row id that has a disallowed char at that spot (e.g.
     "foo bar" -> "foo-x0020bar") — two distinct rows would `.set()` the
     same document path and one decision would silently overwrite the
     other. Escaping every literal '-' too means "-x" can only ever appear
     as a real escape sequence, which is what actually keeps this
     injective, not merely what the comment claimed. */
  static key(rowId) {
    return String(rowId).replace(/[^A-Za-z0-9_.~:@+]/g, c =>
      '-x' + c.charCodeAt(0).toString(16).padStart(4, '0'));
  }

  async load() {
    frozen = false;
    const snap = await this.db.collection('decisions').get();
    const out = {};
    let n = 0;
    snap.docs.forEach(d => {
      const body = d.data();
      if (body && body.rowId && body.rec) { out[body.rowId] = body.rec; n++; }
    });
    this.writes = n;
    return out;
  }

  /* One write at a time per document, awaited — the db contract is explicit
     that overlapping writes to one document only make each one slower. */
  async save(ops) {
    const at = new Date().toISOString();
    for (const [rowId, rec] of Object.entries(ops)) {
      await this.db.doc('decisions/' + ArtifactDbBackend.key(rowId))
        .set({ rowId, rec, savedAt: at, savedBy: 'artifact-db' });
    }
    this.writes += Object.keys(ops).length;
    return { writeCount: this.writes, savedAt: at };
  }

  get where() { return "this artifact's own store — merged back with merge_artifact_db.py"; }
}
"""

BOOT_JS = r"""  /* An artifact view has no sidecar to POST to, so db wins when it is there.
     On this machine claude.use is absent and we fall straight through to the
     sidecar, which stays the ruled default. */
  const ARTDB = await ArtifactDbBackend.connect();
  if (ARTDB) {
    backend = ARTDB;
    el('dpath').textContent = "this artifact's own store";
    el('pathwhy').textContent =
      'saved as you go — folded back into the repo with merge_artifact_db.py';
    el('pathbar').classList.remove('hide');
    try { loaded = await backend.load(); }
    catch (e) { showErr('Could not read this artifact\'s saved decisions: ' + e.message); }
  } else if (SIDECAR && SIDECAR.mode === 'server') {"""


def patch(html: str, title: str) -> str:
    """Strip the document wrapper the artifact platform supplies, retitle, and
    splice the fourth backend in. Every anchor is asserted: a silent no-op here
    ships a page whose buttons look wired and save nothing, which is the exact
    defect the review-sheets skill spends a section on."""
    # The platform wraps the file in its own doctype/html/head/body.
    m = re.search(r"<head>(.*?)</head>.*?<body[^>]*>(.*)</body>", html, re.S | re.I)
    if not m:
        sys.exit("FAIL: could not find <head>/<body> — is this a review sheet?")
    head, body = m.group(1), m.group(2)

    styles = "\n".join(re.findall(r"<style.*?</style>", head, re.S | re.I))
    if not styles:
        sys.exit("FAIL: no <style> block in <head> — refusing to ship an unstyled sheet.")

    if "class ServerBackend {" not in body:
        sys.exit("FAIL: ServerBackend not found — the template changed shape.")
    body = body.replace("class ServerBackend {", BACKEND_JS.strip() + "\n\nclass ServerBackend {", 1)

    anchor = "  if (SIDECAR && SIDECAR.mode === 'server') {"
    if body.count(anchor) != 1:
        sys.exit(f"FAIL: backend-selection anchor appears {body.count(anchor)}x, expected exactly 1.")
    body = body.replace(anchor, BOOT_JS, 1)

    return f"<title>{title}</title>\n{styles}\n{body}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet", required=True, help="the served review sheet .html")
    ap.add_argument("--title", required=True, help="the artifact's name (2-4 words)")
    ap.add_argument("--out", required=True, help="where to write the publishable page")
    a = ap.parse_args()

    src = open(a.sheet, encoding="utf-8").read()
    out = patch(src, a.title)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"{a.out}  {len(out):,} bytes  (from {os.path.basename(a.sheet)})")


if __name__ == "__main__":
    main()
