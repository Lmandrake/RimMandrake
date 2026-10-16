# usage: trim_gen.sh <size> <style> "<trim parts>"  -- one edit: trim parts flat green, rest flat black (mask source)
set -u
S=$1; T=$2; P=$3; s=$(echo $S | tr A-Z a-z); t=$(echo $T | tr A-Z a-z)
cd "$(dirname "$0")"
python3 -c "
from PIL import Image
Image.open('out/$S/$T/RM_$S.png').resize((1024,1024),Image.LANCZOS).save('trim_raw/in_${s}_${t}.png')"
for try in 1 2; do
  timeout 200 python3 /home/mandrake/rm/bench/skills/generating-images/scripts/codex_image.py edit --model gpt-6.1-sol --timeout 180 --force \
    --image trim_raw/in_${s}_${t}.png --out trim_raw/${s}_${t}.png \
    --prompt "Square 1024x1024. Make an exact copy of image 1, same position, same size, same outline, on a fully transparent background, with one change: $P painted solid flat pure green (#00FF00); every other part is painted solid flat black." > trim_raw/${s}_${t}.log 2>&1 && { echo "$s $t ok"; exit 0; }
  echo "$s $t try $try failed"
done
