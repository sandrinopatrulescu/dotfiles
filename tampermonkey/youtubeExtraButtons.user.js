// ==UserScript==
// @name         youtubeExtraButtons
// @namespace    http://tampermonkey.net/
// @version      2025-05-01
// @description  YouTube extra buttons
// @author       AiWonder
// @match        https://www.youtube.com/watch?v=*
// @grant        none
// @downloadURL  https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeExtraButtons.user.js
// @updateURL    https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeExtraButtons.user.js
// ==/UserScript==

(function () {
    'use strict';

    function writeTextToClipboard(text) {
        navigator.clipboard.writeText(text)
            .then(() => {
                console.log(`Copied to clipboard: ${text}`);
            })
            .catch(err => {
                console.error("Failed to copy:", text);
                console.error("Err:", err);
            });
    }

    const buttonsContainer = document.createElement('div');

    const copyUTButton = document.createElement("button");
    copyUTButton.id = "copyUTButton";
    copyUTButton.innerText = 'UT';
    copyUTButton.title = 'Copy url title';

    const copyDUTButton = document.createElement("button");
    copyDUTButton.id = "copyDUTButton";
    copyDUTButton.innerText = 'DUT';
    copyDUTButton.title = 'Copy duration url title';

    buttonsContainer.appendChild(copyUTButton);
    buttonsContainer.appendChild(copyDUTButton);

    window.addEventListener('load', function () {
        const startDiv = document.getElementById('start');

        const duration = document.getElementsByClassName('ytp-time-duration')[0].innerText;
        const title = document.title.replace(' - YouTube', '');
        const url = location.href;

        copyUTButton.onclick = () => writeTextToClipboard(`${url} ${title}`);
        copyDUTButton.onclick = () => writeTextToClipboard(`${duration} ${url} ${title}`);


        startDiv.appendChild(buttonsContainer);
    });
})();
