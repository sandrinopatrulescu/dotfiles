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