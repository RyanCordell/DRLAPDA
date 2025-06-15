import sys
import os.path

import json
import re

from tkinter import filedialog as fd
from datetime import datetime

from typing import Any, Literal


def current_time() -> datetime:
    return datetime.now().strftime("%H:%M:%S")


INPUT_FOLDER_ARG: int = 1
OUTPUT_FOLDER_ARG: int = 2
SEPARATOR_ARG: int = 3


class Arsenal:
    output_data: str = ""
    language_warning: str = '''[enu default]\n\n//
  Please do not modify this file directly,
  it\'s specifically compiled and any changes may be lost.\n\n'''
    data: Any = ""
    loaded_json: dict[str, Any] | str = {}
    loaded_files: str = ""
    separator_token: str = ":"
    filler: dict[str, Any] = {}

    input_files: list[str] = []
    output_file: str = ""

    colors: dict[str, Any] = {}
    attributes: dict[str, Any] = {}

    def res_padder(self, str_to_pad: str, padding_length: int) -> str:
        return str_to_pad.rjust(padding_length, " ")

    def language_padding(self, value: str) -> str:
        return Arsenal.res_padder(self, " ", 4 - len(value))

    def is_invoked_by_combiner(self) -> bool:
        return "Combiner" in self.__class__.__name__

    def main(self) -> None:
        Arsenal.do_input(self)

        if len(sys.argv) > 3:
            if sys.argv[SEPARATOR_ARG]:
                Arsenal.separator_token = sys.argv[SEPARATOR_ARG]

        if sys.argv[OUTPUT_FOLDER_ARG]:
            Arsenal.output_file = sys.argv[OUTPUT_FOLDER_ARG]

        Arsenal.do_compile(self)

    def attempt_print(self, line: str) -> None:
        if Arsenal.is_invoked_by_combiner(self) and hasattr(self, "print_line"):
            self.print_line(line)
        else:
            print(line)

    def attempt_clear_results(self) -> None:
        if Arsenal.is_invoked_by_combiner(self) and hasattr(self, "clear_results"):
            self.clear_results()

    def __init__(self):
        self.current_path: str = ""

    def do_input(self) -> None:
        if Arsenal.is_invoked_by_combiner(self) and hasattr(self, "current_path"):

            if not self.current_path:
                self.current_path = os.path.dirname(os.path.realpath(__file__))

            if self.current_path:
                select_directory: str = fd.askdirectory(
                    title="Open folder of JSON files", initialdir=self.current_path
                )

                if select_directory:
                    Arsenal.input_files = [
                        os.path.join(select_directory, filename)
                        for filename in os.listdir(select_directory)
                        if filename.endswith(".json")
                    ]

        else:
            if sys.argv[INPUT_FOLDER_ARG]:
                if not os.path.isdir(sys.argv[INPUT_FOLDER_ARG]):
                    return None
                for filename in os.listdir(sys.argv[INPUT_FOLDER_ARG]):
                    if filename.endswith(".json"):
                        Arsenal.input_files.append(
                            os.path.join(sys.argv[INPUT_FOLDER_ARG], filename)
                        )

        Arsenal.attempt_clear_results(self)

        if Arsenal.input_files:
            Arsenal.attempt_print(
                self,
                f"{ current_time() } Files selected: {list(Arsenal.input_files)}\n",
            )
            Arsenal.filler: dict[str, Any] = {}

            for _, file in enumerate(Arsenal.input_files):
                Arsenal.attempt_print(
                    self, f"{ current_time() } Loaded JSON into filler memory: {file}\n"
                )
                Arsenal.loaded_files += os.path.basename(file) + "\n"

                if "data.json" in file:
                    with open(
                        os.path.normpath(file), mode="r", encoding="utf-8"
                    ) as freshdata:
                        Arsenal.filler = json.load(freshdata)

                if file:
                    with open(
                        os.path.normpath(file), mode="r", encoding="utf-8"
                    ) as json_buffer:
                        Arsenal.loaded_json.update(json.load(json_buffer))

            for f in Arsenal.filler:
                if "colors" in f:
                    Arsenal.colors = Arsenal.filler[f]
                if "attributes" in f:
                    Arsenal.attributes = Arsenal.filler[f]
        else:
            Arsenal.attempt_print(self, f"{ current_time() } No JSON files selected\n")

    def clearWindow(self):
        Arsenal.attempt_print(self, line=f"{ current_time() } Clearing window\n")
        Arsenal.attempt_clear_results(self)

    def do_compile(self):
        if "weapons" in Arsenal.loaded_json:
            Arsenal.process_weapons(self, Arsenal.loaded_json["weapons"], True)
        if "equipment" in Arsenal.loaded_json:
            Arsenal.process_equipment(self, Arsenal.loaded_json["equipment"], True)
        if "modeffect" in Arsenal.loaded_json:
            Arsenal.process_mod_effect(self, Arsenal.loaded_json["modeffect"], True)
        if "assemblies" in Arsenal.loaded_json:
            Arsenal.process_assemblies(self, Arsenal.loaded_json, True)

    def do_quasi_compile(self):
        if "weapons" in Arsenal.loaded_json:
            Arsenal.process_weapons(self, Arsenal.loaded_json["weapons"], False)
        if "equipment" in Arsenal.loaded_json:
            Arsenal.process_equipment(self, Arsenal.loaded_json["equipment"], False)
        if "modeffect" in Arsenal.loaded_json:
            Arsenal.process_mod_effect(self, Arsenal.loaded_json["modeffect"], False)
        if "assemblies" in Arsenal.loaded_json:
            Arsenal.process_assemblies(self, Arsenal.loaded_json, False)

    def do_output(self, name: str) -> str | None:
        if (
            Arsenal.is_invoked_by_combiner(self)
            and hasattr(self, "current_path")
            and self.current_path
        ):

            Arsenal.output_data: str = fd.asksaveasfile(
                title="Save file as..",
                initialfile=name,
                initialdir=self.current_path,
                filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            )  # type: ignore

            if not Arsenal.output_data:
                Arsenal.attempt_clear_results(self)
                Arsenal.attempt_print(self, f"{ current_time() } No file chosen\n")

                if hasattr(self, "compileArsenal"):
                    self.compileArsenal.configure(state="disabled")
        else:
            if not os.path.isdir(sys.argv[OUTPUT_FOLDER_ARG]):
                os.mkdir(sys.argv[OUTPUT_FOLDER_ARG])

            new_path: str = os.path.join(sys.argv[OUTPUT_FOLDER_ARG], name)

            with open(file=new_path, mode="w+", encoding="utf-8") as new_file:
                new_file.write("")

            Arsenal.output_data = new_path

    def handle_colors(self, str_to_color: str, method: str) -> str:
        if not str_to_color or len(Arsenal.colors) < 1:
            Arsenal.attempt_print(
                self, f"{ current_time() } No data found to process\n"
            )
            return "false"

        for color_key, color_value in Arsenal.colors.items():
            str_to_color = str_to_color.replace(
                "[" + color_key + "]", "\\c" + color_value if method == "revert" else ""
            )

        return str_to_color

    # -----
    def process_weapons(
        self, weapons: dict[str, Any], do_output: bool
    ) -> None | Literal[0]:
        Arsenal.attempt_print(self, f"{ current_time() } Parsing WEAPONS database\n")

        weapon_mod_max: int = 0
        demonic_weapons: int = 0
        basic_mod_max: int = 0
        advanced_mod_max: int = 0
        master_mod_max: int = 0
        # weapon_mods        : str = ''
        # weapon_mod_effects  : str = ''
        # demonic_artifacts  : str = ''
        # weapon_description : str = ''
        # weapon_s_description: str = ''
        # weapon_language    : str = ''
        weapon_language: list[str] = []
        weapon_description: list[str] = []
        weapon_s_description: list[str] = []
        demonic_artifacts: list[str] = []
        weapon_mods: list[str] = []
        weapon_mod_effects: list[str] = []
        weapon_mod_list: dict[str, Any] = {}
        # weaponArtifacts = ''

        for weapon in weapons:
            weapon: dict[str, Any]
            weapon_description = []
            weapon_s_description = []
            weapon_mods = []
            # weaponArtifacts = ''

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
                                  "{weapon["mods"]["nano"]}"'''
                )
                weapon_mod_effects.append("},")
                weapon_mod_max += 1

                mods_len = len(weapon["mods"])
                for i, mods_fragment in enumerate(weapon["mods"]):
                    mods_fragment: str = mods_fragment.replace("\n", "/n")
                    weapon_mods.append(
                        f'"{weapon['mods'][mods_fragment]}{self.separator_token}"'
                    )

                    if i < mods_len - 1:
                        weapon_mods.append("\n")

                weapon["actualMods"] = "".join(weapon_mods)

            if "corruptions" in weapon:
                demonic_artifacts.append("{")
                demonic_artifacts.append(
                    f'''
                    "RL{weapon["name"]}",
                    "{weapon["corruptions"][0]}",
                    "{weapon["corruptions"][INPUT_FOLDER_ARG]}",
                    "{weapon["corruptions"][OUTPUT_FOLDER_ARG]}"
                    '''
                )
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

            weapon["flatname"] = Arsenal.handle_colors(
                self, weapon["prettyname"], "strip"
            )
            weapon_language.append(Arsenal.create_weapons_language(self, weapon))
            weapon_language.append("\n")

        weapon_mod_list["max"] = weapon_mod_max
        weapon_mod_list["dmax"] = demonic_weapons
        weapon_mod_list["basicmax"] = basic_mod_max
        weapon_mod_list["advancedmax"] = advanced_mod_max
        weapon_mod_list["mastermax"] = master_mod_max
        weapon_mod_list["list"] = "".join(weapon_mod_effects)
        weapon_mod_list["dlist"] = "".join(demonic_artifacts)

        temp_string: str = "".join(weapon_language)
        temp_string = Arsenal.handle_colors(self, temp_string, "revert")

        temp_string = temp_string.replace("[INNERQUOTE]", '\\"')
        temp_string = re.sub("/(\n)/g", "\\n", temp_string)
        temp_string = re.sub("/(;)\\n/gm", ";", temp_string)
        temp_string = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', "", temp_string)
        temp_string = re.sub("/( {3,})\\n/gm", "", temp_string)
        temp_string = re.sub("/^\\n( {1,})/gm", "", temp_string)
        temp_string = temp_string.replace("/n", "\\n")

        language_weapon_output: str = Arsenal.language_warning + temp_string

        if do_output:
            Arsenal.do_output(self, "language.auto.weapons")

            if Arsenal.output_data:
                file_path: str = ""

                if hasattr(Arsenal.output_data, "name"):
                    file_path = Arsenal.output_data.name
                else:
                    file_path = Arsenal.output_data

                if len(file_path) > 0:
                    with open(file_path, mode="w", encoding="utf-8") as file:
                        file.write(language_weapon_output)

            Arsenal.attempt_print(
                self,
                f'''{ current_time() } Processing weapons completed. Created/updated language.auto.weapons [{os.path.getsize(file_path)} bytes]\n''',
            )
        else:
            Arsenal.attempt_print(
                self, f"{ current_time() } Ending weapons processing.\n"
            )
            Arsenal.attempt_print(
                self, f"{ current_time() } {language_weapon_output}.\n"
            )

    def process_equipment(
        self, equipment: dict[str, Any], do_output: bool
    ) -> None | Literal[0]:
        Arsenal.attempt_print(self, f"{ current_time() } Reading EQUIPMENT...\n")

        # header_armor_list  : str = ''
        # language_armor_list: str = ''
        equipment_max: int = 0
        # equip_description : str = ''
        language_armor_list: list[str] = []
        header_armor_list: list[str] = []
        equip_description: list[str] = []

        for equip in equipment:
            equip: dict[str, Any]
            equip_description = []
            header_armor_list.append("{")
            header_armor_list.append(f'"RL{equip['name']}", "{equip['name'].upper()}"')
            header_armor_list.append("},")
            # header_armor_list += '{'
            # header_armor_list += f'''"RL{equip['name']}", "{equip['name'].upper()}"'''
            # header_armor_list += '},'
            equipment_max += 1

            if "description" in equip:
                for desc_fragment in equip["description"]:
                    desc_fragment: str = desc_fragment.replace("\n", "/n")
                    equip_description.append(f'"{desc_fragment}"\n')
                    # equip_description += f'"{desc_fragment}"\n'

                equip["actualDescription"] = "".join(equip_description)

            language_armor_list.append(Arsenal.create_equipment_language(self, equip))
            language_armor_list.append("\n")

        equipment_list: dict[str, Any] = {}
        equipment_list["max"] = equipment_max
        equipment_list["list"] = "".join(header_armor_list)

        arsenal_db = Arsenal.create_armor_acs_array(self, equipment_list)
        arsenal_db = arsenal_db.replace("'", '"')

        temp_string: str = "".join(language_armor_list)

        if do_output:
            Arsenal.do_output(self, "equipment.idb")

            if Arsenal.output_data:
                file_path: str = ""

                if hasattr(Arsenal.output_data, "name"):
                    file_path = Arsenal.output_data.name
                else:
                    file_path = Arsenal.output_data

                if len(file_path) > 0:
                    with open(file_path, mode="w", encoding="utf-8") as file:
                        file.write(arsenal_db)

            Arsenal.attempt_print(
                self,
                f'''{ current_time() } Created Equipment ACS array list as equipment.idb [{os.path.getsize(file_path)} bytes]\n''',
            )
        else:
            Arsenal.attempt_print(
                self, f"{ current_time() } Created ACS array list for EQUIPMENT\n"
            )
            Arsenal.attempt_print(self, f"{ current_time() } {arsenal_db}\n")

        # for i in Arsenal.filler:
        #   if ('attributes' in i):
        #     attributes = Arsenal.filler[i]

        for attribute_key, attribute_value in Arsenal.attributes.items():
            temp_string = temp_string.replace(attribute_key, attribute_value)

        Arsenal.attempt_print(
            self, f"{ current_time() } Keywords translated into attributes\n"
        )

        temp_string = re.sub("/(\n)/g", "\\n", temp_string)
        temp_string = re.sub("/(;)\\n/gm", ";", temp_string)
        temp_string = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', "", temp_string)

        temp_string = temp_string.replace("/n", "\\n")

        temp_string = Arsenal.handle_colors(self, temp_string, "revert")

        language_armor_output = Arsenal.language_warning + temp_string

        if do_output:
            Arsenal.do_output(self, "language.auto.equipment")

            if Arsenal.output_data:
                file_path: str = ""
                if hasattr(Arsenal.output_data, "name"):
                    file_path = Arsenal.output_data.name
                else:
                    file_path = Arsenal.output_data

                if len(file_path) > 0:
                    with open(file_path, mode="w", encoding="utf-8") as file:
                        file.write(language_armor_output)

            Arsenal.attempt_print(
                self,
                f'''{ current_time() } Finished Equipment. Generated language.auto.equipment [{os.path.getsize(file_path)} bytes]\n''',
            )
        else:
            Arsenal.attempt_print(
                self, f"{ current_time() } Done with processing equipment.\n"
            )
            Arsenal.attempt_print(
                self, f"{ current_time() } {language_armor_output}.\n"
            )

    def process_mod_effect(
        self, mods: dict[str, Any], do_output: bool
    ) -> None | Literal[0]:
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
        temp_string = Arsenal.handle_colors(self, temp_string, "revert")

        language_mod_output: Any | str = Arsenal.language_warning + temp_string

        Arsenal.attempt_print(
            self, f"{ current_time() } Done parsing mod effects DB.\n"
        )

        if do_output:
            Arsenal.do_output(self, "language.auto.mods")

            if Arsenal.output_data:
                file_path: str = ""

                if hasattr(Arsenal.output_data, "name"):
                    file_path = Arsenal.output_data.name
                else:
                    file_path = Arsenal.output_data

                if len(file_path) > 0:
                    with open(file_path, mode="w", encoding="utf-8") as file:
                        file.write(language_mod_output)

            Arsenal.attempt_print(
                self,
                f'''{ current_time() } Created language.auto.mods [{os.path.getsize(file_path)} bytes]\n''',
            )
        else:
            Arsenal.attempt_print(self, f"{ current_time() } \n")
            Arsenal.attempt_print(self, f"{ current_time() } {language_mod_output}.\n")

    def process_assemblies(
        self, data: dict[str, Any], do_output: bool
    ) -> None | Literal[0]:
        header_assembly_max: int = 0
        header_unique_max: int = 0
        basic_max: int = 0
        advanced_max: int = 0
        master_max: int = 0
        assembly_description: list[str] = []
        header_assembly_list: list[str] = []
        language_assembly_list: list[str] = []
        header_exotic_list: list[str] = []

        # language_assembly_list += 'PDA_ASSEMBLIES='
        language_assembly_list.append(
            'PDA_ASSEMBLY_REQUIREMENTS = "\\cdRequirements:\\c-\\n";\n'
        )
        language_assembly_list.append("PDA_ASSEMBLIES=\"")
        for i, assembly in enumerate(data["assemblies"]):
            language_assembly_list.append(f'''RL{assembly['name']}AssemblyLearntToken{self.separator_token}PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}{self.separator_token}''')

            if i < len(data["assemblies"]) - 1:
                # language_assembly_list += '\n'
                language_assembly_list.append("\n")

        language_assembly_list.append("\";")
        language_assembly_list.append("\n")
        language_assembly_list.append("\n")
        language_assembly_list.append(
            f'''PDA_SEPARATOR_CHARACTER="{self.separator_token}";'''
        )
        language_assembly_list.append("\n")
        language_assembly_list.append("\n")

        for assembly in data["assemblies"]:
            assembly_description = []

            header_assembly_list.append("{")
            header_assembly_list.append(
                f'''
                "RL{assembly['name']}AssemblyLearntToken",
                "PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}"
            '''
            )
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

        temp_string = re.sub("/(\n)/g", "\\n", temp_string)
        temp_string = re.sub("/(;)\\n/gm", ";", temp_string)
        temp_string = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', "", temp_string)

        temp_string = temp_string.replace("/n", "\\n")

        temp_string = Arsenal.handle_colors(self, temp_string, "revert")

        for weapon in data["weapons"]:
            weapon: dict[str, Any]
            if (
                weapon["tier"] == "Unique"
                or weapon["tier"] == "Demonic"
                or weapon["tier"] == "Legendary"
            ):
                if "unmoddable" in weapon:
                    header_exotic_list.append("{")
                    header_exotic_list.append(
                        f'''"RL{weapon['name']}", "null", "null", "null"'''
                    )
                    header_exotic_list.append("},")
                else:
                    header_exotic_list.append("{")
                    header_exotic_list.append(
                        f'''
                        "RL{weapon['name']}",
                        "RL{weapon['name']}SniperLearntToken",
                        "RL{weapon['name']}FirestormLearntToken",
                        "RL{weapon['name']}NanoLearntToken"
                    '''
                    )
                    header_exotic_list.append("},")

                header_unique_max += 1

        language_assembly_list.append(
            f'''
