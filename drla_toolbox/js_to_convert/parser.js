'use strict';

import { getEle, printDebugLine } from './utils.js';
import { PDA_MOD, PDA_ARM, PDA_ASM, LANGUAGE_EQUIPMENT, LANGUAGE_WEAPONS, LANGUAGE_ASSEMBLIES } from './templates.js';

let outputDownload = {};

let template = ``;

let weaponModList = [];
let equipmentList = [];
let assemblyList = [];
let assemble = [];
let modEffects = [];
let language_warning = `[enu default]\n\n// Please do not modify this file directly, it's specifically compiled and any changes may be lost.\n\n`;

window.onload = function () {
    outputDownload = getEle('output__field');
}

export const parseJSON = (value) => {
    if (value.length < 1) return;

    let jsonObj = {};
    value.map(obj => Object.assign(jsonObj, obj));

    equipmentJSONParse(jsonObj);
    weaponJSONParse(jsonObj);
    modEffectJSONParse(jsonObj);
    assembliesJSONParse(jsonObj);
    
    printDebugLine('Task failed successfully! :D');
}

export const generateDownload = (filename, text) => {
    console.time('Download generation');
    
    let element = document.createElement('a');
    element.setAttribute('id', filename);
    element.text = `Download ${filename}`;
    element.setAttribute('class', 'output__download');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
  
    let outputDownload = getEle('output__field', false);
    if (outputDownload.length > 0) outputDownload[0].appendChild(element);
    
    console.timeEnd('Download generation');
}

const weaponJSONParse = (value) => {
    if (!value) return;
    if (!value.hasOwnProperty('weapons')) return;

    console.time('Weapons');
    printDebugLine('Parsing WEAPONS database');
    let weaponModEffects = ``;
    let weaponModMax = 0;
    let demonicWeapons = 0;
    let demonicArtifacts = ``;
    let weaponLanguage = ``;
    let basicModMax = 0,
        advancedModMax = 0,
        masterModMax = 0;
    let weaponDescription = '';
    
    printDebugLine('Reading weapons...');
    value.weapons.forEach(weapon => {
        weapon.actualDescription = '';

        if (weapon.mods) {
            weaponModEffects = weaponModEffects.concat(`{ "RL${weapon.name}", "${weapon.mods.bulk}", "${weapon.mods.power}", "${weapon.mods.agility}", "${weapon.mods.technical}", "${weapon.mods.sniper}", "${weapon.mods.firestorm}", "${weapon.mods.nano}"},`);
            weaponModMax++;
        }
        if (weapon.corruptions) {
            demonicArtifacts = demonicArtifacts.concat(`{ "RL${weapon.name}", "${weapon.corruptions[0]}", "${weapon.corruptions[1]}", "${weapon.corruptions[2]}"},`)
            demonicWeapons++;
        }

        if (weapon.tier === 'Basic') basicModMax++;
        if (weapon.tier === 'Advanced') advancedModMax++;
        if (weapon.tier === 'Master') masterModMax++;

        if (Array.isArray(weapon.description)) {
            for (let i = 0, len = weapon.description.length; i < len; i++) {
                weapon.actualDescription += weapon.description[i];
            }
        }

        weaponLanguage = weaponLanguage.concat(LANGUAGE_WEAPONS(weapon));
    });
    printDebugLine('Weapons translated to language');

    /** PDA_MOD */
    weaponModList.push({
        max: weaponModMax,
        list: weaponModEffects,
        dmax: demonicWeapons,
        dlist: demonicArtifacts,
        basicmax: basicModMax,
        advancedmax: advancedModMax,
        mastermax: masterModMax
    });
    generateDownload('modeffects.idb', PDA_MOD(weaponModList[0]));

    /** LANGUAGE.WEAPONS */
    printDebugLine('Transforming JSON colors into ZDoom colors');
    weaponLanguage = revertColors(value, weaponLanguage);

    /** Strip readability for language */
    printDebugLine('Minifying and tidying up Language output');
    weaponLanguage = weaponLanguage.replaceAll('[INNERQUOTE]', '\\"');
    weaponLanguage = weaponLanguage
    .replace(/(\n)/g, '\\n')
    .replace(/(;)\\n/gm, ';')
    .replace(/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm, '')
    .replace(/( {3,})\\n/gm, '')
    .replace(/^\\n( {1,})/gm, '');
    
    printDebugLine('Generating WEAPONS language lump');
    console.timeEnd('Weapons');
    generateDownload('language.auto.weapons', language_warning.concat(weaponLanguage));
};

