var eqData;
var fileList = [];
var fileInput, fileProcess, outputDownload;

window.pdaglobals = {};

window.onload = function (e) {
    fileInput = this.document.getElementsByClassName('file__select')[0];
    fileProcess = this.document.getElementById('file-field');
    outputDownload = this.document.getElementsByClassName('output__field')[0];
    var that = this;
    var weaponLangInput = this.document.getElementsByClassName('language-weapon__select')[0];
    var modHeaderInput = this.document.getElementsByClassName('header-mod__select')[0];
    var modLangInput = this.document.getElementsByClassName('language-mod__select')[0];

    if (this.hasFSCompat()) {
        console.info('File APIs fully supported, parser will work');
        /** TODO: Once processed, make the files downloadable */
        fileInput.addEventListener('change', handleFile, false);

        /** TODO: Better naming convention for functions */
        fileProcess.addEventListener('submit', function (evt) {
            evt.preventDefault();
            fileList.forEach(function (file) {
                processFile(file);
            });
            /** Necessary to have it read the global variable properly */
            setTimeout(parseJSON, 100);
        });

        //this.fetchJSON();
    } else {
        console.error('The File APIs are not fully supported in this browser, this parser will not work otherwise.');
    }
    this.console.info('Parser.js loaded successfully');
}

var template = ``;


function generateDownload (filename, text) {
    var element = document.createElement('a');
    element.setAttribute('id', filename);
    element.text = `Download ${filename}`;
    element.setAttribute('class', 'output__download');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
  
    if (element.length != 1) outputDownload.appendChild(element);
}

var weaponModList = [];
var equipmentList = [];
var assemblyList = [];

function weaponModListing (max, list, dmax, dlist) {
    this.max = max;
    this.list = list;
    this.dmax = dmax;
    this.dlist = dlist;
}

function equipmentListing (max, list) {
    this.max = max;
    this.list = list;
}

function assemblyListing (max, list, uniquemax, sniper, firestorm, nano) {
    this.max = max;
    this.list = list;
    this.uniquemax = uniquemax;
    this.sniper = sniper;
    this.firestorm = firestorm;
    this.nano = nano;
}