DRLA_ASSEMBLYMAX="{header_assembly_max}";
DRLA_ASSEMBLYELEMENTS="2";
DRLA_EXOTICEFFECTS_MAX="{header_unique_max}";
DRLA_EXOTICELEMENTS="4";
DRLA_BASICMAX="{basic_max}";
DRLA_ADVANCEDMAX="{advanced_max}";
DRLA_MASTERMAX="{master_max}";
'''
        )

        language_assembly_output: str = Arsenal.language_warning + temp_string

        if do_output:
            Arsenal.do_output(self, "language.auto.assemblies")

            if Arsenal.output_data:
                file_path: str = ""

                if hasattr(Arsenal.output_data, "name"):
                    file_path = Arsenal.output_data.name
                else:
                    file_path = Arsenal.output_data

                if len(file_path) > 0:
                    with open(file_path, mode="w", encoding="utf-8") as file:
                        file.write(language_assembly_output)

            Arsenal.attempt_print(
                self, f"{ current_time() } Created language.auto.assemblies\n"
            )
        else:
            Arsenal.attempt_print(self, f"{ current_time() } Created nothing\n")
            Arsenal.attempt_print(
                self, f"{ current_time() } {language_assembly_output}.\n"
            )

        assembly_list: dict[str, Any] = {}

        assembly_list["list"] = "".join(header_assembly_list)
        assembly_list["exotics"] = "".join(header_exotic_list)

        assembly_list["max"] = header_assembly_max
        assembly_list["uniquemax"] = header_unique_max
        assembly_list["basicmax"] = basic_max
        assembly_list["advancedmax"] = advanced_max
        assembly_list["mastermax"] = master_max

        Arsenal.attempt_print(self, f"{ current_time() } Finished compilation\n")

    # -----

    def create_armor_acs_array(self, equipment: dict[str, Any]) -> str:
        # TODO: Export the active set bonuses into a separate JSON, or rely on Equipment instead?
        construct = f'''#library "PDA_ARM"

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
}};
    '''

        return construct

    # -----

    def create_weapons_language(self, weapon: dict[str, Any]):
        if "name" not in weapon:
            return ""

        bigname: str = weapon["name"].upper()

        fragment: list[str] = list(f'''PDA_WEAPON_{bigname}_ACTOR = "RL{bigname}";\n''')

        if "prettyname" in weapon:
            fragment.append(
                f'''
            PDA_WEAPON_{bigname}_NAME = "{weapon['prettyname']}";\n
            '''
            )
            fragment.append(
                f'''
            PDA_WEAPON_{bigname}_FLATNAME = "{weapon['flatname']}";\n
            '''
            )
        if "actualDescription" in weapon:
            fragment.append(
                f'''
            PDA_WEAPON_{bigname}_DESC = {weapon['actualDescription']};\n
            '''
            )
        if "specialpretty" in weapon:
            fragment.append(
                f'''
            PDA_WEAPON_{bigname}DEMONARTIFACTS_NAME = "{weapon['specialpretty']}";\n
            '''
            )
        if "specialdesc" in weapon:
            fragment.append(
                f'''
            PDA_WEAPON_{bigname}DEMONARTIFACTS_DESC = {weapon['actualSpecialDesc']};\n
            '''
            )
        if "mods" in weapon:
            fragment.append(
                f'''
            PDA_WEAPON_{bigname}_MODS = {weapon['actualMods']};\n
            '''
            )
        # if ('corruptions' in weapon):
        #   fragment += f'''PDA_ARTIFACT_{bigname}_ARTIFACTS = {weapon['actualArtifacts']};\n'''

        return "".join(fragment)

    def create_equipment_language(self, equipment: dict[str, Any]) -> str | Literal[0]:
        if not Arsenal.filler:
            print("Arsenal.filler is empty")
            return 0
        if "name" not in equipment:
            print("Name not found in equipment")
            return 0

        bigname: str = equipment["name"].upper()
        coloredequipment: str = equipment["prettyname"]
        flatequipment: str = Arsenal.handle_colors(
            self, equipment["prettyname"], "strip"
        )

        atts: list[str] = []
        for attr in equipment["attributes"]:
            atts.append(f'''" {attr}\\n"''')

        # for f in Arsenal.filler:
        #   if ('colors' in f):
        #     colors = Arsenal.filler[f]

        for color_key, color_value in Arsenal.colors.items():
            if color_key.upper() == equipment["tier"].upper():
                coloredequipment = f'''\\c{color_value}{equipment['prettyname']}\\c-'''

        construct: list[str] = list(
            f'''
