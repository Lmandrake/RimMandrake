A spend meter that only reads transcripts under the arena root is blind to helpers that get a fresh HOME in a tempdir and are rmtree'd (arena testers): the verdict still DECIDEs with blocking=[]. Probe a meter by injecting spend where each helper really writes, not where the meter looks.
home: design/RimMandrake/architecture_switch_harness_2026-10-29.md
