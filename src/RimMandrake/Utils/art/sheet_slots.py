#!/usr/bin/env python3
"""sheet_slots.py — what each picture on a biome art sheet IS FOR: the slot vocabulary (DESIGN 2026-10-10 §3.1).

A SLOT is one picture the game draws for a subject, read from the live def dump — never inferred from a file name:

  animal  adult (· male when the kind has femaleGraphicData)   last lifeStages[].bodyGraphicData        required
          adult · female                                       last lifeStages[].femaleGraphicData      when present
          young · <lifeStageDef> (· female)                    an earlier stage whose texPath differs   when it differs
          flying (· male / · female)                           PawnKindDef flip-book prefix(es)          when present
          swimming (· female)                                  lifeStages[].swimmingGraphicData          when present
          alternate (random pool)                              PawnKindDef alternateGraphics             pool
  plant   grown (a POOL when graphicClass is Graphic_Random)    graphicData                               required
          young (immature) / leafless                          plant.immatureGraphicPath / leafless...   when present
  item    item — or "catch item" for a <X>Catch row            graphicData                               required

A texPath shared by several slots (a young stage drawing the adult's picture) is ONE lane labelled by its most senior
slot, with "also used by" naming the rest. Renders matched only by NAME belong to no slot until they are assigned
(UNASSIGNED); a catch row shows its creature's renders as a non-pickable REFERENCE lane.

Pure functions over dump dicts; gametex.py stores their output per def (deftex schema 3).
"""
from __future__ import annotations

import hashlib
import re

SEX_LABEL = {"": "", "male": " · MALE", "female": " · FEMALE"}
STAGE_WORD = {"AnimalBaby": "baby", "AnimalBabyTiny": "hatchling", "AnimalJuvenile": "juvenile",
              "HumanlikeBaby": "baby", "HumanlikeChild": "child"}
# a render's job name says what it is a picture OF; used only as a HINT on an unassigned render (never auto-assigns)
HINTS = (("flying", re.compile(r"(?:^|[_\s])(?:fly|flight|flying)(?:_|$)", re.I), "flight frame — not a body"),
         ("young", re.compile(r"(?<![a-z])(juv(?:enile)?|young|baby|calf|pup|chick|hatchling|larva|immature|_j)(?![a-z])", re.I), "young"),
         ("female", re.compile(r"(?<![a-z])(female|_f)(?![a-z])", re.I), "female"),
         ("male", re.compile(r"(?<![a-z])(male|_m)(?![a-z])", re.I), "male"),
         ("swimming", re.compile(r"swim", re.I), "swimming"),
         ("catch", re.compile(r"catch|fillet|carcass|dead", re.I), "catch item"))
NONBODY = re.compile(r"dess?icc?ated|_corpse$|skeleton", re.I)


def _tp(gd) -> str | None:
    if isinstance(gd, dict):
        t = gd.get("texPath")
        return t if isinstance(t, str) and t else None
    return gd if isinstance(gd, str) and gd else None


def _is_random(gd) -> bool:
    return isinstance(gd, dict) and str(gd.get("graphicClass") or "").endswith(("Graphic_Random", "Graphic_Collection"))


def slot(def_name, field, kind, label, res, *, pool=False, required=False, stage=None, sex="") -> dict:
    return {"id": f"{def_name}/{field}", "kind": kind, "label": label, "res": res, "pool": pool, "required": required,
            "stage": stage, "sex": sex}


