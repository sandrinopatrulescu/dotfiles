// ==UserScript==
// @name         youtubeCustomVolumeChanger
// @namespace    http://tampermonkey.net/
// @version      2025-05-10_17-47
// @description  YouTube custom volume changer
// @author       AiWonder
// @match        https://www.youtube.com/watch?v=*
// @grant        none
// @downloadURL  https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeCustomVolumeChanger.user.js
// @updateURL    https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeCustomVolumeChanger.user.js
// ==/UserScript==

(function () {
    'use strict';

    function observeAttribute(target, attribute, onValueChange) {
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.type === "attributes" && mutation.attributeName === attribute) {
                    const newValue = target.getAttribute(attribute);
                    onValueChange(newValue);
                }
            });
        });

        observer.observe(target, {
            attributes: true,
            attributeFilter: [attribute]
        });
    }

    const customVolumeContainer = document.createElement('div');
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

    /* https://stackoverflow.com/questions/34077641/how-to-detect-page-navigation-on-youtube-and-modify-its-appearance-seamlessly */
    window.addEventListener('yt-navigate-finish', function () {
        const startDiv = document.getElementById('start');

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
            console.log("[youtubeCustomVolumeChanger] Volume changed to " + newValue);
        });

        startDiv.appendChild(customVolumeContainer);
    });
})();
