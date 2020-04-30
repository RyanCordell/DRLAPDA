var eqData;
var fileList = [];
var fileInput, fileProcess;

window.pdaglobals = {};

window.onload = function (e) {
    fileInput = this.document.getElementsByClassName('file__select')[0];
    fileProcess = this.document.getElementById('file-field');
    var that = this;
    var weaponLangInput = this.document.getElementsByClassName('language-weapon__select')[0];
    var modHeaderInput = this.document.getElementsByClassName('header-mod__select')[0];
    var modLangInput = this.document.getElementsByClassName('language-mod__select')[0];

    if (this.hasFSCompat()) {
        console.info('File APIs fully supported, parser will work');
        /** TODO: Once processed, make the files downloadable */
        fileInput.addEventListener('change', handleFile, false);

        fileProcess.addEventListener('submit', function (evt) {
            evt.preventDefault();
            fileList.forEach(function (file) {
                processFile(file);
            });
            console.log(window.pdaglobals);
            /** Necessary to have it read the global variable properly */
            setTimeout(parseJSON, 100);
        });

        /* weaponLangInput.addEventListener('change', handleWeaponLanguage, false);
        modHeaderInput.addEventListener('change', handleModHeader, false);
        modLangInput.addEventListener('change', handleModLanguage, false); */
        //readInput.addEventListener('change', handleRead, false);
        /** TODO: Better naming convention for functions */
        //this.fetchJSON();
    } else {
        console.error('The File APIs are not fully supported in this browser, this parser will not work otherwise.');
    }
    this.console.info('Parser.js loaded successfully');
}

var template = ``;

function parseJSON () {
    if (Object.keys(window.pdaglobals).length < 1) return;

    if (window.pdaglobals.hasOwnProperty('weapons')) {
        var weaponModEffects = ``;
        var weaponModMax = 0;
        var demonicWeapons = 0;
        var demonicArtifacts = ``;
        
        window.pdaglobals.weapons.forEach(weapon => {
            if (weapon.mods) {
                weaponModEffects = weaponModEffects.concat(`{ "RL${weapon.name}", "${weapon.mods.bulk}", "${weapon.mods.power}", "${weapon.mods.agility}", "${weapon.mods.technical}", "${weapon.mods.sniper}", "${weapon.mods.firestorm}", "${weapon.mods.nano}"},`);
                weaponModMax++;
            }
            if (weapon.corruptions) {
                demonicArtifacts = demonicArtifacts.concat(`{ "RL${weapon.name}", "${weapon.corruptions[0]}", "${weapon.corruptions[1]}", "${weapon.corruptions[2]}"},`)
                demonicWeapons++;
            }
        });
        weaponModList.push(new weaponModListing(weaponModMax, weaponModEffects, demonicWeapons, demonicArtifacts));
        //console.log(PDA_MOD(weaponModList[0]));
        //console.log("DRLA_WEAPONMODLIST: { \"RL" + data.weapons[0].name + "\", \"" + data.weapons[0] +"\",}");
    }
    
    if (pdaglobals.hasOwnProperty('equipment')) {
        var headerArmorList = ``;
        var languageArmorList = `[enu default]\n\n// Please do not modify this file directly, it's specifically compiled and any changes may be lost.\n\n`;
        var equipmentMax = 0;

        window.pdaglobals.equipment.forEach(item => {
            headerArmorList = headerArmorList.concat(`{"RL${item.name}", "${item.name}"},`);
            equipmentMax++;

            languageArmorList = languageArmorList.concat(LANGUAGE_EQUIPMENT(item));
        });

        for(let [key, value] of Object.entries(window.pdaglobals.attributes))
        {
            languageArmorList = languageArmorList.replace(new RegExp(key, 'g'), value);
        }
        //languageArmorList
        console.log(languageArmorList);

        equipmentList.push(new equipmentListing(equipmentMax, headerArmorList));
        //console.log(PDA_ARM(equipmentList[0]));
        //console.log(languageArmorList);
        /** TODO: This needs to pipe into: LANGUAGE.ARMORS, PDA_ARM (actor name and language entry) */
    }

    if (window.pdaglobals.hasOwnProperty('modeffect')) {
        var modEffectList = `[enu default]\n\n// Please do not modify this file directly, it's specifically compiled and any changes may be lost.\n\n`;

        window.pdaglobals.modeffect.forEach(modeffect => {
            modEffectList = modEffectList.concat(`${modeffect.name} = "${modeffect.effect.replace('\\n', '\n')}";`);
        });

        //console.log(modEffectList);
    }
}

