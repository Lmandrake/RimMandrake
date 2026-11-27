A bridge order call that waits on game ticks (jawa/order_pawn waitTicks=5000, timeoutSeconds=180) is cut at the modcheck session client's 30 s read limit, which leaves an UNKNOWN-outcome marker that refuses every later mutation on that game until rimbridge_client.py --reconcile resolves it. Split a long walk into orders of 20 s with stopOnArrival=true (UtinniPatches walk_onto_pad).
item: UTINNI_WORLDMAP_FLIGHT_ICON_1
home: skills/live-debugging-proof-harness
