A bulk art generator with an install verb (biome_worldfaces.py install) re-installs every face it owns with a blanket --owner-said, so a rerun silently reverts a face the owner later picked from a different generator. When another tool takes over a face, make the old generator skip it in code (PICKED_ELSEWHERE in biome_worldfaces.py, 2026-10-24), not just in a note.
home: NONE
