# RIMMANDRAKE_FIX_OFFLINE_DEF_MERGE_REPLACES_WHAT_GAME_APPENDS

Found in the source read of RIMMANDRAKE_REWRITE_SKILL_MODDING, 2026-11-23.

## spec

- `src/RimMandrake/Utils/def_inventory.py` `_merge_into` overwrites an inherited `<li>` list when the child declares the
  list. The 1.6 engine APPENDS each `<li>` child (`Verse/XmlInheritance.cs`, `RecursiveNodeCopyOverwriteElements`).
  `Inherit="False"` replaces the list. The tool and the engine agree on that case.
- Measured: parent comps [A] and child comps [B] give [B] in the tool. The engine gives [A, B].
- The result: wrong `comps`, `tools` and `lifeStageAges` in `animals.csv`, and in each generator that imports `def_inventory`
  (Armoury `gen_*.py`, `gen_megafauna_yield.py`, `fauna_normalization.py`).
- The comment above `INHERIT_MAX_DEPTH` in `def_inventory.py` and the docstring of `animal_inventory.py` state the false
  rule. That docstring also says that patches run after inheritance. They run before.
- First compare the fixed tool with a live capture. Then regenerate the outputs and read each diff.
- In the same change, remove the offline-scan warning about lists from `skills/rimworld-modding/SKILL.md` §1b.

## verify

Acceptance test, seen red on base `2239895533` (exit 1, first case). Expected: exit 0.

```
python3 -c "
import sys, xml.etree.ElementTree as E
sys.path.insert(0, 'src/RimMandrake/Utils')
import def_inventory as d
def run(child):
    p = E.fromstring('<T><c><li>A</li></c></T>'); d._merge_into(E.fromstring(child), p); return [x.text for x in p.find('c')]
ok = (run('<T><c><li>B</li></c></T>') == ['A', 'B'] and run('<T><c Inherit=\"False\"><li>B</li></c></T>') == ['B']
      and run('<T><c/></T>') == ['A'] and run('<T/>') == ['A'])
sys.exit(0 if ok else 1)"
```

## criteria

- The acceptance test exits 0. A selftest holds the same four cases.
- One real def (Muffalo: `AnimalThingBase` comps plus Shearable) has the same comp count in the tool and in a live capture.
