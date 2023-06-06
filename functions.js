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


//
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