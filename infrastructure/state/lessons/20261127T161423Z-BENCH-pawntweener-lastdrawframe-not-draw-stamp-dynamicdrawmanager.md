PawnTweener.lastDrawFrame is not a draw stamp: DynamicDrawManager's cull pass calls DrawPos on every spawned pawn each frame (DynamicDrawManager.cs:276), on screen or not, so 'frames since lastDrawFrame' reads 0 for an off-screen pawn. Only PawnRenderer.silhouettePos (SetSilhouetteData at the end of RenderPawnAt) dates a real draw. Put the camera on the pawn and let a frame pass before reading its draw state.
item: RIMMANDRAKE_READ_FIX_78E6415836_WITH_FRESH_EYES
home: infrastructure/state/facts/instrument_traps.md
