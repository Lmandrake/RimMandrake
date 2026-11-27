# WB-item-RIMMANDRAKE-SHRINK-STEVEDESKTOP-CLONES-FOUR-FILL-ITS-EIGHTY-GIG-20261127-051516

| ticket | class | outcome | commit | live reading |
|---|---|---|---|---|
| RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_EIGHTY_GIG | REAL | fixed | 87c697b3a3, 590a483acd, a520c99c12 (polish) | rm-pool-room.service 21:28 PST 2026-11-26: ROOM, 2 clones + 15 more = 17 runs |

Cause: the live promise aged because rm_pool_room.py sized a new clone by the pool's own clones. An empty pool read
COULD_NOT_LOOK (17:57), and a pool that held only a parked full warm spare (5.1 GB) read SHORT, 6 runs (18:58-20:58).
Fix: a new clone is sized by a slim checkout of store.git's HEAD (1.48 GB) when no slim clone is there. Owed check
trees are sized by a full checkout (5.07 GB). An empty pool loses the +1. selftest_rm_pool_room: red on the old code
(4, then 2 after the fresh reader), green after. One group; done.
