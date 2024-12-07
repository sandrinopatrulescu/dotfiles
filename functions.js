'use strict';

/* NOTE: don't use inline comments if you plan to use it as bookmarklet https://mrcoles.com/bookmarklet/ */

/*
IDEA: i need something that allows me everytime I do a push to my dotfiles github repo
to have all the javascript code converted into bookmarklets and puts them in
my browser's bookmarks list in a special folder (all automatically)
OR EVEN BETTER: create an extension with all this fixes and the possibility to disable any
*/

function showPassword() {
    const inputElementsHTMLCollection = document.getElementsByTagName('input');
    const inputElementsArray = Array.from(inputElementsHTMLCollection);

    inputElementsArray.forEach(inputElement => {
        if (inputElement.type === 'password') {
            inputElement.type = 'text';
        }
    });
}

function uniFilterSchedule() {
    const TABLE_INDEX = 4;
    const formations = ["IE3", "935", "935/2"];
    const disciplines = [
        "Elaborarea lucrarii de licenta",
        "Verificarea si validarea sistemelor soft",
        "Calcul numeric",
        "Tehnici de testare software",
        "Blockchain: Smart contracts",
        "Istoria informaticii",
    ];
    const FORMATION_COLUMN = 4;
    const DISCIPLINE_COLUMN = 6;

    const table = document.getElementsByTagName("table")[TABLE_INDEX];
    const getFormation = (row/*: HTMLTableRowElement*/) => row.cells[FORMATION_COLUMN].innerText;
    const getDiscipline = (row/*: HTMLTableRowElement*/) => row.cells[DISCIPLINE_COLUMN].innerText;


    const rows = table.rows;
    var removed = 0;

    console.log("Initial length: " + rows.length);
    for (let i = 0; i < rows.length; i++) {
        var row = rows[i];

        if (formations.includes(getFormation(row)) && disciplines.includes(getDiscipline(row))) {

        } else {
            table.deleteRow(i);
            removed++;
            i--;
        }
    }
    console.log("Removed: " + removed);
    console.log("Final length: " + rows.length);

    Array.from(document.getElementsByTagName("table"))
        .filter((value, index) => index !== TABLE_INDEX).forEach(table => table.remove());
}

function uniSemesterGradeCalculator() {
    const table = $('table')[0];
    const gradeHeader = "Nota";
    const creditsHeader = "Nr. Credite";
    const nameHeader = "Disciplina";


    let numerator = 0;
    let denominator = 0;
    let numeratorString = "";
    let denominatorString = "";

    const rows = table.rows;

    const headerTexts = Array.from(rows[0].cells).map(cell => cell.innerText);
    const gradeColumnIndex = headerTexts.indexOf(gradeHeader);
    const creditsColumnIndex = headerTexts.indexOf(creditsHeader);
    const nameColumnIndex = headerTexts.indexOf(nameHeader);

    console.log(`${gradeHeader} index: ${gradeColumnIndex}`);
    console.log(`${creditsHeader} index: ${creditsColumnIndex}`);
    console.log(`${nameHeader} index: ${nameColumnIndex}`);

    for (let rowIndex = 1; rowIndex < rows.length; rowIndex++) {
        const getCell = (rowIndex, columnIndex) => rows[rowIndex].cells[columnIndex].innerText;
        const credits = getCell(rowIndex, creditsColumnIndex);
        const name = getCell(rowIndex, nameColumnIndex);
        let grade = getCell(rowIndex, gradeColumnIndex);
        console.log(`name: ${name}, grade: ${grade}, credits: ${credits}`);

        if (!$.isNumeric(grade)) {
            console.log(`Grade for ${name} (${credits} credits) was not set. Prompting user for value...`);
            grade = prompt(`Grade for ${name} (${credits} credits) not set.\n Set value or leave blank to exclude: `);
            if ($.isNumeric(grade)) {
                console.log(`Setting grade for ${name} (${credits} credits) to ${grade}.`);
            }
        }
        if (grade === "") {
            console.log(`Excluding ${name} (${credits} credits)`);
        } else {
            numerator += credits * grade;
            denominator += parseInt(credits);
            numeratorString += `${credits} * ${grade}` + (rowIndex === rows.length - 1 ? "" : " + ");
            denominatorString += `${credits}` + (rowIndex === rows.length - 1 ? "" : " + ");
        }
    }

    const truncateNumber = (number, digits) => Math.trunc(number * Math.pow(10, digits)) / Math.pow(10, digits);

    const result = numerator / denominator;
    const resultString = `(${numeratorString}) / (${denominatorString})`;
    const message = `Result: ${result}\n${truncateNumber(result, 2)} = ${resultString}`;
    console.log(message);
    alert(message);
}


/**
 * Runs properly from either a video page (watch?v) or a channel page.
 */