const equipmentJSONParse = (value) => {
    if (!value) return;
    if (!value.hasOwnProperty('equipment')) return;

    console.time('Equipment');
    printDebugLine('Parsing EQUIPMENT database');
    var headerArmorList = ``;
    var languageArmorList = ``;
    var equipmentMax = 0;

    printDebugLine('Reading EQUIPMENT...');
    value.equipment.forEach(item => {
        headerArmorList = headerArmorList.concat(`{"RL${item.name}", "${item.name.toUpperCase()}"},`);
        equipmentMax++;

        /** Pipe into language */
        languageArmorList = languageArmorList.concat(LANGUAGE_EQUIPMENT(value, item));
    });
    
    /** Pipes into PDA_ARM */
    printDebugLine('Creating ACS array list for EQUIPMENT');
    equipmentList.push({
        max: equipmentMax,
        list: headerArmorList
    });
    generateDownload('equipment.idb', PDA_ARM(equipmentList[0]));

    /** Replace all language pointers with their contents */
    printDebugLine('Transforming unique LANGUAGE KEYWORDS into attributes');
    if (value.hasOwnProperty('attributes')) {
        for(let [key, value] of Object.entries(value.attributes)) {
            languageArmorList = languageArmorList.replace(new RegExp(key, 'g'), value);
        }
    }

    /** LANGUAGE.WEAPONS */
    printDebugLine('Transforming JSON colors into ZDoom colors');
    languageArmorList = languageArmorList.replace(/(\n)/g, '\\n').replace(/(;)\\n/gm, ';').replace(/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm, '');
    languageArmorList = revertColors(value, languageArmorList);
    
    printDebugLine('Generating EQUIPMENT language lump');
    console.timeEnd('Equipment');
    generateDownload('language.auto.equipment', language_warning.concat(languageArmorList));
}

const modEffectJSONParse = (value) => {
    if (!value) return;
    if (!value.hasOwnProperty('modeffect')) return;

    printDebugLine('Parsing MOD EFFECTS database');
    var modEffectList = language_warning;

    value.modeffect.forEach(modeffect => {
        modEffectList = modEffectList.concat(`${modeffect.name} = "${modeffect.effect}";`);
    });

    modEffectList = revertColors(value, modEffectList);
    generateDownload('language.auto.mods', modEffectList);
}

