/** Handle mod + artifact effects on all weapons */
var PDA_MOD = function (weapons) { return `
#library "PDA_MOD"

#define DRLA_WEAPONMAX ${weapons.max}
#define DRLA_DEMONWEAPONMAX ${weapons.dmax}
#define DRLA_WEAPONMODELEMENTS 8
#define DRLA_DEMONWEAPONELEMENTS 4

str DRLA_WeaponModList[DRLA_WEAPONMAX][DRLA_WEAPONMODELEMENTS] = {
    ${weapons.list}
}

str DRLA_ArtifactEffectList[DRLA_DEMONWEAPONMAX][DRLA_DEMONWEAPONELEMENTS] = {
    ${weapons.dlist}
}
`; };

/** Handle armor-to-language link entries */
var PDA_ARM = function (equipment) { return `
#library "PDA_ARM"

#define DRLA_ARMORMAX ${equipment.max}
#define DRLA_ARMORELEMENTS 2
#define DRLA_ARMORSETMAX 18

str DRLA_WeaponModList[DRLA_ARMORMAX][DRLA_ARMORELEMENTS] = {
    ${equipment.list}
}

str DRLA_ArmorSetList[DRLA_ARMORSETMAX] =
{
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

/** Handle armor language entries */
var LANGUAGE_EQUIPMENT = function (equipment) { 
    var bigname = equipment.name.toUpperCase();

    var atts = ``;
    for (var i = 0; i < equipment.attributes.length; i++) {
        atts += `"${equipment.attributes[i]}\\n"`;
    }

    var biggestring = `
    PDA_ARMOR_${bigname}_ICON = "${equipment.icon}";
    PDA_ARMOR_${bigname}_NAME = "${equipment.prettyname}";
    PDA_ARMOR_${bigname}_DESC = "${equipment.description}";
    PDA_ARMOR_${bigname}_PROT = "${equipment.protection}";
    PDA_ARMOR_${bigname}_RENPROT = "${equipment.renprotection}";
    ${ equipment.resistances ? `PDA_ARMOR_${bigname}_RES = 
        "${equipment.resistances.melee} [DARKGRAY]Melee[END]"
        "${equipment.resistances.bullet} [GRAY]Bullet[END]\\n"
        "${equipment.resistances.fire} [RED]Fire[END]"
        "${equipment.resistances.plasma} [BLUE]Plasma[END]\\n"
        "${equipment.resistances.cryo} [CYAN]Cryo[END]"
        "${equipment.resistances.electric} [YELLOW]Electric[END]\\n"
        "${equipment.resistances.poison} [PURPLE]Poison[END]"
        "${equipment.resistances.radiation} [GREEN]Radiation[END]\\n";` : `` }
    PDA_ARMOR_${bigname}_ATTR = ${atts};`;

    return biggestring;
};