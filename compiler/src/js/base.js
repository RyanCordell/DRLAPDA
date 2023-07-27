'use strict';

import { getEle, getEleByID, printDebugLine } from './utils.js';
import { hasFSCompat, handleFile, processFile } from './freader.js';
import { parseJSON } from './parser.js';

window.onload = function () {
    const fileInput = getEle('file__select');
    const fileProcess = getEleByID('file-field');

    if (hasFSCompat()) {
        printDebugLine('File APIs fully supported, parser will work');
        fileInput.addEventListener('change', handleFile, false);

        fileProcess.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (globalFileList.length > 0) {
                await Promise.all(globalFileList.map(file => processFile(file)))
                    .then(value => parseJSON(value))
                    .catch(err => console.error(err));
            }
        });
    } else {
        console.error('The File APIs are not fully supported in this browser, this parser will not work otherwise.');
    }
    printDebugLine('Parser.js loaded successfully');
}

export let globalFileList = [];