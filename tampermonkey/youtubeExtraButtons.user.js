// ==UserScript==
// @name         youtubeExtraButtons
// @namespace    http://tampermonkey.net/
// @version      2026-08-23_17-55-21
// @description  YouTube extra buttons
// @author       AiWonder
// @match        https://www.youtube.com/watch?v=*
// @grant        none
// @downloadURL  https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeExtraButtons.user.js
// @updateURL    https://github.com/sandrinopatrulescu/dotfiles/raw/refs/heads/main/tampermonkey/youtubeExtraButtons.user.js
// ==/UserScript==

function getVideoMetadata() {
    return JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent);
}

function getVideoUploadDate() {
    const metadata = getVideoMetadata();
    const uploadDateIsoString = metadata.uploadDate;
    const uploadDate = new Date(uploadDateIsoString);
    const uploadDateString = uploadDate.toLocaleDateString("en-CA");
    console.log(`${uploadDateIsoString} -> ${uploadDate} -> ${uploadDateString}`);
    return uploadDateString;
}

(function () {
    'use strict';

    const scriptName = GM_info.script.name;

    const setUp = function () {
        function writeTextToClipboard(text, html = undefined) {
            const item = { 'text/plain': new Blob([text], {type: 'text/plain'}), };
            if (html) {
                item['text/html'] = new Blob([html], {type: 'text/html'});
            }

            navigator.clipboard.write([new ClipboardItem(item)])
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

        const copyUDUTButton = document.createElement("button");
        copyUDUTButton.id = "copyUDUTButton";
        copyUDUTButton.innerText = 'UDUT';
        copyUDUTButton.title = 'Copy upload-date,duration,url,title';

        const copyUDAUTButton = document.createElement("button");
        copyUDAUTButton.id = "copyUDAUT";
        copyUDAUTButton.innerText = 'UDAUT';
        copyUDAUTButton.title = 'Copy upload-date,duration,author,url,title';

        buttonsContainer.appendChild(copyUTButton);
        buttonsContainer.appendChild(copyDUTButton);
        buttonsContainer.appendChild(copyUDUTButton);
        buttonsContainer.appendChild(copyUDAUTButton);


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
        copyUDUTButton.onclick = () => {
            const [duration, title, url] = getDurationTitleAndUrl();
            const uploadDateString = getVideoUploadDate();

            const urlToAnchor = (url, title) => `<a href="${url}">${title}</a>`;
            const [text, html] = [url, urlToAnchor(url, url)].map(x => `${uploadDateString},${duration},${x},${title}`);

            writeTextToClipboard(text, html);
        }
        copyUDAUTButton.onclick = () => {
            const [duration, title, url] = getDurationTitleAndUrl();
            const uploadDateString = getVideoUploadDate();
            const author = getVideoMetadata().author;

            const urlToAnchor = (url, title) => `<a href="${url}">${title}</a>`;
            const [text, html] = [url, urlToAnchor(url, url)].map(x => `${uploadDateString},${duration},${author},${x},${title}`);

            writeTextToClipboard(text, html);
        };

        startDiv.appendChild(buttonsContainer);
    };

    const delaySetUp = function () {
        setTimeout(setUp, 500);
    }

    delaySetUp();
})();
