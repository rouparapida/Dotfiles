#!/bin/bash

echo "Starting system cleanup..."

echo "Cleaning Pacman cache..."
sudo paccache -r

echo "Removing orphan packages..."
orphans=$(pacman -Qtdq)
if [ -n "$orphans" ]; then
    sudo pacman -Rns $orphans --noconfirm
else
    echo "No orphan packages found."
fi

echo "Vacuuming system logs..."
sudo journalctl --vacuum-time=7d

echo "Emptying user trash..."
rm -rf ~/.local/share/Trash/*

echo "Cleanup completed successfully."
echo "-----------------------------------"

read -p "Would you like to update the system now? [Y/n]: " confirm
if [[ "$confirm" == [yY] ]]; then
    echo "Running system update..."
    sudo pacman -Syu
else
    echo "Update skipped."
fi