PDA_ARMOR_{bigname}_ICON = "{equipment['icon']}";
PDA_ARMOR_{bigname}_NAME = "{coloredequipment}";
PDA_ARMOR_{bigname}_FLATNAME = "{flatequipment}";
PDA_ARMOR_{bigname}_DESC = {equipment['actualDescription']};
PDA_ARMOR_{bigname}_PROT = "{Arsenal.language_padding(self, equipment['protection'])}{equipment['protection']}% [GOLD]Protection[END]";
PDA_ARMOR_{bigname}_RENPROT = "{Arsenal.language_padding(self, equipment['renprotection'])}{equipment['renprotection']}% [GOLD]Protection[END]";'''
        )

        if "resistances" in equipment:
            res: dict[str, Any] = equipment["resistances"]
            construct.append(
                f'''
PDA_ARMOR_{bigname}_RES =
  "{Arsenal.language_padding(self, res['melee'])}{res['melee']}% [DARKGRAY]Melee[END]  "
  "{Arsenal.language_padding(self, res['bullet'])}{res['bullet']}% [GRAY]Bullet[END] \\n"
  "{Arsenal.language_padding(self, res['fire'])}{res['fire']}% [RED]Fire[END]   "
  "{Arsenal.language_padding(self, res['cryo'])}{res['cryo']}% [CYAN]Cryo[END]   \\n"
  "{Arsenal.language_padding(self, res['plasma'])}{res['plasma']}% [BLUE]Plasma[END] "
  "{Arsenal.language_padding(self, res['electric'])}{res['electric']}% [YELLOW]Electric[END]\\n"
  "{Arsenal.language_padding(self, res['poison'])}{res['poison']}% [PURPLE]Poison[END] "
  "{Arsenal.language_padding(self, res['radiation'])}{res['radiation']}% [GREEN]Radiation[END]\\n";'''
            )
            construct.append("\n")

        if "cyborgstats" in equipment:
            cybres: dict[str, Any] = equipment["cyborgstats"]["resistances"]
            construct.append(f'''PDA_ARMOR_{bigname}_CYBRES =''')

            if "kinetic" in cybres:
                construct.append(
                    f'''"{Arsenal.language_padding(self, cybres['kinetic'])}{cybres['kinetic']}% [WHITE]Kinetic Plating[END]\\n"'''
                )
            if "thermal" in cybres:
                construct.append(
                    f'''"{Arsenal.language_padding(self, cybres['thermal'])}{cybres['thermal']}% [RED]Thermal Dampeners[END]\\n"'''
                )
            if "refractor" in cybres:
                construct.append(
                    f'''"{Arsenal.language_padding(self, cybres['refractor'])}{cybres['refractor']}% [BLUE]Refractor Field[END]\\n"'''
                )
            if "organic" in cybres:
                construct.append(
                    f'''"{Arsenal.language_padding(self, cybres['organic'])}{cybres['organic']}% [GREEN]Organic Recovery[END]\\n"'''
                )

            construct.append(
                f'''"{Arsenal.language_padding(self, cybres['hazard'])}{cybres['hazard']}% [YELLOW]Hazard Shielding[END]\\n";'''
            )

        construct.append(f'''