function youtubePlayAllFromChannel() {
    /* source: https://www.google.com/search?q=youtube+play+all+button -> https://www.reddit.com/r/youtube/comments/rl2rtu/comment/jfksy1d/ -> https://old.reddit.com/r/youtube/comments/v5vugs/uploads_playlist_bookmarklet_for_channels_that/ */
    function findVal(object, key) { /* https://stackoverflow.com/a/40604638 */
        var value;
        Object.keys(object).some(function(k) {
            if (k === key) {
                value = object[k];
                return true;
            }
            if (object[k] && typeof object[k] === 'object') {
                value = findVal(object[k], key);
                return value !== undefined;
            }
        });
        return value;
    }
    var channelID = findVal(ytInitialData, 'browseId');
    window.location.replace("https://youtube.com/playlist?list=" + channelID.replace("UC", "UU"));
}

/**
 * Runs from  a video page (watch?v)
 */
function youtubePlayAllFromChannelOldestFirst() {
    const regex = /^https:\/\/www\.youtube\.com\/watch\?v=.{11}$/;
    if (regex.test(window.location.href)) {
        /* from How to watch all videos of a channel in chronological order -> https://www.reddit.com/r/youtube/comments/iqse6g/comment/gqb6v0h/ */
        window.location.replace(window.location.href + "&list=ULcxqQ59vzyTk");
    } else {
        alert("This function is not meant to be run from this page.");
    }
}

function exportPhoneChromeTabs() {
    function exportArrayToFile(array) {
        /*Create a Blob containing the array as text*/
        const blob = new Blob([JSON.stringify(array, null, 4)], {type: 'text/plain'});

        /*Create a link element to trigger the download*/
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);

        /*NOTE that the date is UTC*/
        const dateFormatted = new Date().toISOString()
            .replace('T', '_')
            .replace(new RegExp(":", "g"), '-');
        link.download = `${dateFormatted}.json`;

        /*Trigger a click event on the link to prompt the user to save the file*/
        link.click();

        /*Clean up by revoking the Blob URL*/
        URL.revokeObjectURL(link.href);
    }

    const anchorNodeList = document.querySelector("#history-app").shadowRoot
        .querySelector("#synced-devices").shadowRoot
        .querySelector("#synced-device-list > history-synced-device-card:nth-child(1)").shadowRoot
        .querySelector("#tab-item-list").querySelectorAll("a");
    const anchorObjectArray = Array.from(anchorNodeList)
        .map(a => new Object({title: a.title, href: a.href}));
    exportArrayToFile(anchorObjectArray);
}

function changeYoutubeVolume() {
    /*https://www.google.com/search?q=programmatically+set+youtube+video+sound+level*/
    /*https://stackoverflow.com/questions/53154863/change-volume-of-a-youtube-video-while-playing*/
    const defaultVolume = 5;
    const player = document.querySelector(".html5-video-player");
    const currentVolume = player.getVolume();

    let volume = prompt(`Enter volume\nCurrent volume: ${currentVolume}`, `${defaultVolume}`);
    if (volume !== null && String(currentVolume) !== volume) {
        console.log(`[${new Date().toISOString()}] Setting volume from ${currentVolume} to ${volume}`);
        player.setVolume(volume);
    }
}

function enablePaste() {
    /*https://twitter.com/fireship_dev/status/1698438648549802104*/
    const dontTreadOnMe = (e) => e.stopImmediatePropagation();
    document.addEventListener('paste', dontTreadOnMe, true);
}

function extractImdbMovieGenres() {
    const nodes = document.querySelector('.ipc-chip-list__scroller').querySelectorAll('a');
    const texts = Array.from(nodes).map(x => x.querySelector('span').innerHTML);
    const textsAsString = texts.reduce((a, e) => `${a}, ${e}`);
    navigator.clipboard.writeText(textsAsString);
    alert("Copied to clipboard:\n" + textsAsString);
}


function lenostubeYouTubePlaylistLengthCalculator_SortDescending() {
    /* https://www.lenostube.com/en/youtube-playlist-length-calculator/ */
    const tableRows = Array.from(document.getElementById("playlist-table").querySelectorAll('tr'));

    const sortedRows = tableRows.sort((a, b) => {
        function tdToSeconds(td = a) {
            const cell = Array.from(td.querySelectorAll('td'))[2];
            const text = cell.textContent.trim();

            // Parse the "4m 11s" format
            const match = text.match(/(\d+)m\s*(\d+)?s?/);
            if (match) {
                const minutes = parseInt(match[1], 10) || 0;
                const seconds = parseInt(match[2], 10) || 0;
                return minutes * 60 + seconds;
            }

            return 0; // Default to 0 if format doesn't match
        }

        const durationA = tdToSeconds(a);
        const durationB = tdToSeconds(b);

        return durationB - durationA;
    });

    console.log(sortedRows);
}