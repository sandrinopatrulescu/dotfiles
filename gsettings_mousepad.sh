#!/bin/bash

# View
gsettings set org.xfce.mousepad.preferences.view show-line-numbers true
gsettings set org.xfce.mousepad.preferences.view show-whitespace true
gsettings set org.xfce.mousepad.preferences.view show-line-endings true
gsettings set org.xfce.mousepad.preferences.view show-right-margin true
gsettings set org.xfce.mousepad.preferences.view highlight-current-line true
gsettings set org.xfce.mousepad.preferences.view match-braces true
gsettings set org.xfce.mousepad.preferences.view word-wrap true

gsettings set org.xfce.mousepad.preferences.view color-scheme 'cobalt'

# Editor
gsettings set org.xfce.mousepad.preferences.view tab-width 4
gsettings set org.xfce.mousepad.preferences.view insert-spaces false
gsettings set org.xfce.mousepad.preferences.view auto-indent true

gsettings set org.xfce.mousepad.preferences.view indent-on-tab true
gsettings set org.xfce.mousepad.preferences.view smart-backspace true
gsettings set org.xfce.mousepad.preferences.view smart-home-end 'before'

# Window
gsettings set org.xfce.mousepad.preferences.window path-in-title true
gsettings set org.xfce.mousepad.preferences.window remember-size true
gsettings set org.xfce.mousepad.preferences.window remember-state true

gsettings set org.xfce.mousepad.preferences.window toolbar-visible false

gsettings set org.xfce.mousepad.preferences.window always-show-tabs true
gsettings set org.xfce.mousepad.preferences.window expand-tabs false
gsettings set org.xfce.mousepad.preferences.window opening-mode 'mixed'

# File
gsettings set org.xfce.mousepad.preferences.file add-last-end-of-line true

gsettings set org.xfce.mousepad.preferences.file session-restore 'unsaved-documents'

gsettings set org.xfce.mousepad.preferences.file monitor-changes true

# Plugins
#gsettings set org.xfce.mousepad.state.application enabled-plugins "['mousepad-plugin-gspell']"

# other settings
gsettings set org.xfce.mousepad.preferences.window statusbar-visible true

gsettings set org.xfce.mousepad.state.search incremental true
gsettings set org.xfce.mousepad.state.search highlight-all true