PDA_ARMOR_{bigname}_CYBAUG = "{equipment['cyborgstats']['augment']}";
PDA_ARMOR_{bigname}_ATTR = {''.join(atts)};
    ''')

        return "".join(construct)

    def create_assemblies_language(self, assembly: dict[str, Any]) -> str | Literal[0]:
        if not Arsenal.filler:
            return 0
        if "name" not in assembly:
            print("Name not found in assembly data")
            return ""

        bigname: str = assembly["name"].upper()
        bigtier: str = assembly["tier"].upper()
        coloredname: str = ""

        mods: list[str] = []
        valid: list[str] = []
        validlist: list[str] = []

        desc_len: int = 0

        for mod in assembly["mods"]:
            for color_key, color_value in Arsenal.colors.items():
                if color_key.upper() == mod:
                    mods.append(f'''\\c{color_value}{mod[0]}\\c-''')

        for color_key, color_value in Arsenal.colors.items():
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

            validlist.append(f'''"{validweapon}\"''')
            if i < desc_len - 1:
                validlist.append("\n")

        temp_string: str = "".join(valid)
        temp_string = temp_string.replace("->", "[YELLOW]->[END]")

        return f'''
PDA_ASSEMBLY_{bigtier}_{bigname} = "{assembly['prettyname']} [GRAY][[END]{mods}[GRAY]][END]";
PDA_ASSEMBLY_{bigtier}_{bigname}_NAME = "{coloredname}";
PDA_ASSEMBLY_{bigtier}_{bigname}_MODS = "[GRAY][[END]{mods}[GRAY]][END]";
PDA_ASSEMBLY_{bigtier}_{bigname}_ICON = "{assembly['icon']}";
PDA_ASSEMBLY_{bigtier}_{bigname}_HEIGHT = "0";
PDA_ASSEMBLY_{bigtier}_{bigname}_DESC = {assembly['actualDescription']}"[GREEN]Valid Weapons:[END]/n"\n{temp_string};
PDA_ASSEMBLY_{bigtier}_{bigname}_REQ = {''.join(validlist)};
    '''

    # -----


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python arsenal.py input_folder output_file [separator token]")
    else:
        self = Arsenal()
        self.main()
