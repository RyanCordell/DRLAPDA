/** Handle mod + artifact effects on all weapons */
/* eslint-disable */
export const PDA_MOD = (weapons) => { return `
#library "PDA_MOD"

#define DRLA_WEAPONMAX ${weapons.max}
#define DRLA_DEMONWEAPONMAX ${weapons.dmax}
#define DRLA_BASICMODMAX ${weapons.basicmax}
#define DRLA_ADVANCEDMODMAX ${weapons.advancedmax}
#define DRLA_MASTERMODMAX ${weapons.mastermax}
#define DRLA_WEAPONMODELEMENTS 8
#define DRLA_DEMONWEAPONELEMENTS 4

str DRLA_WeaponModList[DRLA_WEAPONMAX][DRLA_WEAPONMODELEMENTS] = {
    ${weapons.list}
};

str DRLA_ArtifactEffectList[DRLA_DEMONWEAPONMAX][DRLA_DEMONWEAPONELEMENTS] = {
    ${weapons.dlist}
};
`; };

/** Handle armor-to-language link entries */
export const PDA_ARM = (equipment) => { return `
#library "PDA_ARM"

#define DRLA_ARMORMAX ${equipment.max}
#define DRLA_ARMORELEMENTS 2
#define DRLA_ARMORSETMAX 18

str DRLA_ArmorList[DRLA_ARMORMAX][DRLA_ARMORELEMENTS] = {
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
export const PDA_ASM = (assemblies) => { return `
#library "PDA_ASM"

#define DRLA_ASSEMBLYMAX ${assemblies.max}
#define DRLA_ASSEMBLYELEMENTS 2
#define DRLA_EXOTICEFFECTS_MAX ${assemblies.uniquemax}
#define DRLA_EXOTICELEMENTS 4
#define DRLA_BASICMAX ${assemblies.basicmax}
#define DRLA_ADVANCEDMAX ${assemblies.advancedmax}
#define DRLA_MASTERMAX ${assemblies.mastermax}

/** 
 * Storage for .ini assembly writer
 */

int     DRLA_AssemblyState[MAX_PLAYERS][DRLA_ASSEMBLYMAX],
        DRLA_OldAssemblyState[MAX_PLAYERS][DRLA_ASSEMBLYMAX];

int     DRLA_KnownExoticState[MAX_PLAYERS][DRLA_EXOTICEFFECTS_MAX * 3],
        DRLA_OldExoticState[MAX_PLAYERS][DRLA_EXOTICEFFECTS_MAX * 3];

int     DRLA_KnownSniperState[MAX_PLAYERS][DRLA_EXOTICEFFECTS_MAX],
        DRLA_OldSniperState[MAX_PLAYERS][DRLA_EXOTICEFFECTS_MAX],

        DRLA_KnownFirestormState[MAX_PLAYERS][DRLA_EXOTICEFFECTS_MAX],
        DRLA_OldFirestormState[MAX_PLAYERS][DRLA_EXOTICEFFECTS_MAX],

        DRLA_KnownNanoState[MAX_PLAYERS][DRLA_EXOTICEFFECTS_MAX],
        DRLA_OldNanoState[MAX_PLAYERS][DRLA_EXOTICEFFECTS_MAX];

/** CVAR use */
str     DRLA_FetchStoredInfo[MAX_PLAYERS],
        DRLA_FetchExoticInfo[MAX_PLAYERS],
        DRLA_FetchSniperInfo[MAX_PLAYERS],
        DRLA_FetchFirestormInfo[MAX_PLAYERS],
        DRLA_FetchNanoInfo[MAX_PLAYERS];

/** Current state of weapon assembly knowledge */
str     DRLA_CurrentAssemblerState[MAX_PLAYERS] = {"","","","","","","",""};

str     DRLA_CurrentExoticModInfo[MAX_PLAYERS];

str     DRLA_CurrentSniperState[MAX_PLAYERS]    = {"","","","","","","",""},
        DRLA_CurrentFirestormState[MAX_PLAYERS] = {"","","","","","","",""},
        DRLA_CurrentNanoState[MAX_PLAYERS]      = {"","","","","","","",""};

str DRLA_Assemblies[DRLA_ASSEMBLYMAX][DRLA_ASSEMBLYELEMENTS] = {
    ${assemblies.list}
};

str DRLA_UniqueExoticModEffects[DRLA_EXOTICEFFECTS_MAX][DRLA_EXOTICELEMENTS] = {
    ${assemblies.exotics}
};
`; };

/** Handle armor language entries */

export const LANGUAGE_EQUIPMENT = (value, equipment) => { 
    const bigname = equipment.name.toUpperCase();
    let coloredequipment = equipment.prettyname;

    let atts = ``;
    for (var i = 0; i < equipment.attributes.length; i++) {
        atts += `" ${equipment.attributes[i]}\\n"`;
    }

    if (value.hasOwnProperty('colors')) {
        for(let [key, value] of Object.entries(value.colors)) {
            if (key.toUpperCase() === equipment.tier.toUpperCase()) {
                coloredequipment = `\\c${value}${equipment.prettyname}\\c-`;
            }
        }
    }

    const resPadder = (str, len) => {
        return str.padStart(len, ' ');
    };

    const res = equipment.resistances;
    const cybres = equipment.cyborgstats.resistances;

    return `
    PDA_ARMOR_${bigname}_ICON = "${equipment.icon}";
    PDA_ARMOR_${bigname}_NAME = "${coloredequipment}";
    PDA_ARMOR_${bigname}_DESC = "${equipment.description}";
    PDA_ARMOR_${bigname}_PROT = "${resPadder(' ', 4 - equipment.protection)}${equipment.protection}% [GOLD]Protection[END]";
    PDA_ARMOR_${bigname}_RENPROT = "${resPadder(' ', 4 - equipment.renprotection)}${equipment.renprotection}% [GOLD]Protection[END]";
    ${ equipment.resistances ? `PDA_ARMOR_${bigname}_RES = 
        "${resPadder(' ', 4 - equipment.resistances.melee.length)}${res.melee}% [DARKGRAY]Melee[END]  "
        "${resPadder(' ', 4 - equipment.resistances.bullet.length)}${res.bullet}% [GRAY]Bullet[END] \\n"
        "${resPadder(' ', 4 - equipment.resistances.fire.length)}${res.fire}% [RED]Fire[END]   "
        "${resPadder(' ', 4 - equipment.resistances.cryo.length)}${res.cryo}% [CYAN]Cryo[END]   \\n"
        "${resPadder(' ', 4 - equipment.resistances.plasma.length)}${res.plasma}% [BLUE]Plasma[END] "
        "${resPadder(' ', 4 - equipment.resistances.electric.length)}${res.electric}% [YELLOW]Electric[END]\\n"
        "${resPadder(' ', 4 - equipment.resistances.poison.length)}${res.poison}% [PURPLE]Poison[END] "
        "${resPadder(' ', 4 - equipment.resistances.radiation.length)}${res.radiation}% [GREEN]Radiation[END]\\n";` : `` }
    ${ equipment.cyborgstats ? `PDA_ARMOR_${bigname}_CYBRES = 
        ${cybres.kinetic ? `"${resPadder(' ', 4 - cybres.kinetic.length)}${cybres.kinetic}% [WHITE]Kinetic Plating[END]\\n"` : ""}
        ${cybres.thermal ? `"${resPadder(' ', 4 - cybres.thermal.length)}${cybres.thermal}% [RED]Thermal Dampeners[END]\\n"` : ""}
        ${cybres.refractor ? `"${resPadder(' ', 4 - cybres.refractor.length)}${cybres.refractor}% [BLUE]Refractor Field[END]\\n"` : ""}
        ${cybres.organic ? `"${resPadder(' ', 4 - cybres.organic.length)}${cybres.organic}% [GREEN]Organic Recovery[END]\\n"` : ""}
        "${resPadder(' ', 4 - cybres.hazard.length)}${cybres.hazard}% [YELLOW]Hazard Shielding[END]\\n";` : `` }
    PDA_ARMOR_${bigname}_CYBAUG = "${equipment.cyborgstats.augment}";
    PDA_ARMOR_${bigname}_ATTR = ${atts};`;
};

/** Handle weapon language entries */
export const LANGUAGE_WEAPONS = (weapon) => { 
    const bigname = weapon.name.toUpperCase();

    return `
    PDA_WEAPON_${bigname}_NAME = "${weapon.prettyname}";
    PDA_WEAPON_${bigname}_DESC = "${weapon.actualDescription}";
    ${weapon.specialpretty ? `PDA_WEAPON_${bigname}DEMONARTIFACTS_NAME = "${weapon.specialpretty}";` : `` }
    ${weapon.specialdesc ? `PDA_WEAPON_${bigname}DEMONARTIFACTS_DESC = "${weapon.specialdesc}";` : `` }`;
};

/** Handle assemblies language entries */
export const LANGUAGE_ASSEMBLIES = (value, assembly) => { 
    const bigname = assembly.name.toUpperCase();
    const bigtier = assembly.tier.toUpperCase();
    let coloredname = ``;
    //var coloredvalid = assembly.valid.toString().;

    let mods = ``;
    for (let i = 0; i < assembly.mods.length; i++) {
        if (value.hasOwnProperty('colors')) {
            for(let [key, value] of Object.entries(value.colors)) {
                if (key === assembly.mods[i]) {
                    mods += `\\c${value}${assembly.mods[i].charAt(0)}\\c-`;
                }
            }
        }
    }
    if (value.hasOwnProperty('colors')) {
        for(let [key, value] of Object.entries(value.colors)) {
            if (key.toUpperCase() === assembly.tier.toUpperCase()) {
                coloredname = `\\c${value}${assembly.prettyname}\\c-`;
            }
        }
    }

    let valid = ``;
    for (let i = 0; i < assembly.valid.length; i++) {
        valid += `${assembly.valid[i]}`;
    }

    let validlist = ``;
    for (let i = 0; i < assembly.validlist.length; i++) {
        validlist += `${assembly.validlist[i]}`;
    }

    return `
    PDA_ASSEMBLY_${bigtier}_${bigname} = "${assembly.prettyname} [GRAY][[END]${mods}[GRAY]][END]";
    PDA_ASSEMBLY_${bigtier}_${bigname}_NAME = "${coloredname}";
    PDA_ASSEMBLY_${bigtier}_${bigname}_MODS = "[GRAY][[END]${mods}[GRAY]][END]";
    PDA_ASSEMBLY_${bigtier}_${bigname}_ICON = "${assembly.icon}";
    PDA_ASSEMBLY_${bigtier}_${bigname}_HEIGHT = "0";
    PDA_ASSEMBLY_${bigtier}_${bigname}_DESC = "${assembly.description}[GREEN]Valid Weapons:[END]\n${valid.toString().replace(/->/gm, '[YELLOW]->[END]')}";
    PDA_ASSEMBLY_${bigtier}_${bigname}_REQ = "${validlist}";
    `;
};
