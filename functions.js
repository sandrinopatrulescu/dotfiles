'use strict';

/* NOTE: don't use inline comments if you plan to use it as bookmarklet https://mrcoles.com/bookmarklet/ */

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