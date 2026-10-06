# Monodots

> Hyprland dotfiles I use daily, focused on simplicity and a monochrome palette.

## Installation

For the best experience, I highly recommend installing CachyOS without a desktop environment, or Arch Linux using `archinstall`. Either setup reduces the number of manual steps required.

1. Install the dependencies:

```bash
sudo pacman -S --needed git base-devel
```

2. Clone the repository:

```bash
git clone https://github.com/rouparapida/Dotfiles.git
cd Dotfiles
```

3. Make the installer executable and run it:

```bash
chmod +x install.sh
./install.sh
```

4. Reboot your system:

```bash
sudo reboot
```

## Post-Installation

After the installation finishes, a few manual steps are required for everything to work properly:

- **Set your keyboard layout:** The default layout is US English. Update it in the Hyprland configuration so your keys map correctly.
  Edit the following file: `~/.config/hypr/modules/input.lua`

- **Configure your monitors:** Define the resolution, refresh rate, and position of each monitor.
  Edit the following file: `~/.config/hypr/modules/monitors.lua`

- **Make custom scripts executable:** Give execute permission to the custom scripts (`powermenu.sh` and `cleaner.sh`) located in `~/.scripts`:

```bash
  chmod +x ~/.scripts/powermenu.sh ~/.scripts/cleaner.sh
```

- **Install GPU drivers:** For the best performance and to avoid visual glitches, make sure the correct video drivers for your hardware are installed.

- **Install CPU microcode:** To improve stability and apply known CPU fixes, make sure the appropriate microcode package for your processor is installed.

- **Set GTK and icon themes:** Apply your preferred look using a GTK settings application.

## Keybindings

> Main modifier: `SUPER` (Windows key)

### General

| Key | Action |
|-----|--------|
| SUPER + Q | Open terminal |
| SUPER + E | Open file manager |
| SUPER + Space | Open application launcher |
| SUPER + L | Lock screen |
| SUPER + P | Power menu |
| SUPER + N | Notification center |
| SUPER + SHIFT + W | Wallpaper selector |
| SUPER + SHIFT + S | Screenshot (region) |
| Print Screen | Screenshot (full screen) |
| Mute | Toggle mute |
| Volume Up | Increase volume by 5% |
| Volume Down | Decrease volume by 5% |
| Brightness Up | Increase brightness by 5% |
| Brightness Down | Decrease brightness by 5% |

---

### Window Management

| Key | Action |
|-----|--------|
| SUPER + Arrow Keys | Move focus |
| SUPER + SHIFT + Arrow Keys | Move window |
| SUPER + J | Toggle split layout |
| SUPER + C | Close active window |
| SUPER + V | Toggle floating mode |
| SUPER + F | Fullscreen |

---

### Workspaces

| Key | Action |
|-----|--------|
| SUPER + 1-0 | Switch workspace |
| SUPER + SHIFT + 1-0 | Move window to workspace |