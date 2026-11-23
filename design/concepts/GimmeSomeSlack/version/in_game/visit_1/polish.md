# GimmeSomeSlack 0.2.0 in-game visit 1: polish (a record; nobody fixes these)

- Core/StubJoinAudit.cs Joins: a wall lamp's own lead that ends in front of a wall plate is read as that plate's cord (25 deg off); a lamp base is stubless art. His review map has no such pair, so sc_stub_joins never meets it.
- human_review.py --fresh-map on the full list asks jawa/map_info while the new map is still in a long event and stops; --build on the map that then stands works.
- sc_walk's observes text names a 20 ms per-rewire frame time the runner's journal does not record (sc_rewire_cost reads it).
- ConduitStyleProbe clookicons:...:open opens a FloatMenu that closes at once when the game window is not under the mouse; nothing reads it any more.
