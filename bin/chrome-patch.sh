#!/bin/bash


chromePathDefault="/opt/google/chrome/google-chrome"
commandAnteFix='exec -a "$0" "$HERE/chrome" "$@"'
commandPostFix='exec -a "$0" "$HERE/chrome" --disable-features=ExtensionManifestV2Unsupported,ExtensionManifestV2Disabled "$@"'


sudo true # prompt sudo password
read -r -p "enter path [${chromePathDefault}]" chromePath
chromePath=${chromePath:-$chromePathDefault}


if /usr/bin/grep -q "${commandPostFix}" "${chromePath}"; then
    echo "RESULT: already patched"
elif /usr/bin/grep -q "${commandAnteFix}" "${chromePath}"; then
    chromeCopy="${chromePath}.$(date +%Y-%m-%d_%H-%M-%S)"
    sudo cp "${chromePath}" "${chromeCopy}" && echo "Created copy ${chromeCopy}"
    sudo sed -i "s|${commandAnteFix}|${commandPostFix}|" "${chromePath}"
    echo "# ${commandAnteFix} # commandAnteFix" | sudo tee -a "${chromePath}" > /dev/null
    echo "RESULT: patching succeeded"
else
    echo "RESULT: FAILED to find matched string"
fi