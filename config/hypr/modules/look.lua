-- Window look
hl.config({
    general = {
        gaps_in = 2,
        gaps_out = 6,
        border_size = 1,

        col = {
            active_border = "rgba(ffffff33)",
            inactive_border = "rgba(ffffff14)",
        },

        resize_on_border = false,
        allow_tearing = false,
        layout = "dwindle",
    },

    decoration = {
        rounding = 8,
        rounding_power = 2,

        active_opacity = 1.0,
        inactive_opacity = 1.0,

        shadow = {
            enabled = false,
            range = 10,
            render_power = 2,
            color = 0x1a000000,
        },

        blur = {
            enabled = false,
            size = 6,
            passes = 3,
        },
    },

    animations = {
        enabled = true,
    },
})

-- Animations
hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })
hl.curve("easeInOutCubic", { type = "bezier", points = { { 0.65, 0.05 }, { 0.36, 1 } } })
hl.curve("linear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.curve("almostLinear", { type = "bezier", points = { { 0.5, 0.5 }, { 0.75, 1 } } })
hl.curve("quick", { type = "bezier", points = { { 0.15, 0 }, { 0.1, 1 } } })

hl.animation({ leaf = "global", enabled = true, speed = 10.2, bezier = "default" })
hl.animation({ leaf = "border", enabled = true, speed = 5.5, bezier = "easeOutQuint" })

hl.animation({ leaf = "windows", enabled = true, speed = 4.9, bezier = "easeOutQuint" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 4.3, bezier = "easeOutQuint", style = "popin 87%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.5, bezier = "linear", style = "popin 87%" })

hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.8, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.5, bezier = "almostLinear" })
hl.animation({ leaf = "fade", enabled = true, speed = 3.1, bezier = "quick" })

hl.animation({ leaf = "layers", enabled = true, speed = 3.9, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 4.1, bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.5, bezier = "linear", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 1.8, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.5, bezier = "almostLinear" })

hl.animation({ leaf = "workspaces", enabled = true, speed = 3.5, bezier = "easeOutQuint", style = "slidefade 20%" })
hl.animation({ leaf = "workspacesIn", enabled = true, speed = 3.5, bezier = "easeOutQuint", style = "slidefade 20%" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 3.5, bezier = "easeOutQuint", style = "slidefade 20%" })

hl.animation({ leaf = "zoomFactor", enabled = true, speed = 7.2, bezier = "quick" })

-- Layouts
hl.config({
    dwindle = {
        preserve_split = true,
    },
})

hl.config({
    master = {
        new_status = "master",
    },
})

hl.config({
    scrolling = {
        fullscreen_on_one_column = true,
    },
})
