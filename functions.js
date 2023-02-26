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
