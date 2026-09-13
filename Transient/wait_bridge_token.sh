#!/bin/bash
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
until grep -q "Bridge token:" "$LOG" 2>/dev/null; do sleep 20; done
echo "BRIDGE UP at $(date)"
