# BUILD queue

## B10 Disable the turrets mod in ModsConfig
spec:     Remove `honeybadger.turrets` from `<activeMods>`. Owner's ruling — they
          clutter every outpost and the art is poor.
verify:   the packageId is absent from ModsConfig.xml
state:    ready

## B14 Build the 48 pawn kinds
spec:     48 kinds, 12 factions x 4 roles.
          BLOCKED ON CHAIN STEP 3: `weaponTags` and `apparelRequired` are a
          selection from the surviving item set and cannot be invented.
verify:   every weaponTags string appears on at least one live weapon def
state:    blocked

## B21 Retexture the turret bases
spec:     New PNGs for the four turret bases from the turrets mod.
state:    ready