const assembliesJSONParse = (value) => {
    if (!value) return;
    if (!value.hasOwnProperty('assemblies')) return;

    console.time('Assemblies');
    printDebugLine('Parsing ASSEMBLIES database');
    let headerAssemblyList = ``;
    let headerAssemblyMax = 0;
    let headerUniqueMax = 0;
    let headerExoticList = ``;
    let languageAssemblyList = ``;
    let basicMax = 0,
        advancedMax = 0,
        masterMax = 0;

    printDebugLine('Reading ASSEMBLIES...');
    value.assemblies.forEach(assembly => {
        headerAssemblyList = headerAssemblyList.concat(`{"RL${assembly.name}AssemblyLearntToken", "PDA_ASSEMBLY_${assembly.tier.toUpperCase()}_${assembly.name.toUpperCase()}"},`);
        headerAssemblyMax++;

        if (assembly.tier === 'Basic') basicMax++;
        if (assembly.tier === 'Advanced') advancedMax++;
        if (assembly.tier === 'Master') masterMax++;

        /** LANGUAGE */
        languageAssemblyList = languageAssemblyList.concat(LANGUAGE_ASSEMBLIES(value, assembly));
    });

    printDebugLine('Minifying output and transforming JSON colors into ZDoom colors');
    languageAssemblyList = languageAssemblyList.replace(/(\n)/g, '\\n').replace(/(;)\\n/gm, ';').replace(/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm, '');
    languageAssemblyList = revertColors(value, languageAssemblyList);
    
    printDebugLine('Generating ASSEMBLIES language lump');
    generateDownload('language.auto.assemblies', language_warning.concat(languageAssemblyList));

    /** PDA_ASM */
    printDebugLine('Creating ACS table for weapon assemblies & exotic effects');
    if (value.hasOwnProperty('weapons')) {
        value.weapons.forEach(weapon => { 
            if (weapon.tier === 'Unique' || weapon.tier === 'Demonic' || weapon.tier === 'Legendary') {
                if (weapon.unmoddable) {
                    headerExoticList = headerExoticList.concat(`{"RL${weapon.name}", "null", "null", "null"},`);
                }
                else {
                    headerExoticList = headerExoticList.concat(`{"RL${weapon.name}", "RL${weapon.name}SniperLearntToken", "RL${weapon.name}FirestormLearntToken", "RL${weapon.name}NanoLearntToken"},`);
                }
                headerUniqueMax++;
            }
        });
    }

    assemblyList.push({
        max: headerAssemblyMax,
        list: headerAssemblyList,
        uniquemax: headerUniqueMax,
        basicmax: basicMax,
        advancedmax: advancedMax,
        mastermax: masterMax,
        exotics: headerExoticList
    });
    console.log(assemblyList);

    printDebugLine('Generating ASSEMBLIES ACS lump');
    console.timeEnd('Assemblies');
    generateDownload('assemblies.idb', PDA_ASM(assemblyList[0]))
}

/** 
 * @name: Handle Colors
 * @param: var val The string to modify
 * @param: object searchreplace An object containing the key:value pairs of strings to search and replace with
 * @desc: Given a string, it replaces all instances of KEY with VALUE
 * @example: handleColors('test value with extra test', {"test": "sneaky"})
 */
export const handleColors = (val, searchreplace) => {
    if (typeof searchreplace !== 'object') return false;

    let mod = val;

    for (let [key, value] of Object.entries(searchreplace)) {
        /** This is the only way I knew of to pass a variable to Regex */
        mod = mod.replace(new RegExp(key, 'g'), value);
    }

    return mod;
}

/** 
 * @name: Revert colors
 * @param: var str The string to modify
 * @desc: Given a string, it goes through and changes all known instances of a string from the left to the right one
 * @example: revertColors("\cdThis is a unique weapon\c-")
 */
export const revertColors = (value, str) => {
    if (!str) return 'No data found to process'
    if (!value.hasOwnProperty('colors')) return 'No such property found: colors';

    for(let [key, value] of Object.entries(value.colors)) {
        str = str.replace(new RegExp('\\['+key+'\\]', 'g'), `\\c${value}`);
    }

    return str;
}

/** 
 * @name: Filter characters
 * @param: var str The string to modify
 * @desc: Given a string, it goes through and changes all known instances of a string from the left to the right one
 * @example: filterCharacters("\cdThis is a unique weapon\c-")
 */
