jawa/world_tile_export writes boolean CSV columns (waterCovered) as 0/1, not true/false; a parser comparing to 'true' reads every tile as dry. Accept 0/1/true/false and treat anything else as UNMEASURED.
home: rimworld-world-editing