function fetchJSON () {
    // Grab JSON file from current directory
    /** TODO: Automatically grab JSON files instead of relying on input */
    var fileContent = document.getElementsByClassName('file__content')[0];
        fileContent.innerHTML = template;

    equipmentKeys = Object.keys(eqData);
    resistancesKeys = Object.keys(eqData.resistances);
    cyborgResKeys = Object.keys(eqData.cyborgstats.resistances);

    /** TODO: Generate ACS and Language templates with these values */
    template = `
Actor:${eqData.name}<br>
<br>
Name: ${eqData.prettyname}<br>
<br>
Icon: ${eqData.icon}<br>
<br>
Tier: ${eqData.tier}<br>
<br>
Description: ${eqData.description}<br>
<br>
Protection: ${eqData.protection} (Renegade bonus: ${eqData.renprotection})<br>
<br>
Resistances: <br>
    ${resistancesKeys[0]}: ${eqData.resistances.melee}<br>
    ${resistancesKeys[1]}: ${eqData.resistances.bullet}<br>
    ${resistancesKeys[2]}: ${eqData.resistances.fire}<br>
    ${resistancesKeys[3]}: ${eqData.resistances.plasma}<br>
    ${resistancesKeys[4]}: ${eqData.resistances.cryo}<br>
    ${resistancesKeys[5]}: ${eqData.resistances.electric}<br>
    ${resistancesKeys[6]}: ${eqData.resistances.poison}<br>
    ${resistancesKeys[7]}: ${eqData.resistances.radiation}<br>
<br>
Cyborg information: <br>
    Resistances: <br>
        ${cyborgResKeys[0]}: ${eqData.cyborgstats.resistances.kinetic}<br>
        ${cyborgResKeys[1]}: ${eqData.cyborgstats.resistances.thermal}<br>
        ${cyborgResKeys[2]}: ${eqData.cyborgstats.resistances.refractor}<br>
        ${cyborgResKeys[3]}: ${eqData.cyborgstats.resistances.organic}<br>
        ${cyborgResKeys[4]}: ${eqData.cyborgstats.resistances.hazard}<br>
    Augment: ${eqData.cyborgstats.augment}<br>
<br>
Attributes: <br>
    ${eqData.attributes[0]}<br>
    ${eqData.attributes[1]}<br>
    ${eqData.attributes[2]}<br>
    ${eqData.attributes[3]}<br>
    ${eqData.attributes[4]}<br>
    ${eqData.attributes[5]}<br>
    ${eqData.attributes[6]}<br>
    ${eqData.attributes[7]}<br>
    ${eqData.attributes[8]}<br>
`;

    /** TODO: Be able to save/export templates as the appropriate files */

    console.info('JSON loaded');
}

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

