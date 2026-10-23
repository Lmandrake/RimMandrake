# Under-coupler art regen candidates (2026-10-23, BENCH art helper) -- NOT INSTALLED

Owner: "Do make sure the couplers look like the art they're entering ... a swap in later of higher quality art if needed."

- gpt_question.md / gpt_review_v2.md -- GPT critique + per-look prompts (it saw all 8 images; gpt_packet/ is what it saw)
- raw/ -- Codex $imagegen masters (image 1 = grey shape guide from the installed sprite, guides/; image 2 = the look's RM_UniversalCargoTank texture)
- cand_profile/<Look>/ -- conformed 36x80 collar + 32x56 pipe, pipe = one averaged cross-section (identical at any stretch)
- cand_textured/<Look>/UnderPipe.png -- pipe keeping its painted along-axis wear (undistorted at a 0.5-cell run, smears at others)
- picks/<Look>/ -- the recommended set: Scrapper + Industrial = textured pipe; Modern + Futuristic = profile pipe; collars all from cand_profile
- composites_{profile,textured,picks}/ -- every fixture x look, left INSTALLED couplers vs right CANDIDATE, top 64 px/cell, bottom 4x
- zoom/{profile,textured}/ -- centre crops of the 4x row (JPG)
- validator.txt -- validate_sprite.py vs the installed slot (corner family excepted: the installed strips fail it too)
- masters used: Scrapper collar b / pipe b, Industrial collar b / pipe c, Modern a / a, Futuristic a / a

Install (after the live look) = copy picks/<Look>/*.png over Textures/RimMandrake/FlowWorks/Joins/<Look>/ through the art ledger.
