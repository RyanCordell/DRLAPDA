import sys
import os.path

import json
import re

from tkinter import filedialog as fd
from datetime import datetime

from typing import Dict, List, Optional, Union, Any, Literal

import pdb

# TODO: Examine memory footprint of all loaded JSON modules (currently around 555KB worth of JSON)
# TODO: Optimize loading
# TODO: Perhaps there's a better way to parse and compile all this data instead of smashing it all in memory?

def currentTime() -> datetime:
  return datetime.now().strftime("%H:%M:%S")

INPUT_FOLDER_ARG : int = 1
OUTPUT_FOLDER_ARG: int = 2
SEPARATOR_ARG    : int = 3

class Arsenal():
  outputData      : str = ''
  language_warning: str = '[enu default]\n\n// Please do not modify this file directly, it\'s specifically compiled and any changes may be lost.\n\n'
  loadedFiles     : str = ''
  data            : Any = ''
  loadedJson      : dict[str, Any] | str = {}
  separatorToken  : str = ':'
  filler          : dict[str, Any] = dict()
  inputFiles      : list[str] = list()
  
  
  def resPadder(self, str: str, len: int) -> str:
    return str.rjust(len, ' ')

  def languagePadding(self, value: str) -> str:
    return Arsenal.resPadder(self, ' ', 4 - len(value))
  
  def isInvokedByCombiner(self) -> bool:
    return 'Combiner' in self.__class__.__name__
  
  def main(self) -> None:
    Arsenal.doInput(self)
    
    if (len(sys.argv) > 3): 
      if (sys.argv[SEPARATOR_ARG]):
        Arsenal.separatorToken = sys.argv[SEPARATOR_ARG]
    
    if (sys.argv[OUTPUT_FOLDER_ARG]):
        Arsenal.outputFile = sys.argv[OUTPUT_FOLDER_ARG]
        
    Arsenal.doCompile(self)
  
  def attemptPrint(self, line: str) -> None:
    if (Arsenal.isInvokedByCombiner(self) and hasattr(self, 'printline')): self.printLine(line)
    else: print(line)
      
  def attemptClearResults(self) -> None:
    if (Arsenal.isInvokedByCombiner(self) and hasattr(self, 'clearResults')): self.clearResults()

  def doInput(self) -> None:
    print(Arsenal.isInvokedByCombiner(self))
    if (Arsenal.isInvokedByCombiner(self) and hasattr(self, 'currentPath')) :
      if (not self.currentPath): self.currentPath = os.path.dirname(os.path.realpath(__file__))
      
      if (self.currentPath):
        selectDirectory: str = fd.askdirectory(title='Open folder of JSON files', initialdir=self.currentPath)
        
        if (selectDirectory):
          Arsenal.inputFiles = [os.path.join(selectDirectory, filename) for filename in os.listdir(selectDirectory) if filename.endswith('.json')]
        
    else:
      if (sys.argv[INPUT_FOLDER_ARG]):
        if (not os.path.isdir(sys.argv[INPUT_FOLDER_ARG])): return None
        for filename in os.listdir(sys.argv[INPUT_FOLDER_ARG]):
          if (filename.endswith('.json')):
            Arsenal.inputFiles.append(os.path.join(sys.argv[INPUT_FOLDER_ARG], filename))
      else:
        return None

    Arsenal.attemptClearResults(self)
    
    if (Arsenal.inputFiles):
      Arsenal.attemptPrint(self, '[%s] Files selected: %s\n' % (currentTime(), list(Arsenal.inputFiles)))
      Arsenal.filler = {}
      
      for _, file in enumerate(Arsenal.inputFiles):
        Arsenal.attemptPrint(self, '[%s] Loaded JSON into filler memory: %s\n' % (currentTime(), file))
        Arsenal.loadedFiles += os.path.basename(file) + '\n'

        if ('data.json' in file):
          with open(os.path.normpath(file), mode='r', encoding='utf-8') as freshdata:
            Arsenal.filler = json.load(freshdata)
            
        if file:
          with open(os.path.normpath(file), mode='r', encoding='utf-8') as jsonBuffer:
            Arsenal.loadedJson.update(json.load(jsonBuffer))
    else:
      Arsenal.attemptPrint(self, '[%s] No JSON files selected\n' % currentTime())

  def clearWindow(self):
    Arsenal.attemptPrint(self, line='[%s] Clearing window\n' % currentTime())
    Arsenal.attemptClearResults(self)

  def doCompile(self):
    if ('weapons'    in Arsenal.loadedJson): Arsenal.processWeapons(self,Arsenal.loadedJson['weapons'], True)
    if ('equipment'  in Arsenal.loadedJson): Arsenal.processEquipment(self, Arsenal.loadedJson['equipment'], True)
    if ('modeffect'  in Arsenal.loadedJson): Arsenal.processModEffect(self, Arsenal.loadedJson['modeffect'], True)
    if ('assemblies' in Arsenal.loadedJson): Arsenal.processAssemblies(self, Arsenal.loadedJson, True)

  def doQuasiCompile(self):
    if ('weapons'    in Arsenal.loadedJson): Arsenal.processWeapons(self, Arsenal.loadedJson['weapons'], False)
    if ('equipment'  in Arsenal.loadedJson): Arsenal.processEquipment(self, Arsenal.loadedJson['equipment'], False)
    if ('modeffect'  in Arsenal.loadedJson): Arsenal.processModEffect(self, Arsenal.loadedJson['modeffect'], False)
    if ('assemblies' in Arsenal.loadedJson): Arsenal.processAssemblies(self, Arsenal.loadedJson, False)

  def doOutput(self, name: str):
    if (Arsenal.isInvokedByCombiner(self) and hasattr(self, 'currentPath') and self.currentPath):
      Arsenal.outputData: str = fd.asksaveasfile(
        title='Save file as..',
        initialfile=name,
        initialdir=self.currentPath,
        filetypes=(
          ('Text files', '*.txt'),
          ('All files', '*.*')
        )
      ) # type: ignore
      
      if (not Arsenal.outputData): 
        Arsenal.attemptClearResults(self)
        Arsenal.attemptPrint(self, '[%s] No file chosen\n' % currentTime())
        if (hasattr(self, 'compileArsenal')): self.compileArsenal.configure(state='disabled')
        return 0
      else:
        return Arsenal.outputData
    else:
      if (not os.path.isdir(sys.argv[OUTPUT_FOLDER_ARG])): 
        os.mkdir(sys.argv[OUTPUT_FOLDER_ARG])
        
      newPath: str = os.path.join(sys.argv[OUTPUT_FOLDER_ARG], name)
      
      with open(file=newPath, mode='w+', encoding='utf-8') as newFile:
        newFile.write('')
        
      Arsenal.outputData = newPath
      return Arsenal.outputData
        

  def handleColors(self, dict: dict[str, Any], str: str, method: str) -> str:
    if (not str or len(dict) < 1): 
      Arsenal.attemptPrint(self, '[%s] No data found to process\n' % currentTime())
      return 'false'

    noColors = 1
    
    for i in dict:
      if ('colors' in i):
        noColors = 0

    if (noColors): 
      Arsenal.attemptPrint(self, '[%s] No such property: colors\n' % currentTime())
      return 'false'

    for i in dict:
      if ('colors' in i):
        colors = dict[i].items()
        for colorKey, colorValue in colors:
          str = str.replace('['+colorKey+']', '\\c'+colorValue if method == 'revert' else '')

    return str

  # -----
  def processWeapons(self, weapons: dict[str, Any], doOutput: bool) -> None | Literal[0]:
    if (not weapons): return 0
    Arsenal.attemptPrint(self, '[%s] Parsing WEAPONS database\n' % currentTime())
    
    weaponModMax      : int = 0
    demonicWeapons    : int = 0
    basicModMax       : int = 0
    advancedModMax    : int = 0
    masterModMax      : int = 0
    # weaponMods        : str = ''
    # weaponModEffects  : str = ''
    # demonicArtifacts  : str = ''
    # weaponDescription : str = ''
    # weaponSDescription: str = ''
    # weaponLanguage    : str = ''
    weaponLanguage    : list[str] = list()
    weaponDescription : list[str] = list()
    weaponSDescription: list[str] = list()
    demonicArtifacts  : list[str] = list()
    weaponMods        : list[str] = list()
    weaponModEffects  : list[str] = list()
    weaponModList     : dict[str, Any] = {}
    # weaponArtifacts = ''

    for weapon in weapons:
      weapon: dict[str, Any]
      weaponDescription  = list()
      weaponSDescription = list()
      weaponMods         = list()
      # weaponArtifacts = ''
      
      if ('mods' in weapon):
        weaponModEffects.append('{')
        weaponModEffects.append(f'"RL{weapon["name"]}", "{weapon["mods"]["bulk"]}", "{weapon["mods"]["power"]}", "{weapon["mods"]["agility"]}", "{weapon["mods"]["technical"]}", "{weapon["mods"]["sniper"]}", "{weapon["mods"]["firestorm"]}", "{weapon["mods"]["nano"]}"')
        weaponModEffects.append('},')
        weaponModMax     += 1

        modsLen = len(weapon['mods'])
        for i, modsFragment in enumerate(weapon['mods']):
          modsFragment: str = modsFragment.replace('\n', '/n')
          weaponMods.append(f'"{weapon['mods'][modsFragment]}{self.separatorToken}"')

          if (i < modsLen - 1):
            weaponMods.append(f'\n')

        weapon['actualMods'] = ''.join(weaponMods)

      if ('corruptions' in weapon):
        demonicArtifacts.append('{')
        demonicArtifacts.append(f'"RL{weapon["name"]}", "{weapon["corruptions"][0]}", "{weapon["corruptions"][INPUT_FOLDER_ARG]}", "{weapon["corruptions"][OUTPUT_FOLDER_ARG]}"')
        demonicArtifacts.append('},')
        demonicWeapons   += 1
      
      if ('tier' in weapon):
        match weapon['tier']:
          case 'Basic':    basicModMax    += 1
          case 'Advanced': advancedModMax += 1
          case 'Master':   masterModMax   += 1
          case _: pass
      
      if ('description' in weapon):
        descLen = len(weapon['description'])
        for i, descFragment in enumerate(weapon['description']):
          descFragment: str = descFragment.replace('\n', '/n')
          weaponDescription.append(f'"{descFragment}"')

          if (i < descLen - 1):
            weaponDescription.append(f'\n')

        weapon['actualDescription'] = ''.join(weaponDescription)
      
      if ('specialdesc' in weapon):
        descLen = len(weapon['specialdesc'])
        
        for i, descFragment in enumerate(weapon['specialdesc']):
          descFragment: str = descFragment.replace('\n', '/n')
          weaponSDescription.append(f'"{descFragment}"')

          if i < descLen - 1:
            weaponSDescription.append(f'\n')

        weapon['actualSpecialDesc'] = ''.join(weaponSDescription)

      weapon['flatname'] = Arsenal.handleColors(self, Arsenal.filler, weapon['prettyname'], 'strip')
      weaponLanguage.append(Arsenal.LANGUAGE_WEAPONS(self, weapon))
      weaponLanguage.append('\n')

      
    weaponModList['max']         = weaponModMax
    weaponModList['dmax']        = demonicWeapons
    weaponModList['basicmax']    = basicModMax
    weaponModList['advancedmax'] = advancedModMax
    weaponModList['mastermax']   = masterModMax
    weaponModList['list']        = ''.join(weaponModEffects)
    weaponModList['dlist']       = ''.join(demonicArtifacts)

    tempString: str = ''.join(weaponLanguage)
    tempString = Arsenal.handleColors(self, Arsenal.filler, tempString, 'revert')

    tempString = tempString.replace('[INNERQUOTE]', '\\"')
    tempString = re.sub('/(\n)/g', '\\n', tempString)
    tempString = re.sub('/(;)\\n/gm', ';', tempString)
    tempString = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', '', tempString)
    tempString = re.sub('/( {3,})\\n/gm', '', tempString)
    tempString = re.sub('/^\\n( {1,})/gm', '', tempString)
    tempString = tempString.replace('/n', '\\n')

    languageWeaponOutput: str = Arsenal.language_warning + tempString
    
    if (doOutput):
      Arsenal.doOutput(self, 'language.auto.weapons')
      
      if (Arsenal.outputData):
        filePath: str = ''
        
        if (hasattr(Arsenal.outputData, 'name')):
          filePath = Arsenal.outputData.name
        else:
          filePath = Arsenal.outputData
        
        if (len(filePath) > 0):
          with open(filePath, mode='w', encoding='utf-8') as file:
            file.write(languageWeaponOutput)
    
      Arsenal.attemptPrint(self, '[%s] Weapons complete. Created/updated language.auto.weapons (size %s bytes)\n' % (currentTime(), os.path.getsize(filePath)))
    else: 
      Arsenal.attemptPrint(self, '[%s] Ending weapons processing.\n' % currentTime())
      Arsenal.attemptPrint(self, '[%s] %s.\n' % (currentTime(), languageWeaponOutput))
    
  def processEquipment(self, equipment: dict[str, Any], doOutput: bool) -> None | Literal[0]:
    if (not equipment): return 0
    Arsenal.attemptPrint(self, '[%s] Reading EQUIPMENT...\n' % currentTime())

    # headerArmorList  : str = ''
    # languageArmorList: str = ''
    equipmentMax     : int = 0
    # equipDescription : str = ''
    languageArmorList: list[str] = list()
    headerArmorList  : list[str] = list()
    equipDescription : list[str] = list()
    

    for equip in equipment:
      equip: dict[str, Any]
      equipDescription = list()
      headerArmorList.append('{')
      headerArmorList.append(f'"RL{equip['name']}", "{equip['name'].upper()}"')
      headerArmorList.append('},')
      # headerArmorList += '{'
      # headerArmorList += f'''"RL{equip['name']}", "{equip['name'].upper()}"'''
      # headerArmorList += '},'
      equipmentMax    += 1

      if ('description' in equip):
        for descFragment in equip['description']:
          descFragment: str = descFragment.replace('\n', '/n')
          equipDescription.append(f'"{descFragment}"\n')
          # equipDescription += f'"{descFragment}"\n'
          
        equip['actualDescription'] = ''.join(equipDescription)

      languageArmorList.append(Arsenal.LANGUAGE_EQUIPMENT(self, equip))
      languageArmorList.append('\n')

    equipmentList: dict[str, Any]  = {}
    equipmentList['max']  = equipmentMax
    equipmentList['list'] = ''.join(headerArmorList)

    arsenalDB = Arsenal.PDA_ARM(self, equipmentList)
    arsenalDB = arsenalDB.replace("'", '"')

    tempString: str = ''.join(languageArmorList)
    
    if (doOutput):
      Arsenal.doOutput(self, 'equipment.idb')
      
      if (Arsenal.outputData):
        filePath: str = ''
        
        if (hasattr(Arsenal.outputData, 'name')):
          filePath = Arsenal.outputData.name
        else:
          filePath = Arsenal.outputData
        
        if (len(filePath) > 0):
          with open(filePath, mode='w', encoding='utf-8') as file:
            file.write(arsenalDB)

      Arsenal.attemptPrint(self, '[%s] Created Equipment ACS array list as equipment.idb (size %s bytes)\n' % (currentTime(), os.path.getsize(filePath)))
    else: 
      Arsenal.attemptPrint(self, '[%s] Created ACS array list for EQUIPMENT\n' % currentTime())
      Arsenal.attemptPrint(self, '[%s] %s\n' % (currentTime(), arsenalDB))

    for i in Arsenal.filler:
      if ('attributes' in i):
        attributes = Arsenal.filler[i].items()
        
        for attributeKey, attributeValue in attributes:
          tempString = tempString.replace(attributeKey, attributeValue)

    Arsenal.attemptPrint(self, '[%s] Keywords translated into attributes\n' % currentTime())

    tempString = re.sub('/(\n)/g', '\\n', tempString)
    tempString = re.sub('/(;)\\n/gm', ';', tempString)
    tempString = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', '', tempString)
    
    tempString = tempString.replace('/n', '\\n')
    
    tempString = Arsenal.handleColors(self, Arsenal.filler, tempString, 'revert')

    languageArmorOutput = Arsenal.language_warning + tempString
    
    if (doOutput):
      Arsenal.doOutput(self, 'language.auto.equipment')
      
      if (Arsenal.outputData):
        filePath: str = ''
        if (hasattr(Arsenal.outputData, 'name')):
          filePath = Arsenal.outputData.name
        else:
          filePath = Arsenal.outputData
          
        if (len(filePath) > 0):
          with open(filePath, mode='w', encoding='utf-8') as file:
            file.write(languageArmorOutput)
          
      Arsenal.attemptPrint(self, '[%s] Finished Equipment. Generated language.auto.equipment (size %s bytes)\n' % (currentTime(), os.path.getsize(filePath)))
    else:
      Arsenal.attemptPrint(self, '[%s] Done with processing equipment.\n' % currentTime())
      Arsenal.attemptPrint(self, '[%s] %s.\n' % (currentTime(), languageArmorOutput))

  def processModEffect(self, mods: dict[str, Any], doOutput: bool) -> None | Literal[0]:
    if (not mods): return 0

    # modEffectList = ''
    modEffectList: list[str] = list()
    
    for mod in mods:
      mod: dict[str, Any]
      modEffectListLen: int = len(mod['effect'])
        
      if (type(mod['effect']) == str) :
        modEffectList.append(f'''{mod['name']} = "{mod['effect']}";''')
        
      if (type(mod['effect']) == list or type(mod['effect']) == dict) :
        modEffectList.append(f'''{mod['name']} = ''')
        
        for i, modEffectFragment in enumerate(mod['effect']):
          modEffectFragment: str = modEffectFragment.replace('\n', '/n')
          modEffectList.append(f'"{modEffectFragment}"')

          if i < modEffectListLen - 1:
            modEffectList.append(f'\n')
            
        modEffectList.append(f';')
        
      modEffectList.append('\n')

    tempString: str = ''.join(modEffectList)
    tempString = Arsenal.handleColors(self, Arsenal.filler, tempString, 'revert')
    
    languageModOutput: Any | str = Arsenal.language_warning + tempString
    
    Arsenal.attemptPrint(self, '[%s] Done parsing mod effects DB.\n' % currentTime())

    if (doOutput):
      Arsenal.doOutput(self, 'language.auto.mods')
      
      if (Arsenal.outputData):
        filePath: str = ''
        
        if (hasattr(Arsenal.outputData, 'name')):
          filePath = Arsenal.outputData.name
        else:
          filePath = Arsenal.outputData
          
        if (len(filePath) > 0):
          with open(filePath, mode='w', encoding='utf-8') as file:
            file.write(languageModOutput)
            
      Arsenal.attemptPrint(self, '[%s] Created language.auto.mods (size %s bytes)\n' % (currentTime(), os.path.getsize(filePath)))
    else: 
      Arsenal.attemptPrint(self, '[%s] \n'  % currentTime())
      Arsenal.attemptPrint(self, '[%s] %s.\n' % (currentTime(), languageModOutput))

  def processAssemblies(self, data: dict[str, Any], doOutput: bool) -> None | Literal[0]:
    if (not data): return 0

    headerAssemblyMax   : int = 0
    headerUniqueMax     : int = 0
    basicMax            : int = 0
    advancedMax         : int = 0
    masterMax           : int = 0
    # headerExoticList    : str = ''
    # assemblyDescription : str = ''
    # headerAssemblyList  : str = ''
    # languageAssemblyList: str = f'''PDA_ASSEMBLY_REQUIREMENTS = "\\cdRequirements:\\c-\\n";\n'''
    assemblyDescription : list[str] = list()
    headerAssemblyList  : list[str] = list()
    languageAssemblyList: list[str] = list()
    headerExoticList    : list[str] = list()

    # languageAssemblyList += 'PDA_ASSEMBLIES='
    languageAssemblyList.append(f'''PDA_ASSEMBLY_REQUIREMENTS = "\\cdRequirements:\\c-\\n";\n''')
    languageAssemblyList.append('PDA_ASSEMBLIES=')
    for i, assembly in enumerate(data['assemblies']):
      # languageAssemblyList += f'''"RL{assembly['name']}AssemblyLearntToken{self.separatorToken}PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}{self.separatorToken}"'''
      languageAssemblyList.append(f'''"RL{assembly['name']}AssemblyLearntToken{self.separatorToken}PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}{self.separatorToken}"''')
      
      if (i < len(data['assemblies']) - 1):
        # languageAssemblyList += '\n'
        languageAssemblyList.append('\n')

    languageAssemblyList.append(';')
    languageAssemblyList.append('\n')
    languageAssemblyList.append('\n')
    languageAssemblyList.append(f'''PDA_SEPARATOR_CHARACTER="{self.separatorToken}";''')
    languageAssemblyList.append('\n')
    languageAssemblyList.append('\n')

    for assembly in data['assemblies']:
      assemblyDescription = list()
      
      headerAssemblyList.append('{')
      headerAssemblyList.append(f'''"RL{assembly['name']}AssemblyLearntToken", "PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}"''')
      headerAssemblyList.append('},')
      headerAssemblyMax += 1

      match assembly['tier']:
        case 'Basic':    basicMax    += 1
        case 'Advanced': advancedMax += 1
        case 'Master':   masterMax   += 1
        case _:          pass

      if ('description' in assembly):
        descLen = len(assembly['description'])
        
        for i, descFragment in enumerate(assembly['description']):
          descFragment: str = descFragment.replace('\n', '/n')
          
          if i < descLen - 1:
            assemblyDescription.append(f'"{descFragment}"\n')
          else:
            assemblyDescription.append(f'"{descFragment}"')
            
        assembly['actualDescription'] = ''.join(assemblyDescription)

      languageAssemblyList.append(self.LANGUAGE_ASSEMBLIES(assembly))
      languageAssemblyList.append('\n')

    tempString: str = ''.join(languageAssemblyList)
    
    tempString = re.sub('/(\n)/g', '\\n', tempString)
    tempString = re.sub('/(;)\\n/gm', ';', tempString)
    tempString = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', '', tempString)
    
    tempString = tempString.replace('/n', '\\n')
    
    tempString = Arsenal.handleColors(self, Arsenal.filler, tempString, 'revert')
  
    for weapon in data['weapons']:
      weapon: dict[str, Any] 
      if (weapon['tier'] == 'Unique' or weapon['tier'] == 'Demonic' or weapon['tier'] == 'Legendary'):
        if ('unmoddable' in weapon):
          headerExoticList.append('{')
          headerExoticList.append(f'''"RL{weapon['name']}", "null", "null", "null"''')
          headerExoticList.append('},')
        else:
          headerExoticList.append('{')
          headerExoticList.append(f'''"RL{weapon['name']}", "RL{weapon['name']}SniperLearntToken", "RL{weapon['name']}FirestormLearntToken", "RL{weapon['name']}NanoLearntToken"''')
          headerExoticList.append('},')
          
        headerUniqueMax += 1
    
    languageAssemblyList.append(f'''
DRLA_ASSEMBLYMAX="{headerAssemblyMax}";
DRLA_ASSEMBLYELEMENTS="2";
DRLA_EXOTICEFFECTS_MAX="{headerUniqueMax}";
DRLA_EXOTICELEMENTS="4";
DRLA_BASICMAX="{basicMax}";
DRLA_ADVANCEDMAX="{advancedMax}";
DRLA_MASTERMAX="{masterMax}";
''')

    languageAssemblyOutput: str = Arsenal.language_warning + tempString
    
    if (doOutput):
      Arsenal.doOutput(self, 'language.auto.assemblies')
      
      if (Arsenal.outputData):
        filePath: str = ''
        
        if (hasattr(Arsenal.outputData, 'name')):
          filePath = Arsenal.outputData.name
        else:
          filePath = Arsenal.outputData
        
        if (len(filePath) > 0):
          with open(filePath, mode='w', encoding='utf-8') as file:
            file.write(languageAssemblyOutput)

      Arsenal.attemptPrint(self, '[%s] Created language.auto.assemblies\n' % currentTime())
    else:
      Arsenal.attemptPrint(self, '[%s] Created nothing\n' % currentTime())
      Arsenal.attemptPrint(self, '[%s] %s.\n' % (currentTime(), languageAssemblyOutput))

    assemblyList: dict[str, Any] = {}
    
    assemblyList['list']         = ''.join(headerAssemblyList)
    assemblyList['exotics']      = ''.join(headerExoticList)
    
    assemblyList['max']          = headerAssemblyMax
    assemblyList['uniquemax']    = headerUniqueMax
    assemblyList['basicmax']     = basicMax
    assemblyList['advancedmax']  = advancedMax
    assemblyList['mastermax']    = masterMax
    

    Arsenal.attemptPrint(self, '[%s] Finished compilation\n' % currentTime())

  # -----
  
  def PDA_ARM(self, equipment: dict[str, Any]) -> str:
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
  
  def LANGUAGE_WEAPONS(self, weapon: dict[str, Any]):
    if ('name' not in weapon):
      return ''

    bigname: str = weapon['name'].upper()

    fragment: list[str] = list(f'''PDA_WEAPON_{bigname}_ACTOR = "RL{bigname}";\n''')

    if ('prettyname' in weapon): 
      fragment.append(f'''PDA_WEAPON_{bigname}_NAME = "{weapon['prettyname']}";\n''')
      fragment.append(f'''PDA_WEAPON_{bigname}_FLATNAME = "{weapon['flatname']}";\n''')
    if ('actualDescription' in weapon): 
      fragment.append(f'''PDA_WEAPON_{bigname}_DESC = {weapon['actualDescription']};\n''')
    if ('specialpretty' in weapon): 
      fragment.append(f'''PDA_WEAPON_{bigname}DEMONARTIFACTS_NAME = "{weapon['specialpretty']}";\n''')
    if ('specialdesc' in weapon): 
      fragment.append(f'''PDA_WEAPON_{bigname}DEMONARTIFACTS_DESC = {weapon['actualSpecialDesc']};\n''')
    if ('mods' in weapon): 
      fragment.append(f'''PDA_WEAPON_{bigname}_MODS = {weapon['actualMods']};\n''')
    # if ('corruptions' in weapon): 
    #   fragment += f'''PDA_ARTIFACT_{bigname}_ARTIFACTS = {weapon['actualArtifacts']};\n'''

    return ''.join(fragment)

  def LANGUAGE_EQUIPMENT(self, equipment: dict[str, Any]) -> str | Literal[0]: 
    if (not Arsenal.filler): 
      print("Arsenal.filler is empty")
      return 0
    if ('name' not in equipment): 
      print("Name not found in equipment")
      return 0

    bigname         : str = equipment['name'].upper()
    coloredequipment: str = equipment['prettyname']
    flatequipment   : str = Arsenal.handleColors(self, Arsenal.filler, equipment['prettyname'], 'strip')

    atts: list[str] = list()
    for attr in equipment['attributes']:
      atts.append(f'''" {attr}\\n"''')

    for f in Arsenal.filler:
      if ('colors' in f):
        colors = Arsenal.filler[f].items()
        
        for colorKey, colorValue in colors:
          if (colorKey.upper() == equipment['tier'].upper()):
            coloredequipment = f'''\\c{colorValue}{equipment['prettyname']}\\c-'''

    construct: list[str] = list(f'''
PDA_ARMOR_{bigname}_ICON = "{equipment['icon']}";
PDA_ARMOR_{bigname}_NAME = "{coloredequipment}";
PDA_ARMOR_{bigname}_FLATNAME = "{flatequipment}";
PDA_ARMOR_{bigname}_DESC = {equipment['actualDescription']};
PDA_ARMOR_{bigname}_PROT = "{Arsenal.languagePadding(self, equipment['protection'])}{equipment['protection']}% [GOLD]Protection[END]";
PDA_ARMOR_{bigname}_RENPROT = "{Arsenal.languagePadding(self, equipment['renprotection'])}{equipment['renprotection']}% [GOLD]Protection[END]";''')

    if 'resistances' in equipment:
      res: dict[str, Any] = equipment['resistances']
      construct.append(f'''
PDA_ARMOR_{bigname}_RES = 
  "{Arsenal.languagePadding(self, res['melee'])}{res['melee']}% [DARKGRAY]Melee[END]  "
  "{Arsenal.languagePadding(self, res['bullet'])}{res['bullet']}% [GRAY]Bullet[END] \\n"
  "{Arsenal.languagePadding(self, res['fire'])}{res['fire']}% [RED]Fire[END]   "
  "{Arsenal.languagePadding(self, res['cryo'])}{res['cryo']}% [CYAN]Cryo[END]   \\n"
  "{Arsenal.languagePadding(self, res['plasma'])}{res['plasma']}% [BLUE]Plasma[END] "
  "{Arsenal.languagePadding(self, res['electric'])}{res['electric']}% [YELLOW]Electric[END]\\n"
  "{Arsenal.languagePadding(self, res['poison'])}{res['poison']}% [PURPLE]Poison[END] "
  "{Arsenal.languagePadding(self, res['radiation'])}{res['radiation']}% [GREEN]Radiation[END]\\n";''')
      construct.append('\n')
    
    if 'cyborgstats' in equipment:
      cybres: dict[str, Any] = equipment['cyborgstats']['resistances']
      construct.append(f'''PDA_ARMOR_{bigname}_CYBRES =''')
      if 'kinetic' in cybres:   construct.append(f'''"{Arsenal.languagePadding(self, cybres['kinetic'])}{cybres['kinetic']}% [WHITE]Kinetic Plating[END]\\n"''')
      if 'thermal' in cybres:   construct.append(f'''"{Arsenal.languagePadding(self, cybres['thermal'])}{cybres['thermal']}% [RED]Thermal Dampeners[END]\\n"''')
      if 'refractor' in cybres: construct.append(f'''"{Arsenal.languagePadding(self, cybres['refractor'])}{cybres['refractor']}% [BLUE]Refractor Field[END]\\n"''')
      if 'organic' in cybres:   construct.append(f'''"{Arsenal.languagePadding(self, cybres['organic'])}{cybres['organic']}% [GREEN]Organic Recovery[END]\\n"''')
      construct.append(f'''"{Arsenal.languagePadding(self, cybres['hazard'])}{cybres['hazard']}% [YELLOW]Hazard Shielding[END]\\n";''')

    construct.append(f'''
PDA_ARMOR_{bigname}_CYBAUG = "{equipment['cyborgstats']['augment']}";
PDA_ARMOR_{bigname}_ATTR = {''.join(atts)};
    ''')

    return ''.join(construct)
 
  def LANGUAGE_ASSEMBLIES(self, assembly: dict[str, Any]) -> str | Literal[0]:
    if (not Arsenal.filler): return 0
    if ('name' not in assembly):
      print('Name not found in assembly data')
      return ''

    bigname    : str = assembly['name'].upper()
    bigtier    : str = assembly['tier'].upper()
    coloredname: str = ''

    mods     : list[str] = list()
    valid    : list[str] = list()
    validlist: list[str] = list()
    colors   : list[str] = list()
    
    descLen  : int = 0

    for mod in assembly['mods']:
      for f in Arsenal.filler:
        if ('colors' in f):
          colors = Arsenal.filler[f].items()
          
          for colorKey, colorValue in colors:
            if (colorKey.upper() == mod):
              mods.append(f'''\\c{colorValue}{mod[0]}\\c-''')

    for f in Arsenal.filler:
      if ('colors' in f):
        colors = Arsenal.filler[f].items()
        
        for colorKey, colorValue in colors:
          if (colorKey.upper() == assembly['tier'].upper()):
            coloredname = f'''\\c{colorValue}{assembly['prettyname']}\\c-'''

    descLen = len(assembly['valid'])
    
    for i, validassemblies in enumerate(assembly['valid']):
      validassemblies: str = validassemblies.replace('\n', '/n')
      
      if i < descLen - 1:
        valid.append(f'''"{validassemblies}"\n''')
      else:
        valid.append(f'''"{validassemblies}"''')

    descLen = len(assembly['validlist'])
    for i, validweapon in enumerate(assembly['validlist']):
      validweapon: str = validweapon.replace('\n', '/n')
      
      if i < descLen - 1:
        validlist.append(f'''"{validweapon}"\n''')
      else:
        validlist.append(f'''"{validweapon}"''')

    tempString: str = ''.join(valid)
    tempString = tempString.replace('->', '[YELLOW]->[END]')

    return f'''
PDA_ASSEMBLY_{bigtier}_{bigname} = "{assembly['prettyname']} [GRAY][[END]{mods}[GRAY]][END]";
PDA_ASSEMBLY_{bigtier}_{bigname}_NAME = "{coloredname}";
PDA_ASSEMBLY_{bigtier}_{bigname}_MODS = "[GRAY][[END]{mods}[GRAY]][END]";
PDA_ASSEMBLY_{bigtier}_{bigname}_ICON = "{assembly['icon']}";
PDA_ASSEMBLY_{bigtier}_{bigname}_HEIGHT = "0";
PDA_ASSEMBLY_{bigtier}_{bigname}_DESC = {assembly['actualDescription']}"[GREEN]Valid Weapons:[END]/n"\n{tempString};
PDA_ASSEMBLY_{bigtier}_{bigname}_REQ = {validlist};
    '''
  
  # -----
  
if __name__ == '__main__':
  if (len(sys.argv) < 2):
    print("Usage: python arsenal.py input_folder output_file [separator token]")
  else:
    self = Arsenal()
    self.main()