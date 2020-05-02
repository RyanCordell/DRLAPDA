/** Handle mod + artifact effects on all weapons */
var PDA_MOD = function (weapons) { return `
#library "PDA_MOD"

#define DRLA_WEAPONMAX ${weapons.max}
#define DRLA_DEMONWEAPONMAX ${weapons.dmax}
#define DRLA_WEAPONMODELEMENTS 8
#define DRLA_DEMONWEAPONELEMENTS 4

str DRLA_WeaponModIcons[PDA_MODMAX] = {
	"BMODICON","PMODICON","AMODICON","TMODICON","SMODICON","FMODICON","NMODICON"
};

str DRLA_AnimatedModIcons[PDA_MODMAX] = {
	"PDABMOD","PDAPMOD","PDAAMOD","PDATMOD","PDASMOD","PDAFMOD","PDANMOD"
};

str DRLA_WeaponModList[DRLA_WEAPONMAX][DRLA_WEAPONMODELEMENTS] = {
    ${weapons.list}
};

str DRLA_ArtifactEffectList[DRLA_DEMONWEAPONMAX][DRLA_DEMONWEAPONELEMENTS] = {
    ${weapons.dlist}
};
`; };

/** Handle armor-to-language link entries */
var PDA_ARM = function (equipment) { return `
#library "PDA_ARM"

#define DRLA_ARMORMAX ${equipment.max}
#define DRLA_ARMORELEMENTS 2
#define DRLA_ARMORSETMAX 18

str DRLA_WeaponModList[DRLA_ARMORMAX][DRLA_ARMORELEMENTS] = {
    ${equipment.list}
};

str DRLA_ArmorSetList[DRLA_ARMORSETMAX] = {
	"RLNuclearWeaponSetBonusActive",
	"RLCerberusSetBonusActive",
	"RLTacticalSetBonusActive",
	"RLLavaSetBonusActive",
	"RLGothicSetBonusActive",
	"RLPhaseshiftSetBonusActive",
	"RLInquisitorsSetBonusActive",
	"RLDeathFromAboveSetBonusActive",
	"RLDemonicSetBonusActive",
	"RLRoystenSetBonusActive",
	"RLArchitectSetBonusActive",
	"RLTorgueSetBonusActive",
	"RLSentrySentinelSetBonusActive",
	"RLSensibleStrategistSetBonusActive",
	"RLEnclaveSetBonusActive",
	"RLAngelicAttireSetBonusActive",
	"RLRainbowSetBonusActive",
	"RLTeslaboltSetBonusActive"
};
`; };

/** Handle assemblies-to-language link entries */
var PDA_ASM = function (assemblies) { return `
#library "PDA_ASM"

#define DRLA_ASSEMBLYMAX ${assemblies.max}
#define DRLA_ASSEMBLYELEMENTS 2
#define DRLA_EXOTICEFFECTS_MAX ${assemblies.uniquemax}

str DRLA_Assemblies[DRLA_ASSEMBLYMAX][DRLA_ASSEMBLYELEMENTS] = {
    ${assemblies.list}
};

str DRLA_UniqueSniperEffects[DRLA_EXOTICEFFECTS_MAX][DRLA_ASSEMBLYELEMENTS] = {
	${assemblies.sniper}
};

str DRLA_UniqueFirestormEFfects[DRLA_EXOTICEFFECTS_MAX][DRLA_ASSEMBLYELEMENTS] = {
	${assemblies.firestorm}
};

str DRLA_UniqueNanoEffects[DRLA_EXOTICEFFECTS_MAX][DRLA_ASSEMBLYELEMENTS] = {
	${assemblies.nano}
};
`; };

