#!/bin/bash
# rm-ssd-mount.sh - mount SteveDesktop's ~/rm disk at /home/mandrake/rm (RIMMANDRAKE_MOVE_STEVEDESKTOP_CLONES_TO_SSD_LINUX_DRIVE_SITS_ON_HARD_DISK).
# The disk is C:\WSL\rmssd\rm.vhdx (80 GiB, fixed, ext4 label rmssd) on the NVMe. Windows attaches it to the WSL VM
# (`wsl --mount --bare` needs administrator: the \RM SSD Attach task, at logon and every 2 min); this mounts it.
# Run as root by rm-ssd-mount.service at every boot of the distro. Installed to /usr/local/sbin by install.sh.
# No time limit on the wait: a wait that never ends harms nothing (the unit is Type=simple, nothing is ordered after it),
# and the empty ~/rm under the mount is immutable, so a tool that runs before the mount fails instead of writing the HDD.
UUID=3bfbfd35-f6eb-41fe-a94d-10faf48fa360
MP=/home/mandrake/rm
TASK='\RM SSD Attach'
n=0
while ! mountpoint -q "$MP"; do
    dev=$(blkid -U "$UUID" 2>/dev/null)
    if [ -n "$dev" ]; then
        if mount -o noatime "$dev" "$MP"; then echo "mounted $dev at $MP"; break; fi
        echo "mount of $dev at $MP failed; retrying"
    elif [ $((n % 6)) -eq 0 ]; then
        # not attached yet: ask Windows now instead of waiting for the task's next 2-minute beat
        if /mnt/c/Windows/System32/schtasks.exe /run /tn "$TASK" >/dev/null 2>&1; then echo "disk $UUID absent: asked Windows to run $TASK"
        else echo "disk $UUID absent and schtasks.exe could not run $TASK (interop?); the task's own beat will attach it"; fi
    fi
    n=$((n + 1))
    sleep 10
done
mountpoint -q "$MP" && echo "$MP is $(findmnt -n -o SOURCE,UUID --mountpoint "$MP")"