function parseJSON () {
    if (Object.keys(window.pdaglobals).length < 1) return;

    var language_warning = `[enu default]\n\n// Please do not modify this file directly, it's specifically compiled and any changes may be lost.\n\n`;

    if (window.pdaglobals.hasOwnProperty('weapons')) {
        var weaponModEffects = ``;
        var weaponModMax = 0;
        var demonicWeapons = 0;
        var demonicArtifacts = ``;
        var weaponLanguage = ``;
        
        window.pdaglobals.weapons.forEach(weapon => {
            if (weapon.mods) {
                weaponModEffects = weaponModEffects.concat(`{ "RL${weapon.name}", "${weapon.mods.bulk}", "${weapon.mods.power}", "${weapon.mods.agility}", "${weapon.mods.technical}", "${weapon.mods.sniper}", "${weapon.mods.firestorm}", "${weapon.mods.nano}"},`);
                weaponModMax++;
            }
            if (weapon.corruptions) {
                demonicArtifacts = demonicArtifacts.concat(`{ "RL${weapon.name}", "${weapon.corruptions[0]}", "${weapon.corruptions[1]}", "${weapon.corruptions[2]}"},`)
                demonicWeapons++;
            }

            weaponLanguage = weaponLanguage.concat(LANGUAGE_WEAPONS(weapon));
        });

        /** PDA_MOD */
        weaponModList.push(new weaponModListing(weaponModMax, weaponModEffects, demonicWeapons, demonicArtifacts));
        generateDownload('PDA_MOD.ach', PDA_MOD(weaponModList[0]));

        /** LANGUAGE.WEAPONS */
        weaponLanguage = revertColors(weaponLanguage);
        /* if (window.pdaglobals.hasOwnProperty('colors')) {
            for(let [key, value] of Object.entries(window.pdaglobals.colors)) {
                weaponLanguage = weaponLanguage.replace(new RegExp('\\['+key+'\\]', 'g'), `\\c${value}`);
            }
        } */
        /** Strip readability for language */
        weaponLanguage = weaponLanguage.replace(/(\n)/g, '\\n').replace(/(;)\\n/gm, ';').replace(/( {3,})\\n/gm, '').replace(/^\\n( {1,})/gm, '');
        generateDownload('language.auto.weapons', weaponLanguage);

    }
    
    if (pdaglobals.hasOwnProperty('equipment')) {
        var headerArmorList = ``;
        var languageArmorList = language_warning;
        var equipmentMax = 0;

        window.pdaglobals.equipment.forEach(item => {
            headerArmorList = headerArmorList.concat(`{"RL${item.name}", "${item.name.toUpperCase()}"},`);
            equipmentMax++;

            /** Pipe into language */
            languageArmorList = languageArmorList.concat(LANGUAGE_EQUIPMENT(item));
        });
        
        /** Pipes into PDA_ARM */
        equipmentList.push(new equipmentListing(equipmentMax, headerArmorList));
        generateDownload('PDA_ARM.ach', PDA_ARM(equipmentList[0]));

        /** Replace all language pointers with their contents */
        if (window.pdaglobals.hasOwnProperty('attributes')) {
            for(let [key, value] of Object.entries(window.pdaglobals.attributes)) {
                languageArmorList = languageArmorList.replace(new RegExp(key, 'g'), value);
            }
        }

        /** LANGUAGE.WEAPONS */
        languageArmorList = languageArmorList.replace(/(\n)/g, '\\n').replace(/(;)\\n/gm, ';').replace(/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm, '');
        languageArmorList = revertColors(languageArmorList);
        generateDownload('language.auto.equipment', languageArmorList);
    }

    if (window.pdaglobals.hasOwnProperty('modeffect')) {
        var modEffectList = language_warning;

        window.pdaglobals.modeffect.forEach(modeffect => {
            modEffectList = modEffectList.concat(`${modeffect.name} = "${modeffect.effect}";`);
        });

        modEffectList = revertColors(languageAssemblyList);
        generateDownload('language.auto.mods', modEffectList);
    }

    if (window.pdaglobals.hasOwnProperty('assemblies')) {
        var headerAssemblyList = ``;
        var headerAssemblyMax = 0;
        var headerUniqueMax = 0;
        var headerSniperList = ``;
        var headerFirestormList = ``;
        var headerNanoList = ``;
        var languageAssemblyList = language_warning;

        window.pdaglobals.assemblies.forEach(assembly => {
            headerAssemblyList = headerAssemblyList.concat(`{"RL${assembly.name}AssemblyLearntToken", "PDA_ASSEMBLY_${assembly.tier.toUpperCase()}_${assembly.name.toUpperCase()}"},`);
            headerAssemblyMax++;

            /** LANGUAGE */
            languageAssemblyList = languageAssemblyList.concat(LANGUAGE_ASSEMBLIES(assembly));
        });

        languageAssemblyList = languageAssemblyList.replace(/(\n)/g, '\\n').replace(/(;)\\n/gm, ';').replace(/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm, '');
        languageAssemblyList = revertColors(languageAssemblyList);
        generateDownload('language.auto.assemblies', languageAssemblyList);

        /** PDA_ASM */
        if (window.pdaglobals.hasOwnProperty('weapons')) {
            window.pdaglobals.weapons.forEach(weapon => { 
                if (weapon.tier === 'Unique' || weapon.tier === 'Demonic' || weapon.tier === 'Legendary') {
                    if (weapon.unmoddable) {
                        headerSniperList = headerSniperList.concat(`{"RL${weapon.name}", "null"},`);
                        headerFirestormList = headerFirestormList.concat(`{"RL${weapon.name}", "null"},`);
                        headerNanoList = headerNanoList.concat(`{"RL${weapon.name}", "null"},`);
                    }
                    else {
                        headerSniperList = headerSniperList.concat(`{"RL${weapon.name}", "RL${weapon.name}SniperLearntToken"},`);
                        headerFirestormList = headerFirestormList.concat(`{"RL${weapon.name}", "RL${weapon.name}FirestormLearntToken"},`);
                        headerNanoList = headerNanoList.concat(`{"RL${weapon.name}", "RL${weapon.name}NanoLearntToken"},`);
                    }
                    headerUniqueMax++;
                }
            });
        }

        assemblyList.push(new assemblyListing(headerAssemblyMax, headerArmorList, headerUniqueMax, headerSniperList, headerFirestormList, headerNanoList));

        generateDownload('PDA_ASM.ach', PDA_ASM(assemblyList[0]))
    }
}

/** 
 * @name: Handle Colors
 * @param: var val The string to modify
 * @param: object searchreplace An object containing the key:value pairs of strings to search and replace with
 * @desc: Given a string, it replaces all instances of KEY with VALUE
 * @example: handleColors('test value with extra test', {"test": "sneaky"})
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

/** 
 * @name: Revert colors
 * @param: var str The string to modify
 * @desc: Given a string, it goes through and changes all known instances of a string from the left to the right one
 * @example: revertColors("\cdThis is a unique weapon\c-")
 */
function revertColors (str) {
    if (window.pdaglobals.hasOwnProperty('colors')) {
        for(let [key, value] of Object.entries(window.pdaglobals.colors)) {
            str = str.replace(new RegExp('\\['+key+'\\]', 'g'), `\\c${value}`);
        }
    }

    return str;
}

/** 
 * @name: Filter characters
 * @param: var str The string to modify
 * @desc: Given a string, it goes through and changes all known instances of a string from the left to the right one
 * @example: filterCharacters("\cdThis is a unique weapon\c-")
 */
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

/** No longer necessary */
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
    }
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
                    
                    if (an == n) {
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
    }
}