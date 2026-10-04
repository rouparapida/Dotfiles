-- Autostart
hl.on("hyprland.start", function()
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")

    hl.exec_cmd("awww-daemon &")
    hl.exec_cmd("swaync")
    hl.exec_cmd("hyprsunset")
    hl.exec_cmd("swayosd-server --top-margin 0.95")
    hl.exec_cmd("waybar")

    hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
end)
