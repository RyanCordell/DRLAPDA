'use strict';

import { printDebugLine } from './utils.js';
import { globalFileList } from './base.js';

let reader = new FileReader();

export const hasFSCompat = () => {
    return window.File && window.FileReader && window.FileList && window.Blob;
}
/*
export const handleWeaponLanguage = (evt) => {
    var read = evt.target.files[0];

    readAsText(read);

    reader.addEventListener('load', function (evt) {
        parseWeaponLanguage(evt.target.result);
    });
}

export const handleModHeader = (evt) => {
    var read = evt.target.files[0];

    readAsText(read);

    reader.addEventListener('load', function (evt) {
        parseHeader(evt.target.result);
    });
}

export const handleModLanguage = (evt) => {
    var read = evt.target.files[0];

    readAsText(read);

    reader.addEventListener('load', function (evt) {
        parseModLanguage(evt.target.result);
    });
}
*/
export function handleFile () {
    const fileList = this.files;

    if (!fileList) return;

    for (let i = 0, len = fileList.length; i < len; i++) {
        globalFileList.push(fileList[i]);
    }
}

export const processFile = (file) => {
    readAsText(file, file.name);

    if (file.name) {
        printDebugLine('Reading file: ' + file.name);
    } else {
        printDebugLine('File name somehow missing');
    }

    let data;

    // Bitches love asynchronous data.
    return new Promise((resolve, reject) => {
        reader.addEventListener('load', function (evt) {
            printDebugLine('Parsing JSON for file ' + file.name + ', this might take a while!');
            /** 'Allow' for newlines in JSON */
            data = evt.target.result.replace(/\\n(\r\n|\n|\r)/g, '\\n');
            /** NOW actually parse */
            data = JSON.parse(data);
    
            resolve(data);
        });
    }).catch(err => console.error(err));
}

const readAsText = (file, name) => {
    /** Reinitialize to handle multiple files. There might be a better way than this though...? */

    if (file) {
        return new Promise((resolve, reject) => {
            reader = new FileReader();
            let loaded;

            reader.readAsText(file, 'UTF-8');
            reader.onprogress = function (evt) {
                if (evt.lengthComputable) {
                    loaded = (evt.loaded / evt.total);

                    if (loaded < 1) {
                        printDebugLine('Loaded file ' + name + ' in: ' + loaded + 'ms');
                    }
                }
            };
            reader.onload = function (evt) {
                let fileString = evt.target.result;
                printDebugLine('Loaded file ' + name + ' in: ' + loaded + 'ms');

                resolve(fileString);
            };
            reader.onerror = function (evt) {
                if (evt.target.error.name === 'NotReadableError') {
                    printDebugLine('!! FILE COULD NOT BE READ !!' + evt.target.error);
                    console.error('!! FILE COULD NOT BE READ !!', evt.target.error);
                }
                reject(evt.target.error);
            };
        }).catch(err => console.error(err));
    } else {
        throw err('ERROR: File not found or premature cache purge');
    }
}
