// ==UserScript==
// @name         youtubeCustomVolumeChanger
// @namespace    http://tampermonkey.net/
// @version      2025-05-11_17-44-25
// @description  YouTube custom volume changer
// @author       AiWonder
// @match        https://www.youtube.com/watch?v=*
// @grant        none
// @downloadURL  https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeCustomVolumeChanger.user.js
// @updateURL    https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeCustomVolumeChanger.user.js
// ==/UserScript==

(function () {
    'use strict';

    const scriptName = GM_info.script.name;

    const setUp = function () {
        function observeAttribute(target, attribute, onValueChange) {
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.type === "attributes" && mutation.attributeName === attribute) {
                        const oldValue = mutation.oldValue;
                        const newValue = target.getAttribute(attribute);

                        if (oldValue !== newValue) {
                            onValueChange(newValue);
                        }
                    }
                });
            });

            observer.observe(target, {
                attributes: true, attributeFilter: [attribute], attributeOldValue: true,
            });
        }

        const customVolumeContainerId = 'customVolumeContainer';
        if (document.getElementById(customVolumeContainerId)) {
            console.debug(`[${scriptName}] element with id ${customVolumeContainerId} already exists. Skipping logic`);
            return;
        }

        const customVolumeContainer = document.createElement('div');
        customVolumeContainer.id = customVolumeContainerId;
        customVolumeContainer.style.display = 'flex';
        customVolumeContainer.style.gap = '8px';
        customVolumeContainer.style.alignItems = 'center';

        const customVolumeSlider = document.createElement("input");
        customVolumeSlider.id = "customVolumeSlider";
        customVolumeSlider.type = "range";
        customVolumeSlider.min = "0";
        customVolumeSlider.max = "100";

        const customVolumeInput = document.createElement("input");
        customVolumeInput.id = "customVolumeInput";
        customVolumeInput.type = "number";
        customVolumeInput.min = "0";
        customVolumeInput.max = "100";

        customVolumeContainer.appendChild(customVolumeSlider);
        customVolumeContainer.appendChild(customVolumeInput);


        const startDiv = document.getElementById('start');
        if (!startDiv) {
            console.error(`[${scriptName}] failed to find element for injection`);
            return;
        }


        const player = document.querySelector(".html5-video-player");

        const currentPlayerVolume = player.getVolume();
        customVolumeSlider.value = currentPlayerVolume;
        customVolumeInput.value = currentPlayerVolume;

        // Synchronize slider -> number input
        customVolumeSlider.addEventListener('input', () => {
            customVolumeInput.value = customVolumeSlider.value;
            player.setVolume(customVolumeInput.value);
        });

        // Synchronize number input -> slider
        customVolumeInput.addEventListener('input', () => {
            let val = parseInt(customVolumeInput.value, 10);
            if (isNaN(val)) val = 0;
            val = Math.max(0, Math.min(100, val));
            customVolumeSlider.value = `${val}`;
            player.setVolume(customVolumeSlider.value);
        });

        const volumePanel = document.getElementsByClassName("ytp-volume-panel")[0];
        observeAttribute(volumePanel, 'aria-valuenow', (newValue) => {
            customVolumeSlider.value = newValue;
            customVolumeInput.value = newValue;
            console.log(`[${scriptName}] Volume changed to ` + newValue);
        });

        startDiv.appendChild(customVolumeContainer);
    };

    const delaySetUp = function () {
        setTimeout(setUp, 500);
    }

    delaySetUp();
})();
