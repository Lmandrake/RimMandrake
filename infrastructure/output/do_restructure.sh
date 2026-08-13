#!/usr/bin/env bash
# do_restructure.sh — one-pass execution of output/RESTRUCTURE_PLAN.md §2.
#
# Stages 0-2 (scaffold, research/, vendor/) already landed as 4e0718c, d997871,
# 8909111. This script performs EVERYTHING ELSE in §2 in a single pass:
# stages 3-8. Stage 9 (skills/) is owner-gated and DOES NOT RUN.
#
# `git mv` is used for every tracked path so rename detection survives; paths
# that git does not track (gitignored payloads: logs, art _raw/_cut, _review,
# __pycache__) are moved with plain `mv` because `git mv` refuses them.
#
# Idempotent-ish: every move is guarded on the source existing, so a re-run
# after a partial failure resumes rather than erroring out.
set -u
cd "$(dirname "$0")/.." || exit 1

STAMP="observed/2026-08-13_pre-restructure"

tracked() {
  if [ -d "$1" ]; then
    [ -n "$(git ls-files -- "$1" | head -1)" ]
  else
    git ls-files --error-unmatch -- "$1" >/dev/null 2>&1
  fi
}

# mvp SRC DST — move one path, using git mv when git knows about it.
mvp() {
  [ -e "$1" ] || return 0
  mkdir -p "$(dirname "$2")"
  if tracked "$1"; then git mv -- "$1" "$2"; else mv -- "$1" "$2"; fi
}

# mvinto DST SRC... — move each SRC into directory DST, keeping its basename.
mvinto() {
  d="$1"; shift
  mkdir -p "$d"
  for s in "$@"; do mvp "$s" "$d/$(basename "$s")"; done
}

mkdir -p design/Jawa design/RimMandrake src/Jawa src/RimMandrake \
         deployed/config "$STAMP" infrastructure/state infrastructure/archive

# ---------------------------------------------------------------- worldbuilding
mvinto design/RimMandrake \
  worldbuilding/Custom_World.md \
  worldbuilding/faction_authoring_mechanism.md \
  worldbuilding/balance_paradigm.md
mvp worldbuilding design/Jawa/worldbuilding

# --------------------------------------------------------------------- runtime
# generic method docs -> design/RimMandrake/
mvinto design/RimMandrake \
  runtime/beautiful_tilemap.md \
  runtime/llm_stack_assessment.md \
  runtime/llm_voice_preauthoring.md \
  runtime/map_authoring_decision.md \
  runtime/music_protocol.md \
  runtime/ollama.md \
  runtime/rimbridge.md \
  runtime/rimtalk_analysis.md
# scenario docs -> design/Jawa/
mvinto design/Jawa \
  runtime/build_plan.md \
  runtime/carbonite_trophy_mod.md \
  runtime/divine_satiation_engine.md \
  runtime/droid_ruling.md \
  runtime/first_live_access.md \
  runtime/parked_mod_concepts.md
# game-state artifacts -> observed/<stamp>/
mvp runtime/logs "$STAMP/logs"
for f in runtime/latency_*.json; do mvp "$f" "$STAMP/$(basename "$f")"; done
# game config copied for tracking -> deployed/config/
for f in runtime/backups/*ModsConfig* runtime/backups/Mod_*.xml \
         runtime/backups/*userRules*.json runtime/backups/xenotypes; do
  mvp "$f" "deployed/config/$(basename "$f")"
done
# CREATE's image-generation bench -> src/Jawa/
mvp runtime/art src/Jawa/art_bench
rmdir runtime/backups runtime 2>/dev/null

# ------------------------------------------------------------------------ mods
mvinto design/Jawa/mods \
  mods/agent_supersession_audit.md \
  mods/armoury_keeplist.md \
  mods/cherry_picker_killlist.md \
  mods/concept_defnames.md \
  mods/forbidden_mods.md \
  mods/outer_rim_cherrypick_list.md \
  mods/required_mods.md \
  mods/world_interest_and_mech_danger.md
mvp mods/live_mod_inventory.md "$STAMP/live_mod_inventory.md"
mvp mods/inventory "$STAMP/inventory"
mvp mods/dumps    "$STAMP/dumps"
mvp mods/dev/RimDefDump src/RimMandrake/RimDefDump
rmdir mods/dev mods 2>/dev/null

# -------------------------------------------------------------- custom_patches
mvinto src/Jawa \
  custom_patches/Jawa_Armoury \
  custom_patches/Jawa_Doctrine \
  custom_patches/Jawa_Patches \
  custom_patches/JawaVoice \
  custom_patches/JawaIonWeapons \
  custom_patches/DesertVehicleReskin
mvinto src/RimMandrake \
  custom_patches/MissingArtFixes \
  custom_patches/WreckedMachines
# DEPLOY_HOLD.txt is read as SRC_ROOT/DEPLOY_HOLD.txt; SRC_ROOT becomes src/.
mvp custom_patches/DEPLOY_HOLD.txt src/DEPLOY_HOLD.txt
# src/README.md is the tier file written by stage 0; the deploy-source README
# keeps its name one level down rather than being renamed (plan §2, no renames).
mvp custom_patches/README.md src/Jawa/README.md
rmdir custom_patches 2>/dev/null

# ----------------------------------------------------------- bridgetools/Utils
mvp bridgetools src/RimMandrake/bridgetools
mvp Utils       src/RimMandrake/Utils

# ----------------------------------------------------------------- player_maps
mvp player_maps/authored/coastal_mesa_rationale.md design/RimMandrake/coastal_mesa_rationale.md
mkdir -p src/RimMandrake/mapsynth/runs
for f in player_maps/*; do
  [ -e "$f" ] || continue
  b=$(basename "$f")
  case "$b" in
    __pycache__)                     rm -rf "$f" ;;
    authored|README.md|*.py)         mvp "$f" "src/RimMandrake/mapsynth/$b" ;;
    *)                               mvp "$f" "src/RimMandrake/mapsynth/runs/$b" ;;
  esac
done
rmdir player_maps 2>/dev/null

# -------------------------------------------------------------------- savegame
mvp savegame "$STAMP/savegame"

# --------------------------------------------------------------- image_request
mvinto design/Jawa/art \
  image_request/codex_imagegen_origin_plan.md \
  image_request/graphic.md \
  image_request/graphics_overhaul_protocol.md \
  image_request/.gitignore
mvp image_request/_review src/Jawa/art_bench/_review
rmdir image_request 2>/dev/null

# -------------------------------------------------------------- infrastructure
mvp agents    infrastructure/agents
mvp queue     infrastructure/state/queue
mvp disposing infrastructure/disposing
mvp context.md infrastructure/archive/context.md

mvinto infrastructure \
  STRUCTURE.md agents_def.md DOC_BUDGET.md REFRESH.md
mvinto infrastructure/state \
  TODO.md TODO_v2.md NEXT_RELOAD.md OWNER_DECISIONS.md CLOSED.md V1_SCOPE.md \
  AGENT_BRIDGE_state.md AGENT_CREATE_state.md AGENT_OPS_state.md AGENT_PROJECT_state.md
mvp concept.md                  design/Jawa/concept.md
mvp rimworld_file_lore.md       design/RimMandrake/rimworld_file_lore.md
mvp save_authoring_pipeline.md  design/RimMandrake/save_authoring_pipeline.md

# output/ moves LAST — this script lives inside it.
mvp output infrastructure/output

echo "do_restructure.sh: complete"
