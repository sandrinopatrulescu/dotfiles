// ==UserScript==
// @name         youtubeExtraButtons
// @namespace    http://tampermonkey.net/
// @version      2025-05-11_17-44-25
// @description  YouTube extra buttons
// @author       AiWonder
// @match        https://www.youtube.com/watch?v=*
// @grant        none
// @downloadURL  https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeExtraButtons.user.js
// @updateURL    https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeExtraButtons.user.js
// ==/UserScript==

(function () {
    'use strict';

    const scriptName = GM_info.script.name;

    const setUp = function () {
        function writeTextToClipboard(text) {
            navigator.clipboard.writeText(text)
                .then(() => {
                    console.log(`[${scriptName}] Copied to clipboard: ${text}`);
                })
                .catch(err => {
                    console.error(`[${scriptName}] Failed to copy:`, text);
                    console.error(`[${scriptName}] Err:`, err);
                });
        }

        const buttonsContainerId = 'buttonsContainer';
        if (document.getElementById(buttonsContainerId)) {
            console.debug(`[${scriptName}] element with id ${buttonsContainerId} already exists. Skipping logic`);
            return;
        }

        const buttonsContainer = document.createElement('div');
        buttonsContainer.id = buttonsContainerId;
        buttonsContainer.style.order = '999';

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


        const getDurationTitleAndUrl = () => {
            const duration = document.getElementsByClassName('ytp-time-duration')[0].innerText;
            const title = document.title.replace(' - YouTube', '');
            const url = location.href;

            return [duration, title, url];
        }

        const startDiv = document.getElementById('start');
        if (!startDiv) {
            console.error(`[${scriptName}] failed to find element for injection`);
            return;
        }


        copyUTButton.onclick = () => {
            const [, title, url] = getDurationTitleAndUrl();
            writeTextToClipboard(`${url} ${title}`);
        };
        copyDUTButton.onclick = () => {
            const [duration, title, url] = getDurationTitleAndUrl();
            writeTextToClipboard(`${duration} ${url} ${title}`);
        };

        startDiv.appendChild(buttonsContainer);
    };

    const delaySetUp = function () {
        setTimeout(setUp, 500);
    }

    delaySetUp();
})();
