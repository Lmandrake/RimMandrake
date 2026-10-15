#!/usr/bin/env bash
# Fit every finished look render (v2/looks/<Tank>_<Look>_raw.png) onto its game canvas at v3/<Look>/<Tank>.png with
# fit_to_master.py (same width and ground line as the tank's shape master in v3/_master/), so all four looks of one tank
# stand identically. The Scrapper liquid tanks ARE their masters.
cd "$(dirname "$0")/.."
for f in v2/looks/*_raw.png; do
  b=$(basename "$f" _raw.png); look=${b##*_}; tank=${b%_*}
  mkdir -p v3/$look; python3 v3/fit_to_master.py "$f" v3/_master/$tank.png "v3/$look/$tank.png"
done
cp v3/_master/RM_LiquidTank.png v3/Scrapper/RM_LiquidTank.png; cp v3/_master/RM_LiquidTankTall.png v3/Scrapper/RM_LiquidTankTall.png
