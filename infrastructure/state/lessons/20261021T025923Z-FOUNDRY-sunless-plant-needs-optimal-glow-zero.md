growMinGlow 0 alone does not make a plant live in the dark: the light factor is InverseLerp(growMinGlow, growOptimalGlow, glow), 0 at glow 0 while growOptimalGlow stays 1.0, so it is unlit and dies at 7.5 days. Sunless plants need BOTH growMinGlow 0 and growOptimalGlow 0 (vanilla Glowstool); the selftest refuses the half-set.
home: NONE
