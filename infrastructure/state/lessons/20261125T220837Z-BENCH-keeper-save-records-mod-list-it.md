A keeper save records the mod list it was made on, and the game refuses a load that misses any of them (save.missing_mods). The Pyrelands review keeper of 2026-10-15 holds VFE, Alpha Biomes/Animals and Pyrelands Mechanics, which no current small list loads. So a live proof that needs a review save builds it on the list it runs on (human_review.py --build --load <site fixture> --save), and the site fixture's own meta modIds name the tier that can load it (read them with a structured parse of <meta>, not a text scan).
item: AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE
home: skills/rimworld-live-review
