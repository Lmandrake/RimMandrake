WildAnimalSpawner.CommonalityOfAnimalNow(kind, loc) is called with the map-edge ENTRY cell for ongoing wild spawns (SpawnRandomWildAnimalAt), and with random interior cells only during map generation. A postfix that gates a kind on what is near loc (plants, terrain, buildings) gates arrivals on the edge, not the map (TETCHIK_GLOWERGATE_WIDEN_EDGE_ENTRY).
home: rimworld-modding
