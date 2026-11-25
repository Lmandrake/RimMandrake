#!/bin/bash
# install.sh - install the ~/rm SSD mount, its check, and the Windows attach scripts on SteveDesktop. Rerunnable.
# Run in SteveDesktop's WSL as mandrake (uses sudo): bash ~/rm/runner/infrastructure/stevedesktop/rm_ssd/install.sh
# Then register the Windows task once, over the elevated ssh door:
#   ssh stevedesktop "powershell -NoProfile -ExecutionPolicy Bypass -File C:\SteveDesktop\rm_ssd_install_task.ps1"
set -euo pipefail
H=$(cd "$(dirname "$0")" && pwd)
sudo install -m 0755 "$H/rm-ssd-mount.sh" /usr/local/sbin/rm-ssd-mount.sh
sudo install -m 0644 "$H/rm-ssd-mount.service" /etc/systemd/system/rm-ssd-mount.service
sudo systemctl daemon-reload
sudo systemctl enable rm-ssd-mount.service
install -D -m 0755 "$H/rm_ssd_check.py" "$HOME/.local/bin/rm_ssd_check.py"
install -D -m 0644 "$H/rm-ssd-check.service" "$HOME/.config/systemd/user/rm-ssd-check.service"
install -D -m 0644 "$H/rm-ssd-check.timer" "$HOME/.config/systemd/user/rm-ssd-check.timer"
install -D -m 0755 "$H/rm_pool_room.py" "$HOME/.local/bin/rm_pool_room.py"
install -D -m 0644 "$H/rm-pool-room.service" "$HOME/.config/systemd/user/rm-pool-room.service"
install -D -m 0644 "$H/rm-pool-room.timer" "$HOME/.config/systemd/user/rm-pool-room.timer"
systemctl --user daemon-reload
systemctl --user enable --now rm-ssd-check.timer rm-pool-room.timer
cp "$H/rm_ssd_attach.ps1" "$H/rm_ssd_attach.vbs" /mnt/c/SteveDesktop/
cp "$H/install_task.ps1" /mnt/c/SteveDesktop/rm_ssd_install_task.ps1
echo "installed: rm-ssd-mount.service (enabled), rm-ssd-check.timer and rm-pool-room.timer (user), C:\\SteveDesktop\\rm_ssd_attach.{ps1,vbs}"
