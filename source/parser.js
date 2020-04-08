var reader = new FileReader();
var eqData;

window.onload = function (e) {
    this.console.info('Parser loaded successfully');
    var fileInput = this.document.getElementsByClassName('file__select')[0];

    if (this.hasFSCompat()) {
        console.info('File APIs fully supported, parser will work');
        fileInput.addEventListener('change', handleFile, false);
        /** TODO: Better naming convention for functions */
        this.fetchJSON();
    } else {
        console.error('The File APIs are not fully supported in this browser, this parser will not work otherwise.');
    }
}

function hasFSCompat () {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        return true;
    } else {
        return false;
    }
}

var template = ``;

/*
 * @name: Handle Colors
 * @param: var val The string to modify
 * @param: object searchreplace An object containing the key:value pairs of strings to search and replace with
 * @desc: Given a string, it replaces all instances of KEY with VALUE
 * @example: handleColors ('test value with extra test', {"test": "sneaky"})
 */
function handleColors (val, searchreplace) {
    var mod = val;

    if (typeof searchreplace === 'object') {
        for (let [key, value] of Object.entries(searchreplace)) {
            /** This is the only way I knew of to pass a variable to Regex */
            mod = mod.replace(new RegExp(key, 'g'), value);
        }
    }

    return mod;
}

function handleFile (evt) {
    var file = evt.target.files[0];
    var fileObject = document.getElementsByClassName('file__object')[0];

    fileObject.innerHTML = file.name;

    readAsText(file);

    var data;

    reader.addEventListener('load', function (evt) {
        data = JSON.parse(evt.target.result);

        /** TODO: Make this iterate throughout entire Equipment collection */
        eqData = data.equipment[0];
    });

    //console.log(file);
    
}

function readAsText (file) {
    reader.readAsText(file, 'UTF-8');
    reader.onprogress = function (evt) {
        if (evt.lengthComputable) {
            var loaded = (evt.loaded / evt.total);

            if (loaded < 1) {
                console.log(loaded);
            }
        }
    };
    reader.onload = function (evt) {
        var fileString = evt.target.result;

        var JSONObject = JSON.parse(fileString);
    };
    reader.onerror = function (evt) {
        if (evt.target.error.name === 'NotReadableError') {
            console.error('File could not be read');
        }
    };
}

function fetchJSON () {
    // Grab JSON file from current directory
    /** TODO: Automatically grab JSON files instead of relying on input */
    var fileContent = document.getElementsByClassName('file__content')[0];
        fileContent.innerHTML = template;

    equipmentKeys = Object.keys(eq);
    resistancesKeys = Object.keys(eq.resistances);
    cyborgResKeys = Object.keys(eq.cyborgstats.resistances);

    /** TODO: Generate ACS and Language templates with these values */
    template = `
Actor:${eq.name}<br>
<br>
Name: ${eq.prettyname}<br>
<br>
Icon: ${eq.icon}<br>
<br>
Tier: ${eq.tier}<br>
<br>
Description: ${eq.description}<br>
<br>
Protection: ${eq.protection} (Renegade bonus: ${eq.renprotection})<br>
<br>
Resistances: <br>
    ${resistancesKeys[0]}: ${eq.resistances.melee}<br>
    ${resistancesKeys[1]}: ${eq.resistances.bullet}<br>
    ${resistancesKeys[2]}: ${eq.resistances.fire}<br>
    ${resistancesKeys[3]}: ${eq.resistances.plasma}<br>
    ${resistancesKeys[4]}: ${eq.resistances.cryo}<br>
    ${resistancesKeys[5]}: ${eq.resistances.electric}<br>
    ${resistancesKeys[6]}: ${eq.resistances.poison}<br>
    ${resistancesKeys[7]}: ${eq.resistances.radiation}<br>
<br>
Cyborg information: <br>
    Resistances: <br>
        ${cyborgResKeys[0]}: ${eq.cyborgstats.resistances.kinetic}<br>
        ${cyborgResKeys[1]}: ${eq.cyborgstats.resistances.thermal}<br>
        ${cyborgResKeys[2]}: ${eq.cyborgstats.resistances.refractor}<br>
        ${cyborgResKeys[3]}: ${eq.cyborgstats.resistances.organic}<br>
        ${cyborgResKeys[4]}: ${eq.cyborgstats.resistances.hazard}<br>
    Augment: ${eq.cyborgstats.augment}<br>
<br>
Attributes: <br>
    ${eq.attributes[0]}<br>
    ${eq.attributes[1]}<br>
    ${eq.attributes[2]}<br>
    ${eq.attributes[3]}<br>
    ${eq.attributes[4]}<br>
    ${eq.attributes[5]}<br>
    ${eq.attributes[6]}<br>
    ${eq.attributes[7]}<br>
    ${eq.attributes[8]}<br>
`;

    /** TODO: Be able to save/export templates as the appropriate files */

    console.log(eq);
    console.log(equipmentKeys);
    console.log(resistancesKeys);

    console.info('JSON loaded');
}