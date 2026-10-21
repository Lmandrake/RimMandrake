PerformanceOptimizer caches CurCelestialSunGlow(map) on a refreshTick; after the clock is set BACK the cache stays stale (the constant 0.7535 at five times was a cache, not the tidal lock). Read glow on fresh scratch maps or step the clock forward only.
home: skills/rimworld-debug-testing