export const filterCharacters = (str) => {
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

/** No longer necessary */
/*
export const parseWeaponLanguage = (file) => {
    const lines = file.split('\n');
    var name = '';
    var tier = '';
    var capacity = '';
    var prettyname = '';
    var desc = '';

    for(var line = 0; line < lines.length; line++) {
        let thisLine = lines[line];
        if (thisLine.startsWith('[enu') || thisLine.startsWith('//') || thisLine.startsWith('\n') || thisLine == '' || thisLine.match(/	(?!")/g)) continue;
        if (thisLine.startsWith('PDA_') && thisLine.includes('_NAME') && !thisLine.includes('DEMONARTIFACTS_')) {
            name = thisLine.replace('PDA_WEAPON_', '').replace('_NAME =\r', '').replace('_NAME = \r', '');

            if (lines[line+1] != '') {
                prettyname = lines[line+1];
                prettyname = filterCharacters(prettyname);
                prettyname = prettyname.replace(/\"/g, '');
                prettyname = prettyname.replace(/\];/g, ']');
                continue;
            }
        }
        //  Do some description shenanigans
        if (thisLine.startsWith('PDA_') && thisLine.includes('_DESC') && !thisLine.includes('DEMONARTIFACTS_')) {
            for (var l = 0; l < 20; l++) {
                var nextLine = lines[line+l];
                if (nextLine === '\r' || thisLine.match(/	(?!")/g)) break;
                if (nextLine.startsWith('PDA_')) continue;
                if (thisLine.startsWith('[enu') || thisLine.startsWith('//') || thisLine.startsWith('\n') || thisLine == '') continue;

                console.log(nextLine);
                if (nextLine != '') desc = desc.concat(nextLine);
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

            assemble.push({name, tier, prettyname, capacity, desc});
            tier = '';
            prettyname = '';
            capacity = '';
            desc = '';
        }

        // Try and filter out any duplicates
        assemble = [...new Set(assemble)];
    }
    //console.log(assemble);
}

export const parseModLanguage = (file) => {
    var lines = file.split('\n');
    var name = '';
    var effect = '';

    for(var line = 0; line < lines.length; line++) {
        let thisLine = lines[line];
        if (thisLine.startsWith('[enu') || thisLine.startsWith('//') || thisLine.startsWith('\n') || thisLine == '' || thisLine.match(/	(?!")/g)) continue;
        if (thisLine.startsWith('PDA_MODS_')) {
            name = thisLine.replace(' =\r', '').replace(' = \r', '');

            if (lines[line+1] !== '') {
                for (var l = 1; l < 6; l++) {
                    let thisLinel = lines[line+l];
                    if (thisLinel != '' && !thisLinel.startsWith('PDA_MODS')) effect = effect.concat(thisLinel);
                    if (thisLinel.match(/(";)/g)) break;
                    //if (lines[line+l] === '\r' || lines[line+l].match(/	(?!")/g) || lines[line+l].match(/(";)/g) || lines[line+l].startsWith('PDA_')) break;
                    
                    //if (lines[line+l].startsWith('PDA_')) continue;
                    //if (lines[line+l].startsWith('[enu') || lines[line+l].startsWith('//') || lines[line+l].startsWith('\n') || lines[line+l] == '') continue;
    
                    console.log(thisLinel);
                    
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
            modEffects.push({name, effect});
            name = '';
            effect = '';
        }
    }
}

export const parseHeader = (file) => {
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
                    
                    if (an == n) {
                        if (!lines[line+1].includes("ARTIFACT")) {
                            var bulk      = lines[line+1].replace('					"', '').replace('",\r', '');
                            var power     = lines[line+2].replace('					"', '').replace('",\r', '');
                            var agility   = lines[line+3].replace('					"', '').replace('",\r', '');
                            var technical = lines[line+4].replace('					"', '').replace('",\r', '');
                            var sniper    = lines[line+5].replace('					"', '').replace('",\r', '');
                            var firestorm = lines[line+6].replace('					"', '').replace('",\r', '');
                            var nano      = lines[line+7].replace('					"', '').replace('",\r', '').replace('"},\r', '');
                            assemble[i].mods = {bulk, power, agility, technical, sniper, firestorm, nano};
                        }
                    }
                    else continue;
                }
            }
        }
        else {
            continue;
        }
    }
}
*/
