# String ctor exception, Player.log line 76 (2026-10-02)
- Occurs during mod-metadata scan (before defs load, after dependency warnings), so it is an About.xml, not a def.
- Culprit: Steam workshop 3506645273 "Invisible Conduit Continued" (GlitchGoblin.InvisibleConduitCont),
  `D:`-side path ...\workshop\content\294100\3506645273\About\About.xml: `<author><li>zzz</li></author>` (author is a string).
- Donor mod, not ours; not fixed (report only). Effect: that mod's metadata fails to load (harmless to flowworks tier unless it is active).
- Scan of 1582 About.xml (Mods, workshop, src): this is the only string-field-with-children hit. Unrelated: workshop 2362707956 StopDropAndRoll About.xml is not well-formed.