def derive(def_name: str, fields: dict, is_: dict, kinds: list[tuple[str, dict]], catch: bool = False) -> list[dict]:
    """Slots for ThingDef DEF_NAME (dump `fields`, `is`), with its PawnKindDefs [(defName, fields)] for a pawn."""
    out: list[dict] = []
    is_ = is_ or {}
    if is_.get("pawn"):
        ages = []
        race = fields.get("race") if isinstance(fields.get("race"), dict) else {}
        for a in race.get("lifeStageAges") or []:
            ages.append(a.get("def") if isinstance(a, dict) else None)
        for kn, kf in kinds:
            stages = [s for s in (kf.get("lifeStages") or []) if isinstance(s, dict)]
            if not stages:
                continue
            last = len(stages) - 1
            adult_b, adult_f = _tp(stages[last].get("bodyGraphicData")), _tp(stages[last].get("femaleGraphicData"))
            gendered = bool(adult_f and adult_f != adult_b)
            for i in range(last, -1, -1):
                st = stages[i]
                sdef = ages[i] if i < len(ages) else None
                word = "ADULT" if i == last else "YOUNG · " + (STAGE_WORD.get(sdef or "", "") or (sdef or f"stage {i + 1}")).upper()
                for fld, sex in (("bodyGraphicData", "male" if gendered else ""), ("femaleGraphicData", "female")):
                    t = _tp(st.get(fld))
                    if not t or NONBODY.search(t) or (sex == "female" and not gendered):
                        continue
                    if i != last and t in (adult_b, adult_f):
                        continue             # a young stage drawing the adult picture: a shared lane, not its own slot
                    kind = ("adult" if i == last else "young") + ("_female" if sex == "female" else "")
                    out.append(slot(kn, f"lifeStages[{i}].{fld}", kind, word + SEX_LABEL[sex], t,
                                    required=(i == last), stage=sdef, sex=sex))
                for fld, sex in (("swimmingGraphicData", "male" if gendered else ""), ("femaleSwimmingGraphicData", "female")):
                    t = _tp(st.get(fld))
                    if t and i == last:
                        out.append(slot(kn, f"lifeStages[{i}].{fld}", "swimming" + ("_female" if sex == "female" else ""),
                                        "SWIMMING" + SEX_LABEL[sex], t, stage=sdef, sex=sex))
            pm, pf = kf.get("flyingAnimationFramePathPrefix"), kf.get("flyingAnimationFramePathPrefixFemale")
            if isinstance(pm, str) and pm:
                sx = "male" if isinstance(pf, str) and pf else ""
                out.append(slot(kn, "flyingAnimationFramePathPrefix", "flying", "FLYING" + SEX_LABEL[sx], "_flip:" + pm, sex=sx))
            if isinstance(pf, str) and pf:
                out.append(slot(kn, "flyingAnimationFramePathPrefixFemale", "flying_female", "FLYING · FEMALE", "_flip:" + pf,
                                sex="female"))
            alts = [a.get("texPath") for a in kf.get("alternateGraphics") or [] if isinstance(a, dict) and a.get("texPath")]
            for j, t in enumerate(alts):
                out.append(slot(kn, f"alternateGraphics[{j}]", "alternate", "ADULT · ALTERNATE (random pool)", t, pool=True))
            if alts:
                for s in out:
                    if s["kind"] in ("adult", "adult_female") and s["id"].startswith(kn + "/"):
                        s["pool"] = True
    else:
        gd = fields.get("graphicData")
        t = _tp(gd)
        if is_.get("plant"):
            if t:
                out.append(slot(def_name, "graphicData", "grown", "PLANT · GROWN" + (" (random pool)" if _is_random(gd) else ""),
                                t, pool=_is_random(gd), required=True))
            pl = fields.get("plant") if isinstance(fields.get("plant"), dict) else {}
            for fld, kind, lab in (("immatureGraphicPath", "plant_young", "PLANT · YOUNG (immature)"),
                                   ("leaflessGraphicPath", "leafless", "PLANT · LEAFLESS")):
                if isinstance(pl.get(fld), str) and pl[fld]:
                    out.append(slot(def_name, "plant." + fld, kind, lab, pl[fld]))
        elif t:
            out.append(slot(def_name, "graphicData", "item", "CATCH ITEM" if catch else "ITEM", t,
                            pool=_is_random(gd), required=True))
    # one lane per texPath: the most senior slot names it, the rest are "also used by"
    seen: dict = {}
    res = []
    for s in out:
        k = s["res"]
        if k in seen:
            if s["label"] not in seen[k]["also"] and s["label"] != seen[k]["label"]:
                seen[k]["also"].append(s["label"])
            continue
        s["also"] = []
        seen[k] = s
        res.append(s)
    return res


def hint(job: str) -> str:
    """What an unassigned render's job name suggests it is a picture of (shown, never acted on)."""
    for _k, rx, text in HINTS:
        if rx.search(job or ""):
            return text
    return ""


def set_id(faces: dict) -> str:
    """A set's stable identity under its letter: sha256 of its sorted (facing, picture sha) pairs, 16 hex."""
    return hashlib.sha256("|".join(f"{f}={s}" for f, s in sorted((faces or {}).items())).encode()).hexdigest()[:16]
