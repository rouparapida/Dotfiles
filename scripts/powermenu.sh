#!/usr/bin/env bash

THEME="${POWERMENU_THEME:-$HOME/.config/rofi/powermenu/powermenu.rasi}"

if [[ ! -f "$THEME" ]]; then
    notify-send "Power menu" "Tema não encontrado: $THEME" 2>/dev/null
    echo "Tema não encontrado: $THEME" >&2
    exit 1
fi

poweroff_icon=$(printf '\uf011')
reboot_icon=$(printf '\uf021')
lock_icon=$(printf '\uf023')
logout_icon=$(printf '\uf2f5')

choice=$(printf '%s\n' "$poweroff_icon" "$reboot_icon" "$lock_icon" "$logout_icon" |
    rofi -no-config \
         -dmenu \
         -theme "$THEME" \
         -p "" \
         -format i \
         -selected-row 0 \
         -no-custom)

case "$choice" in
    0) systemctl poweroff ;;
    1) systemctl reboot ;;
    2) pidof hyprlock >/dev/null || hyprlock ;;
    3) hyprctl dispatch 'hl.dsp.exit()' ;;
    *) exit 0 ;;
esac