/** Temp */
function filterCharacters (str) {
    /** Strip out all control characters and some quotation marks to better merge strings */
    str = str.replace(/[^\x20-\x7E]/g, '');
    str = str.replace(/\\n""/g, '\n');
    str = str.replace(/\"\x20\x20\x20\x20\"/g, '');
    /** End stripping */
    /** Replace existing ACS print codes with JSON-friendly color codes */
    str = str.replace('\\c[DarkGreen]', '[DARKGREEN]');
    str = str.replace('\\c[Green]', '[DARKGREEN]');
    str = str.replace('\\c[Yellow]', '[YELLOW]');
    str = str.replace('\\c[Red]', '[RED]');
    str = str.replace('\\c[Orange]', '[ORANGE]');
    str = str.replace('\\c[White]', '[WHITE]');
    str = str.replace('\\c[Purple]', '[PURPLE]');
    str = str.replace('\\c[LightBlue]', '[LIGHTBLUE]');
    str = str.replace('\\c[BB]', '[BASIC]');
    str = str.replace('\\c[AB]', '[ADVANCED]');
    str = str.replace('\\c[MB]', '[MASTER]');
    str = str.replace('\\c[WN]', '[NORMAL]');
    str = str.replace('\\c[WE]', '[EXOTIC]');
    str = str.replace('\\c[WS]', '[SUPERIOR]');
    str = str.replace('\\c[WD]', '[DEMONIC]');
    str = str.replace('\\c[WU]', '[UNIQUE]');
    str = str.replace('\\c[WL]', '[LEGENDARY]');
    str = str.replace('\\c[BM]', '[BULK]');
    str = str.replace('\\c[PM]', '[POWER]');
    str = str.replace('\\c[AM]', '[AGILITY]');
    str = str.replace('\\c[TM]', '[TECH]');
    str = str.replace('\\c[SM]', '[SNIPER]');
    str = str.replace('\\c[FM]', '[FIRESTORM]');
    str = str.replace('\\c[NM]', '[NANO]');
    str = str.replace('\\c[OM]', '[ONYX]');
    str = str.replace('\\ca', '[BRICK]');
    str = str.replace('\\cb', '[TAN]');
    str = str.replace('\\cc', '[GRAY]');
    str = str.replace('\\cd', '[GREEN]');
    str = str.replace('\\ce', '[BROWN]');
    str = str.replace('\\cf', '[GOLD]');
    str = str.replace('\\cg', '[RED]');
    str = str.replace('\\ch', '[BLUE]');
    str = str.replace('\\ci', '[ORANGE]');
    str = str.replace('\\cj', '[WHITE]');
    str = str.replace('\\ck', '[YELLOW]');
    str = str.replace('\\cl', '[INHERIT]');
    str = str.replace('\\cm', '[BLACK]');
    str = str.replace('\\cn', '[LIGHTBLUE]');
    str = str.replace('\\co', '[CREAM]');
    str = str.replace('\\cp', '[OLIVE]');
    str = str.replace('\\cq', '[DARKGREEN]');
    str = str.replace('\\cr', '[DARKRED]');
    str = str.replace('\\cs', '[DARKBROWN]');
    str = str.replace('\\ct', '[PURPLE]');
    str = str.replace('\\cu', '[DARKGRAY]');
    str = str.replace('\\cv', '[CYAN]');
    str = str.replace('\\cw', '[ICE]');
    str = str.replace('\\cx', '[FIRE]');
    str = str.replace('\\cy', '[SAPPHIRE]');
    str = str.replace('\\cz', '[TEAL]');
    str = str.replace(/\\c-/g, '[END]');
    str = str.replace(/(\\"\[)/g, '[');
    str = str.replace(/(\]\\")/g, ']');
    /** End color coding */

    return str;
}

var assemble = [];

function weaponDef (wname, wtier, wpretty, wcapacity, wdesc) {
    this.name = wname;
    this.tier = wtier;
    this.prettyname = wpretty;
    this.capacity = wcapacity;
    this.description = wdesc;
}

function parseWeaponLanguage (file) {
    var lines = file.split('\n');
    var name = '';
    var tier = '';
    var capacity = '';
    var prettyname = '';
    var desc = '';
    for(var line = 0; line < lines.length; line++) {
        if (lines[line].startsWith('[enu') || lines[line].startsWith('//') || lines[line].startsWith('\n') || lines[line] == '' || lines[line].match(/	(?!")/g)) continue;
        if (lines[line].startsWith('PDA_') && lines[line].includes('_NAME') && !lines[line].includes('DEMONARTIFACTS_')) {
            name = lines[line].replace('PDA_WEAPON_', '').replace('_NAME =\r', '').replace('_NAME = \r', '');

            if (lines[line+1] != '') {
                prettyname = lines[line+1];
                prettyname = filterCharacters(prettyname);
                prettyname = prettyname.replace(/\"/g, '');
                prettyname = prettyname.replace(/\];/g, ']');
                continue;
            }
        }
        if (lines[line].startsWith('PDA_') && lines[line].includes('_DESC') && !lines[line].includes('DEMONARTIFACTS_')) {
            for (var l = 0; l < 20; l++) {
                if (lines[line+l] === '\r' || lines[line].match(/	(?!")/g)) break;
                if (lines[line+l].startsWith('PDA_')) continue;
                if (lines[line].startsWith('[enu') || lines[line].startsWith('//') || lines[line].startsWith('\n') || lines[line] == '') continue;

                if (lines[line+l] != '') desc = desc.concat(lines[line+l]);
            }
            if (desc !== '') {
                desc = filterCharacters(desc);
                desc = desc.replace(/\"(;?)/g, '');
                continue;
            }
        }
        if (name != '' && desc != '') {
                 if(prettyname.includes("NORMAL")   ) { tier = 'Standard';  capacity = 'FOUR_MOD_CAPACITY'; }
            else if(prettyname.includes("EXPTOC")   ) { tier = 'Exotic';    capacity = 'FOUR_MOD_CAPACITY'; }
            else if(prettyname.includes("SUPERIOR") ) { tier = 'Superior';  capacity = 'TWO_MOD_CAPACITY';  }
            else if(prettyname.includes("UNIQUE")   ) { tier = 'Unique';    capacity = 'ONE_MOD_CAPACITY';  }
            else if(prettyname.includes("LEGENDARY")) { tier = 'Legendary'; capacity = 'ONE_MOD_CAPACITY';  }
            else if(prettyname.includes("DEMONIC")  ) { tier = 'Demonic';   capacity = 'FOUR_MOD_CAPACITY'; }
            else if(prettyname.includes("BASIC")    ) { tier = 'Basic';     capacity = 'TWO_MOD_CAPACITY';  }
            else if(prettyname.includes("ADVANCED") ) { tier = 'Advanced';  capacity = 'ONE_MOD_CAPACITY';  }
            else if(prettyname.includes("MASTER")   ) { tier = 'Master';    capacity = 'ZERO_MOD_CAPACITY'; }

            assemble.push(new weaponDef(name, tier, prettyname, capacity, desc));
            tier = '';
            prettyname = '';
            capacity = '';
            desc = '';
        }

        /** Try and filter out any duplicates */
        assemble = [...new Set(assemble)];
    }
    //console.log(assemble);
}

function modDef (wname, weffect) {
    this.name = wname;
    this.effect = weffect;
}

var modEffects = [];

function parseModLanguage (file) {
    var lines = file.split('\n');
    var name = '';
    var effect = '';

    for(var line = 0; line < lines.length; line++) {
        if (lines[line].startsWith('[enu') || lines[line].startsWith('//') || lines[line].startsWith('\n') || lines[line] == '' || lines[line].match(/	(?!")/g)) continue;
        if (lines[line].startsWith('PDA_MODS_')) {
            name = lines[line].replace(' =\r', '').replace(' = \r', '');

            if (lines[line+1] != '') {
                for (var l = 1; l < 6; l++) {
                    if (lines[line+l] != '' && !lines[line+l].startsWith('PDA_MODS')) effect = effect.concat(lines[line+l]);
                    if (lines[line+l].match(/(";)/g)) break;
                    //if (lines[line+l] === '\r' || lines[line+l].match(/	(?!")/g) || lines[line+l].match(/(";)/g) || lines[line+l].startsWith('PDA_')) break;
                    
                    //if (lines[line+l].startsWith('PDA_')) continue;
                    //if (lines[line+l].startsWith('[enu') || lines[line+l].startsWith('//') || lines[line+l].startsWith('\n') || lines[line+l] == '') continue;
    
                    //console.log(lines[line+l]);
                    
                }
                //console.log(name, effect);
                if (effect !== '') {
                    effect = filterCharacters(effect);
                    effect = effect.replace(/\"/g, '');
                    effect = effect.replace(/\];/g, ']');
                    effect = effect.replace(/\"(;?)/g, '');
                    continue;
                }
            }
        }
        //console.log(name, effect);
        if (name != '' && effect != '') {
            modEffects.push(new modDef(name, effect));
            name = '';
            effect = '';
        }
        /*
        if (lines[line].startsWith('PDA_') && lines[line].includes('_DESC')) {
            
        }
        if (name != '' && desc != '') {
                 if(prettyname.includes("NORMAL")   ) { tier = 'Standard';  capacity = 'FOUR_MOD_CAPACITY'; }
            else if(prettyname.includes("EXPTOC")   ) { tier = 'Exotic';    capacity = 'FOUR_MOD_CAPACITY'; }
            else if(prettyname.includes("SUPERIOR") ) { tier = 'Superior';  capacity = 'TWO_MOD_CAPACITY';  }
            else if(prettyname.includes("UNIQUE")   ) { tier = 'Unique';    capacity = 'ONE_MOD_CAPACITY';  }
            else if(prettyname.includes("LEGENDARY")) { tier = 'Legendary'; capacity = 'ONE_MOD_CAPACITY';  }
            else if(prettyname.includes("DEMONIC")  ) { tier = 'Demonic';   capacity = 'FOUR_MOD_CAPACITY'; }
            else if(prettyname.includes("BASIC")    ) { tier = 'Basic';     capacity = 'TWO_MOD_CAPACITY';  }
            else if(prettyname.includes("ADVANCED") ) { tier = 'Advanced';  capacity = 'ONE_MOD_CAPACITY';  }
            else if(prettyname.includes("MASTER")   ) { tier = 'Master';    capacity = 'ZERO_MOD_CAPACITY'; }

            assemble.push(new weaponDef(name, tier, prettyname, capacity, desc));
            tier = '';
            prettyname = '';
            capacity = '';
            desc = '';
        }

        assemble = [...new Set(assemble)];
        */
    }
    //console.log(modEffects);
}

function modsEffects (wbulk, wpower, wagility, wtechnical, wsniper, wfirestorm, wnano) {
    this.bulk = wbulk;
    this.power = wpower;
    this.agility = wagility;
    this.technical = wtechnical;
    this.sniper = wsniper;
    this.firestorm = wfirestorm;
    this.nano = wnano;
}

function parseHeader (file) {
    var lines = file.split('\n');
    var name;
    var assembleLength = assemble.length;
    
    for(var line = 0; line < lines.length; line++) {
        if (lines[line].includes("RL")) {
            name = lines[line].replace(/\W/g, '');

            if (assembleLength > 0) {
                for(var i = 0; i < assembleLength; i++) {
                    var an = assemble[i].name.toUpperCase();
                    var n = name.substring(2).toUpperCase();
                    //console.log(an, n, an == n);
                    
                    if (an == n) {
                        //console.log(lines[line+1], lines[line+2], lines[line+3], lines[line+4], lines[line+5], lines[line+6], lines[line+7]);
                        if (!lines[line+1].includes("ARTIFACT")) {
                            var bulk      = lines[line+1].replace('					"', '').replace('",\r', '');
                            var power     = lines[line+2].replace('					"', '').replace('",\r', '');
                            var agility   = lines[line+3].replace('					"', '').replace('",\r', '');
                            var technical = lines[line+4].replace('					"', '').replace('",\r', '');
                            var sniper    = lines[line+5].replace('					"', '').replace('",\r', '');
                            var firestorm = lines[line+6].replace('					"', '').replace('",\r', '');
                            var nano      = lines[line+7].replace('					"', '').replace('",\r', '').replace('"},\r', '');
                            assemble[i].mods = new modsEffects(bulk, power, agility, technical, sniper, firestorm, nano);
                        }
                    }
                    else continue;
                }
            }
        }
        else {
            continue;
        }
        //console.log(lines[line], lines[line].includes("RL"));
    }
    //console.log(assemble);
}