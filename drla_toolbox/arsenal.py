import sys
import os.path

import json
import re

from typing import Any

from utils import current_time

INPUT_FOLDER_ARG: int = 1
OUTPUT_FOLDER_ARG: int = 2
SEPARATOR_ARG: int = 3

FIRST_ARTIFACT: int = 0
SECOND_ARTIFACT: int = 1
THIRD_ARTIFACT: int = 2

class Arsenal:
    def __init__(self, on_log=print, on_clear=None, pick_input_dir=None, pick_output_file=None):
        self.language_warning: str = f'''
[enu default]\n\n/*
Please do not modify this file directly,
it\'s specifically compiled and any changes may be lost.
*/\n'''
        self.separator_token: str = ":"
        self.output_file: str = ""
        self.colors: dict[str, Any] = {}
        self.input_files: list[str] = []
        self.loaded_json: dict[str, Any] = {}
        self.filler: dict[str, Any] = {}
        self.attributes: dict[str, Any] = {}
        self.on_log = on_log
        self.on_clear = on_clear
        self.pick_input_dir = pick_input_dir
        self.pick_output_file = pick_output_file
  
    def res_padder(self, str_to_pad: str, padding_length: int) -> str:
        return str_to_pad.rjust(padding_length, " ")

    def language_padding(self, value: str) -> str:
        return self.res_padder(" ", 4 - len(value))

    def main(self) -> None:
        self.do_input()

        if len(sys.argv) > 3:
            if sys.argv[SEPARATOR_ARG]:
                self.separator_token = sys.argv[SEPARATOR_ARG]

        if sys.argv[OUTPUT_FOLDER_ARG]:
            self.output_file = sys.argv[OUTPUT_FOLDER_ARG]

        self.do_compile(do_output=True)

    def clear_results(self) -> None:
        if self.on_clear:
            self.on_clear()

    def do_input(self) -> None:
        if self.pick_input_dir:
            select_directory = self.pick_input_dir()
        else:
            if not os.path.isdir(sys.argv[INPUT_FOLDER_ARG]):
                return

            select_directory = sys.argv[INPUT_FOLDER_ARG]

        if select_directory:
            self.input_files = [
                os.path.join(select_directory, f)
                for f in os.listdir(select_directory)
                if f.endswith(".json")
            ]

        self.clear_results()

        if self.input_files:
            self.on_log(f"{current_time()} Files selected: {self.input_files}")
            self.filler = {}

            for file in self.input_files:
                self.on_log(f"{current_time()} Loaded JSON into filler memory: {file}\n")

                if "data.json" in file:
                    with open(os.path.normpath(file), mode="r", encoding="utf-8") as freshdata:
                        self.filler = json.load(freshdata)

                # Preventative guard if there is ever an empty string or somesuch
                if file:
                    with open(os.path.normpath(file), mode="r", encoding="utf-8") as json_buffer:
                        self.loaded_json.update(json.load(json_buffer))

            for f in self.filler:
                if "colors" in f:
                    self.colors = self.filler[f]
                if "attributes" in f:
                    self.attributes = self.filler[f]
        else:
            self.on_log(f"{current_time()} No JSON files selected\n")

    def do_compile(self, do_output: bool = True) -> None:
        if "weapons" in self.loaded_json:
            self.process_weapons(self.loaded_json["weapons"], do_output)
        if "equipment" in self.loaded_json:
            self.process_equipment(self.loaded_json["equipment"], do_output)
        if "modeffect" in self.loaded_json:
            self.process_mod_effect(self.loaded_json["modeffect"], do_output)
        if "assemblies" in self.loaded_json:
            self.process_assemblies(self.loaded_json, do_output)

    def do_output(self, name: str) -> str:
        if self.pick_output_file:
            file = self.pick_output_file(name)
            return file.name if file else ""
        else:
            if not os.path.isdir(sys.argv[OUTPUT_FOLDER_ARG]):
                os.mkdir(sys.argv[OUTPUT_FOLDER_ARG])

            return os.path.join(sys.argv[OUTPUT_FOLDER_ARG], name)

    def handle_colors(self, str_to_color: str, method: str) -> str:
        if not str_to_color or len(self.colors) < 1:
            self.on_log(f"{current_time()} No data found to process\n")
            return ""

        for color_key, color_value in self.colors.items():
            str_to_color = str_to_color.replace(
                "[" + color_key + "]", "\\c" + color_value if method == "revert" else ""
            )

        return str_to_color

    # -----
    def process_weapons(self, weapons: dict[str, Any], do_output: bool) -> None:
        self.on_log(f"{current_time()} Parsing WEAPONS database\n")

        weapon_mod_max: int = 0
        demonic_weapons: int = 0
        basic_mod_max: int = 0
        advanced_mod_max: int = 0
        master_mod_max: int = 0
        weapon_language: list[str] = []
        weapon_description: list[str] = []
        weapon_s_description: list[str] = []
        demonic_artifacts: list[str] = []
        weapon_mods: list[str] = []
        weapon_mod_effects: list[str] = []
        weapon_mod_list: dict[str, Any] = {}

        for weapon in weapons:
            weapon: dict[str, Any]
            weapon_description = []
            weapon_stats: list[str] = []
            weapon_s_description = []
            weapon_mods = []

            if "mods" in weapon:
                weapon_mod_effects.append("{")
                weapon_mod_effects.append(
f'''"RL{weapon["name"]}",
"{weapon["mods"]["bulk"]}",
"{weapon["mods"]["power"]}",
"{weapon["mods"]["agility"]}",
"{weapon["mods"]["technical"]}",
"{weapon["mods"]["sniper"]}",
"{weapon["mods"]["firestorm"]}",
"{weapon["mods"]["nano"]}"
''')
                weapon_mod_effects.append("},")
                weapon_mod_max += 1

                mods_len = len(weapon["mods"])
                for i, mods_fragment in enumerate(weapon["mods"]):
                    mods_fragment: str = mods_fragment.replace("\n", "/n")
                    weapon_mods.append(
                        f'''"{weapon['mods'][mods_fragment]}{self.separator_token}"'''
                    )

                    if i < mods_len - 1:
                        weapon_mods.append("\n")

                weapon["actualMods"] = "".join(weapon_mods)

            if "corruptions" in weapon:
                demonic_artifacts.append("{")
                demonic_artifacts.append(
f'''"RL{weapon["name"]}",
"{weapon["corruptions"][FIRST_ARTIFACT]}",
"{weapon["corruptions"][SECOND_ARTIFACT]}",
"{weapon["corruptions"][THIRD_ARTIFACT]}"
''')
                demonic_artifacts.append("},")
                demonic_weapons += 1

            if "tier" in weapon:
                match weapon["tier"]:
                    case "Basic":
                        basic_mod_max += 1
                    case "Advanced":
                        advanced_mod_max += 1
                    case "Master":
                        master_mod_max += 1
                    case _:
                        pass

            if "stats" in weapon:
                stats_len = len(weapon["stats"])
                if stats_len > 0:
                    for i, stats_fragment in enumerate(weapon["stats"]):
                        stats_fragment: str = stats_fragment.replace("\n", "/n")
                        weapon_stats.append(f'"{stats_fragment}"')

                        if i < stats_len - 1:
                            weapon_stats.append("\n")

                    weapon["actualStats"] = "".join(weapon_stats)

            if "description" in weapon:
                desc_len = len(weapon["description"])
                for i, desc_fragment in enumerate(weapon["description"]):
                    desc_fragment: str = desc_fragment.replace("\n", "/n")
                    weapon_description.append(f'"{desc_fragment}"')

                    if i < desc_len - 1:
                        weapon_description.append("\n")

                weapon["actualDescription"] = "".join(weapon_description)

            if "specialdesc" in weapon:
                desc_len = len(weapon["specialdesc"])

                for i, desc_fragment in enumerate(weapon["specialdesc"]):
                    desc_fragment: str = desc_fragment.replace("\n", "/n")
                    weapon_s_description.append(f'"{desc_fragment}"')

                    if i < desc_len - 1:
                        weapon_s_description.append("\n")

                weapon["actualSpecialDesc"] = "".join(weapon_s_description)

            weapon["flatname"] = self.handle_colors(weapon["prettyname"], "strip")
            weapon_language.append(self.create_weapons_language(weapon))
            weapon_language.append("\n\n")

        # TODO (us): Used to be part of modeffects.idb, will need to re-examine
        # weapon_mod_list["max"] = weapon_mod_max
        # weapon_mod_list["dmax"] = demonic_weapons
        # weapon_mod_list["basicmax"] = basic_mod_max
        # weapon_mod_list["advancedmax"] = advanced_mod_max
        # weapon_mod_list["mastermax"] = master_mod_max
        # weapon_mod_list["list"] = "".join(weapon_mod_effects)
        # weapon_mod_list["dlist"] = "".join(demonic_artifacts)

        temp_string: str = "".join(weapon_language).strip()
        temp_string = self.handle_colors(temp_string, "revert")

        temp_string = temp_string.replace("[INNERQUOTE]", '\\"')
        temp_string = temp_string.replace("\n", "\\n")
        temp_string = re.sub(r";\n", ";", temp_string)
        temp_string = re.sub(r'\n(?=(?:[^"]*"[^"]*")*[^"]*$)', "", temp_string, flags=re.MULTILINE)
        temp_string = re.sub(r" {3,}\n", "", temp_string)
        temp_string = re.sub(r"^\n +", "", temp_string, flags=re.MULTILINE)
        temp_string = temp_string.replace("/n", "\\n")

        language_weapon_output: str = self.language_warning + temp_string
        self.output_construct(do_output, language_weapon_output, "language.auto.weapons")

    def process_equipment(self, equipment: dict[str, Any], do_output: bool) -> None:
        self.on_log(f"{current_time()} Reading EQUIPMENT...\n")

        equipment_max: int = 0
        language_armor_list: list[str] = []
        header_armor_list: list[str] = []
        equip_description: list[str] = []

        for equip in equipment:
            equip: dict[str, Any]
            equip_description = []
            header_armor_list.append("{")
            header_armor_list.append(f'"RL{equip["name"]}", "{equip["name"].upper()}"')
            header_armor_list.append("},")
            equipment_max += 1

            if "description" in equip:
                for desc_fragment in equip["description"]:
                    desc_fragment: str = desc_fragment.replace("\n", "/n")
                    equip_description.append(f'"{desc_fragment}"\n')

                equip["actualDescription"] = "".join(equip_description)

            language_armor_list.append(self.create_equipment_language(equip))
            language_armor_list.append("\n")

        equipment_list: dict[str, Any] = {}
        equipment_list["max"] = equipment_max
        equipment_list["list"] = "".join(header_armor_list)

        arsenal_db = self.create_armor_acs_array(equipment_list)
        arsenal_db = arsenal_db.replace("'", '"')

        temp_string: str = "".join(language_armor_list)

        self.output_construct(do_output, arsenal_db, "equipment.idb")

        for attribute_key, attribute_value in self.attributes.items():
            temp_string = temp_string.replace(attribute_key, attribute_value)

        self.on_log(f"{current_time()} Keywords translated into attributes\n")

        temp_string = temp_string.replace("\n", "\\n")
        temp_string = re.sub(r";\n", ";", temp_string)
        temp_string = re.sub(r'\n(?=(?:[^"]*"[^"]*")*[^"]*$)', "", temp_string, flags=re.MULTILINE)

        temp_string = temp_string.replace("/n", "\\n")

        temp_string = self.handle_colors(temp_string, "revert")

        language_armor_output = self.language_warning + temp_string

        self.output_construct(do_output, language_armor_output, "language.auto.equipment")

    def process_mod_effect(self, mods: dict[str, Any], do_output: bool) -> None:
        mod_effect_list: list[str] = []

        for mod in mods:
            mod: dict[str, Any]
            mod_effect_list_len: int = len(mod["effect"])

            if isinstance(mod["effect"], str):
                mod_effect_list.append(f'''{mod['name']} = "{mod['effect']}";''')

            if isinstance(mod["effect"], (list, dict)):
                mod_effect_list.append(f'''{mod['name']} = ''')

                for i, mod_effect_fragment in enumerate(mod["effect"]):
                    mod_effect_fragment: str = mod_effect_fragment.replace("\n", "/n")
                    mod_effect_list.append(f'"{mod_effect_fragment}"')

                    if i < mod_effect_list_len - 1:
                        mod_effect_list.append("\n")

                mod_effect_list.append(";")

            mod_effect_list.append("\n")

        temp_string: str = "".join(mod_effect_list)
        temp_string = self.handle_colors(temp_string, "revert")

        language_mod_output: str = self.language_warning + temp_string

        self.on_log(f"{current_time()} Done parsing mod effects DB.\n")

        self.output_construct(do_output, language_mod_output, "language.auto.mods")

    def process_assemblies(self, data: dict[str, Any], do_output: bool) -> None:
        header_assembly_max: int = 0
        header_unique_max: int = 0
        basic_max: int = 0
        advanced_max: int = 0
        master_max: int = 0
        assembly_description: list[str] = []
        header_assembly_list: list[str] = []
        language_assembly_list: list[str] = []
        header_exotic_list: list[str] = []

        language_assembly_list.append(
            'PDA_ASSEMBLY_REQUIREMENTS = "\\cdRequirements:\\c-\\n";\n'
        )
        language_assembly_list.append('PDA_ASSEMBLIES="')
        for i, assembly in enumerate(data["assemblies"]):
            language_assembly_list.append(f'''RL{assembly['name']}AssemblyLearntToken{self.separator_token}PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}{self.separator_token}''')
            language_assembly_list.append('"')

            if i < len(data["assemblies"]) - 1:
                language_assembly_list.append("\n")
                language_assembly_list.append('"')

        language_assembly_list.append(";")
        language_assembly_list.append("\n")
        language_assembly_list.append("\n")
        language_assembly_list.append(f'''PDA_SEPARATOR_CHARACTER="{self.separator_token}";''')
        language_assembly_list.append("\n")
        language_assembly_list.append("\n")

        for assembly in data["assemblies"]:
            assembly_description = []

            header_assembly_list.append("{")
            header_assembly_list.append(f'''
                "RL{assembly['name']}AssemblyLearntToken",
                "PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}"
            ''')
            header_assembly_list.append("},")
            header_assembly_max += 1

            match assembly["tier"]:
                case "Basic":
                    basic_max += 1
                case "Advanced":
                    advanced_max += 1
                case "Master":
                    master_max += 1
                case _:
                    pass

            if "description" in assembly:
                desc_len = len(assembly["description"])

                for i, desc_fragment in enumerate(assembly["description"]):
                    desc_fragment: str = desc_fragment.replace("\n", "/n")

                    if i < desc_len - 1:
                        assembly_description.append(f'"{desc_fragment}"\n')
                    else:
                        assembly_description.append(f'"{desc_fragment}"')

                assembly["actualDescription"] = "".join(assembly_description)

            language_assembly_list.append(self.create_assemblies_language(assembly))
            language_assembly_list.append("\n")

        temp_string: str = "".join(language_assembly_list)

        temp_string = temp_string.replace("\n", "\\n")
        temp_string = re.sub(r";\n", ";", temp_string)
        temp_string = re.sub(r'\n(?=(?:[^"]*"[^"]*")*[^"]*$)', "", temp_string, flags=re.MULTILINE)

        temp_string = temp_string.replace("/n", "\\n")

        temp_string = self.handle_colors(temp_string, "revert")

        for weapon in data["weapons"]:
            weapon: dict[str, Any]
            if (
                weapon["tier"] == "Unique"
                or weapon["tier"] == "Demonic"
                or weapon["tier"] == "Legendary"
            ):
                if "unmoddable" in weapon:
                    header_exotic_list.append("{")
                    header_exotic_list.append(f'''"RL{weapon['name']}", "null", "null", "null"''')
                    header_exotic_list.append("},")
                else:
                    header_exotic_list.append("{")
                    header_exotic_list.append(f'''
"RL{weapon['name']}",
"RL{weapon['name']}SniperLearntToken",
"RL{weapon['name']}FirestormLearntToken",
"RL{weapon['name']}NanoLearntToken"
''')
                    header_exotic_list.append("},")

                header_unique_max += 1

        language_assembly_list.append(f'''
DRLA_ASSEMBLYMAX="{header_assembly_max}";
DRLA_ASSEMBLYELEMENTS="2";
DRLA_EXOTICEFFECTS_MAX="{header_unique_max}";
DRLA_EXOTICELEMENTS="4";
DRLA_BASICMAX="{basic_max}";
DRLA_ADVANCEDMAX="{advanced_max}";
DRLA_MASTERMAX="{master_max}";
''')

        language_assembly_output: str = self.language_warning + temp_string

        self.output_construct(do_output, language_assembly_output, "language.auto.assemblies")

        # TODO (us): Used to be part of modeffects.idb, will need to re-examine
        # assembly_list: dict[str, Any] = {}
        # assembly_list["list"] = "".join(header_assembly_list)
        # assembly_list["exotics"] = "".join(header_exotic_list)
        # assembly_list["max"] = header_assembly_max
        # assembly_list["uniquemax"] = header_unique_max
        # assembly_list["basicmax"] = basic_max
        # assembly_list["advancedmax"] = advanced_max
        # assembly_list["mastermax"] = master_max

        self.on_log(f"{current_time()} Finished compilation\n")

    # -----

    def output_construct(self, do_output: bool, input: str, output: str) -> None:
        if do_output:
            file_path: str = self.do_output(output)

            if file_path:
                with open(file_path, mode="w", encoding="utf-8") as file:
                    file.write(input)
                self.on_log(f"{current_time()} Created {output}\n")
        else:
            self.on_log(f"{current_time()} Created nothing\n")

    def create_armor_acs_array(self, equipment: dict[str, Any]) -> str:
        # TODO: Export the active set bonuses into a separate JSON, or rely on Equipment instead?
        construct: str = f'''
#library "PDA_ARM"

#define DRLA_ARMORMAX {equipment['max']}
#define DRLA_ARMORELEMENTS 2
#define DRLA_ARMORSETMAX 18

// I am currently unable to be rid of this, so this will stay for now
str DRLA_ArmorList[DRLA_ARMORMAX][DRLA_ARMORELEMENTS] = {{{equipment['list']}}};

str DRLA_ArmorSetList[DRLA_ARMORSETMAX] = {{
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
}};'''

        return construct

    # -----

    def create_weapons_language(self, weapon: dict[str, Any]) -> str:
        if "name" not in weapon:
            return ""

        bigname: str = weapon["name"].upper()

        fragment: list[str] = list(f'''PDA_WEAPON_{bigname}_ACTOR = "RL{bigname}";\n''')

        if "icon" in weapon:
            fragment.append(f'''PDA_WEAPON_{bigname}_ICON = "{weapon['icon']}";\n''')
        if "prettyname" in weapon:
            fragment.append(f'''PDA_WEAPON_{bigname}_NAME = "{weapon['prettyname']}";\n''')
            fragment.append(f'''PDA_WEAPON_{bigname}_FLATNAME = "{weapon['flatname']}";\n''')
        if "actualDescription" in weapon:
            # Note to future self: Don't try to add quote marks here, they're already handled elsewhere.
            if "actualStats" in weapon:
                fragment.append(f'''PDA_WEAPON_{bigname}_DESC = {weapon['actualStats']}\n''')
                fragment.append(f'''"/n/n"\n''')
                fragment.append(f'''{weapon['actualDescription']};\n''')
            else:
                fragment.append(f'''PDA_WEAPON_{bigname}_DESC = {weapon['actualDescription']};\n''')
        if "specialpretty" in weapon:
            fragment.append(f'''PDA_WEAPON_{bigname}DEMONARTIFACTS_NAME = "{weapon['specialpretty']}";\n''')
        if "specialdesc" in weapon:
            fragment.append(f'''PDA_WEAPON_{bigname}DEMONARTIFACTS_DESC = {weapon['actualSpecialDesc']};\n''')
        if "mods" in weapon:
            fragment.append(f'''PDA_WEAPON_{bigname}_MODS = {weapon['actualMods']};\n''')

        return "".join(fragment).strip()

    def create_equipment_language(self, equipment: dict[str, Any]) -> str:
        if not self.filler:
            raise ValueError("self.filler is empty")
        if "name" not in equipment:
            raise ValueError(f"{equipment} not found in equipment list")

        bigname: str = equipment["name"].upper()
        coloredequipment: str = equipment["prettyname"]
        flatequipment: str = self.handle_colors(equipment["prettyname"], "strip")

        atts: list[str] = []
        for attr in equipment["attributes"]:
            atts.append(f'''" {attr}\\n"''')

        for color_key, color_value in self.colors.items():
            if color_key.upper() == equipment["tier"].upper():
                coloredequipment = f'''\\c{color_value}{equipment['prettyname']}\\c-'''

        construct: list[str] = list(
f'''
PDA_ARMOR_{bigname}_ICON = "{equipment['icon']}";
PDA_ARMOR_{bigname}_NAME = "{coloredequipment}";
PDA_ARMOR_{bigname}_FLATNAME = "{flatequipment}";
PDA_ARMOR_{bigname}_DESC = {equipment['actualDescription']};
PDA_ARMOR_{bigname}_PROT = "{self.language_padding(equipment['protection'])}{equipment['protection']}% [GOLD]Protection[END]";
PDA_ARMOR_{bigname}_RENPROT = "{self.language_padding(equipment['renprotection'])}{equipment['renprotection']}% [GOLD]Protection[END]";
'''
        )

        if "resistances" in equipment:
            res: dict[str, Any] = equipment["resistances"]
            construct.append(
f'''
PDA_ARMOR_{bigname}_RES =
  "{self.language_padding(res['melee'])}{res['melee']}% [DARKGRAY]Melee[END]  "
  "{self.language_padding(res['bullet'])}{res['bullet']}% [GRAY]Bullet[END] \\n"
  "{self.language_padding(res['fire'])}{res['fire']}% [RED]Fire[END]   "
  "{self.language_padding(res['cryo'])}{res['cryo']}% [CYAN]Cryo[END]   \\n"
  "{self.language_padding(res['plasma'])}{res['plasma']}% [BLUE]Plasma[END] "
  "{self.language_padding(res['electric'])}{res['electric']}% [YELLOW]Electric[END]\\n"
  "{self.language_padding(res['poison'])}{res['poison']}% [PURPLE]Poison[END] "
  "{self.language_padding(res['radiation'])}{res['radiation']}% [GREEN]Radiation[END]\\n";
'''
            )
            construct.append("\n")

        if "cyborgstats" in equipment:
            cybres: dict[str, Any] = equipment["cyborgstats"]["resistances"]
            construct.append(f'''PDA_ARMOR_{bigname}_CYBRES =''')

            if "kinetic" in cybres:
                construct.append(
                    f'''"{self.language_padding(cybres['kinetic'])}{cybres['kinetic']}% [WHITE]Kinetic Plating[END]\\n"'''
                )
            if "thermal" in cybres:
                construct.append(
                    f'''"{self.language_padding(cybres['thermal'])}{cybres['thermal']}% [RED]Thermal Dampeners[END]\\n"'''
                )
            if "refractor" in cybres:
                construct.append(
                    f'''"{self.language_padding(cybres['refractor'])}{cybres['refractor']}% [BLUE]Refractor Field[END]\\n"'''
                )
            if "organic" in cybres:
                construct.append(
                    f'''"{self.language_padding(cybres['organic'])}{cybres['organic']}% [GREEN]Organic Recovery[END]\\n"'''
                )

            construct.append(
                f'''"{self.language_padding(cybres['hazard'])}{cybres['hazard']}% [YELLOW]Hazard Shielding[END]\\n";'''
            )

        temp_atts_string: str = ''.join(atts)
        construct.append(
f'''
PDA_ARMOR_{bigname}_CYBAUG = "{equipment['cyborgstats']['augment']}";
PDA_ARMOR_{bigname}_ATTR = {temp_atts_string};
''')

        return "".join(construct)

    def create_assemblies_language(self, assembly: dict[str, Any]) -> str:
        if not self.filler:
            raise ValueError("Arsenal filler is empty")
        if "name" not in assembly:
            raise ValueError(f"Name not found in assembly data: {assembly}")

        bigname: str = assembly["name"].upper()
        bigtier: str = assembly["tier"].upper()
        coloredname: str = ""

        mods: list[str] = []
        valid: list[str] = []
        validlist: list[str] = []

        desc_len: int = 0

        for mod in assembly["mods"]:
            for color_key, color_value in self.colors.items():
                if color_key.upper() == mod:
                    mods.append(f'\\c{color_value}{mod[0]}\\c-')

        for color_key, color_value in self.colors.items():
            if color_key.upper() == assembly["tier"].upper():
                coloredname = f'''\\c{color_value}{assembly['prettyname']}\\c-'''

        desc_len = len(assembly["valid"])

        for i, validassemblies in enumerate(assembly["valid"]):
            validassemblies: str = validassemblies.replace("\n", "/n")

            if i < desc_len - 1:
                valid.append(f'''"{validassemblies}"\n''')
            else:
                valid.append(f'''"{validassemblies}"''')

        desc_len = len(assembly["validlist"])
        for i, validweapon in enumerate(assembly["validlist"]):
            validweapon: str = validweapon.replace("\n", "/n")

            validlist.append(f'''"{validweapon}"''')
            if i < desc_len - 1:
                validlist.append("\n")

        temp_string: str = "".join(valid)
        temp_string = temp_string.replace("->", "[YELLOW]->[END]")

        temp_mods_string: str = "".join(mods)
        temp_list_string: str = ''.join(validlist)

        return f'''
PDA_ASSEMBLY_{bigtier}_{bigname} = "{assembly['prettyname']} [GRAY][[END]{temp_mods_string}[GRAY]][END]";
PDA_ASSEMBLY_{bigtier}_{bigname}_NAME = "{coloredname}";
PDA_ASSEMBLY_{bigtier}_{bigname}_MODS = "[GRAY][[END]{temp_mods_string}[GRAY]][END]";
PDA_ASSEMBLY_{bigtier}_{bigname}_ICON = "{assembly['icon']}";
PDA_ASSEMBLY_{bigtier}_{bigname}_HEIGHT = "0";
PDA_ASSEMBLY_{bigtier}_{bigname}_DESC = {assembly['actualDescription']}"[GREEN]Valid Weapons:[END]/n"\n{temp_string};
PDA_ASSEMBLY_{bigtier}_{bigname}_REQ = {temp_list_string};
'''

    # -----


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python arsenal.py input_folder output_file [separator token]")
    else:
        a = Arsenal()
        a.main()
