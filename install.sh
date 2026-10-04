#!/bin/bash

set -e

cat << 'EOF'
  __  __                       _       _       
 |  \/  | ___  _ __   ___   __| | ___ | |_ ___ 
 | |\/| |/ _ \| '_ \ / _ \ / _` |/ _ \| __/ __|
 | |  | | (_) | | | | (_) | (_| | (_) | |_\__ \
 |_|  |_|\___/|_| |_|\___/ \__,_|\___/ \__|___/

EOF

echo "System update"
sudo pacman -Syyuu --noconfirm

echo "Installing fonts and themes"
sudo pacman -S --needed --noconfirm \
    noto-fonts \
    noto-fonts-emoji \
    ttf-dejavu \
    ttf-jetbrains-mono-nerd \
    nwg-look

echo "Installing Wayland and Hyprland core"
sudo pacman -S --needed --noconfirm \
    hyprland \
    qt5-wayland \
    qt6-wayland \
    xdg-desktop-portal \
    xdg-desktop-portal-hyprland \
    polkit-gnome \
    sddm

echo "Installing desktop components"
sudo pacman -S --needed --noconfirm \
    waybar \
    rofi-wayland \
    awww \
    swaync \
    swayosd \
    hyprlock \
    hyprshot \
    hyprsunset \
    hyprpicker \
    wl-clipboard \
    cliphist \
    brightnessctl \
    playerctl

echo "Installing audio and media codecs"
sudo pacman -S --needed --noconfirm \
    pipewire \
    pipewire-audio \
    pipewire-alsa \
    pipewire-pulse \
    wireplumber \
    pavucontrol \
    ffmpeg \
    gstreamer \
    gst-libav \
    gst-plugins-bad \
    gst-plugins-ugly
    
echo "Installing system and network tools"
sudo pacman -S --needed --noconfirm \
    networkmanager \
    ufw \
    gvfs \
    gvfs-mtp \
    gvfs-afc \
    usbutils \
    android-udev \
    dosfstools \
    chafa

echo "Installing terminal and utilities"
sudo pacman -S --needed --noconfirm \
    pacman-contrib \
    kitty \
    fish \
    fastfetch \
    nano \
    btop \
    unzip \
    unrar \
    zip \
    p7zip

echo "Installing applications and gaming"
sudo pacman -S --needed --noconfirm \
    firefox \
    mpv \
    nemo \
    nemo-fileroller \
    file-roller \
    gamemode \
    wine \
    wine-gecko \
    wine-mono \
    winetricks

echo "Creating user directories"
mkdir -p \
    ~/Documents \
    ~/Downloads \
    ~/Music \
    ~/Games \
    ~/Videos \
    ~/Pictures \
    ~/Projects \
    ~/.themes \
    ~/.icons \
    ~/.config \
    ~/.scripts

echo "Copying dotfiles to user directories"
if cp -r config/. "$HOME/.config/" && \
     cp -r themes/. "$HOME/.themes/" && \
     cp -r icons/. "$HOME/.icons/" && \
     cp -r scripts/. "$HOME/.scripts/" && \
     cp -r Wallpapers "$HOME/Pictures/"; then
        echo "Success! All dotfiles were successfully copied."
else
        echo "ERROR: Failed to copy the dotfiles."
fi

echo "Enabling services"
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

sudo systemctl enable ufw
sudo systemctl start ufw

sudo systemctl enable sddm

systemctl --user daemon-reexec

echo "Dependencies are installed. Please follow the post-installation steps to complete the setup"