/** Handle armor language entries */
var LANGUAGE_EQUIPMENT = function (equipment) { 
    var bigname = equipment.name.toUpperCase();
    var coloredequipment = equipment.prettyname;

    var atts = ``;
    for (var i = 0; i < equipment.attributes.length; i++) {
        atts += `"${equipment.attributes[i]}\\n"`;
    }

    if (window.pdaglobals.hasOwnProperty('colors')) {
        for(let [key, value] of Object.entries(window.pdaglobals.colors)) {
            if (key.toUpperCase() === equipment.tier.toUpperCase()) {
                coloredequipment = `\\c${value}${equipment.prettyname}\\c-`;
            }
        }
    }

    var resPadder = function (str, len) {
        return str.padStart(len, ' ');
    };

    var res = equipment.resistances;
    var cybres = equipment.cyborgstats.resistances;

    return `
    PDA_ARMOR_${bigname}_ICON = "${equipment.icon}";
    PDA_ARMOR_${bigname}_NAME = "${coloredequipment}";
    PDA_ARMOR_${bigname}_DESC = "${equipment.description}";
    PDA_ARMOR_${bigname}_PROT = "${equipment.protection}% [GOLD]Protection[END]";
    PDA_ARMOR_${bigname}_RENPROT = "${equipment.renprotection}% [GOLD]Protection[END]";
    ${ equipment.resistances ? `PDA_ARMOR_${bigname}_RES = 
        "${res.melee}%${resPadder(' ', 4 - equipment.resistances.melee.length)}[DARKGRAY]Melee[END]${resPadder(' ', 4 - equipment.resistances.melee.length)}"
        "${res.bullet}%${resPadder(' ', 4 - equipment.resistances.bullet.length)}[GRAY]Bullet[END]\\n"
        "${res.fire}%${resPadder(' ', 4 - equipment.resistances.fire.length)}[RED]Fire[END]${resPadder(' ', 4 - equipment.resistances.melee.length)}"
        "${res.plasma}%${resPadder(' ', 4 - equipment.resistances.plasma.length)}[BLUE]Plasma[END]\\n"
        "${res.cryo}%${resPadder(' ', 4 - equipment.resistances.cryo.length)}[CYAN]Cryo[END]${resPadder(' ', 4 - equipment.resistances.melee.length)}"
        "${res.electric}%${resPadder(' ', 4 - equipment.resistances.electric.length)}[YELLOW]Electric[END]\\n"
        "${res.poison}%${resPadder(' ', 4 - equipment.resistances.poison.length)}[PURPLE]Poison[END]${resPadder(' ', 4 - equipment.resistances.melee.length)}"
        "${res.radiation}%${resPadder(' ', 4 - equipment.resistances.radiation.length)}[GREEN]Radiation[END]\\n";` : `` }
    ${ equipment.cyborgstats ? `PDA_ARMOR_${bigname}_CYBRES = 
        ${cybres.kinetic ? `"${cybres.kinetic}%${resPadder(' ', 4 - cybres.kinetic.length)}[WHITE]Kinetic Plating[END]\\n"` : ""}
        ${cybres.thermal ? `"${cybres.thermal}%${resPadder(' ', 4 - cybres.thermal.length)}[RED]Thermal Dampeners[END]\\n"` : ""}
        ${cybres.refractor ? `"${cybres.refractor}%${resPadder(' ', 4 - cybres.refractor.length)}[BLUE]Refractor Field[END]\\n"` : ""}
        ${cybres.organic ? `"${cybres.organic}%${resPadder(' ', 4 - cybres.organic.length)}[GREEN]Organic Recovery[END]\\n"` : ""}
        "${cybres.hazard}%${resPadder(' ', 4 - cybres.hazard.length)}[YELLOW]Hazard Shielding[END]\\n";` : `` }
    PDA_ARMOR_${bigname}_CYBAUG = "${equipment.cyborgstats.augment}";
    PDA_ARMOR_${bigname}_ATTR = ${atts};`;
};

/** Handle weapon language entries */
var LANGUAGE_WEAPONS = function (weapon) { 
    var bigname = weapon.name.toUpperCase();

    return `
    PDA_WEAPON_${bigname}_NAME = "${weapon.prettyname}";
    PDA_WEAPON_${bigname}_DESC = "${weapon.description}";
    ${weapon.specialpretty ? `PDA_WEAPON_${bigname}DEMONARTIFACTS_NAME = "${weapon.specialpretty}";` : `` }
    ${weapon.specialdesc ? `PDA_WEAPON_${bigname}DEMONARTIFACTS_DESC = "${weapon.specialdesc}";` : `` }`;
};

/** Handle assemblies language entries */
var LANGUAGE_ASSEMBLIES = function (assembly) { 
    var bigname = assembly.name.toUpperCase();
    var bigtier = assembly.tier.toUpperCase();
    var coloredname = ``;
    //var coloredvalid = assembly.valid.toString().;

    var mods = ``;
    for (var i = 0; i < assembly.mods.length; i++) {
        if (window.pdaglobals.hasOwnProperty('colors')) {
            for(let [key, value] of Object.entries(window.pdaglobals.colors)) {
                if (key === assembly.mods[i]) {
                    mods += `\\c${value}${assembly.mods[i].charAt(0)}\\c-`;
                }
            }
        }
    }
    if (window.pdaglobals.hasOwnProperty('colors')) {
        for(let [key, value] of Object.entries(window.pdaglobals.colors)) {
            if (key.toUpperCase() === assembly.tier.toUpperCase()) {
                coloredname = `\\c${value}${assembly.prettyname}\\c-`;
            }
        }
    }

    return `
    PDA_ASSEMBLY_${bigtier}_${bigname} = "${assembly.prettyname} [GRAY][[END]${mods}[GRAY]][END]";
    PDA_ASSEMBLY_${bigtier}_${bigname}_NAME = "${coloredname}";
    PDA_ASSEMBLY_${bigtier}_${bigname}_MODS = "[GRAY][[END]${mods}[GRAY]][END]";
    PDA_ASSEMBLY_${bigtier}_${bigname}_ICON = "${assembly.icon}";
    PDA_ASSEMBLY_${bigtier}_${bigname}_HEIGHT = "0";
    PDA_ASSEMBLY_${bigtier}_${bigname}_DESC = "${assembly.description}[GREEN]Valid Weapons:[END]\n${assembly.valid.toString().replace('->', '[YELLOW]->[END]')}";
    PDA_ASSEMBLY_${bigtier}_${bigname}_REQ = "${assembly.validlist}";
    `;
};
