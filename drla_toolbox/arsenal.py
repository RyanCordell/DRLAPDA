import os.path
import sys
import customtkinter
import json
import re

from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from datetime import datetime
from typing import Dict, List, Optional, Union

# TODO: Examine memory footprint of all loaded JSON modules (currently around 555KB worth of JSON)
# TODO: Optimize loading
# TODO: Perhaps there's a better way to parse and compile all this data instead of smashing it all in memory?

def currentTime() -> datetime:
  return datetime.now().strftime("%H:%M:%S")

class Arsenal:
  outputData      : str = ''
  language_warning: str = '[enu default]\n\n// Please do not modify this file directly, it\'s specifically compiled and any changes may be lost.\n\n'
  loadedFiles     : str = ''

  def doInput(self):
    if (not self.currentPath): self.currentPath = os.path.dirname(os.path.realpath(__file__))
    
    self.inputFiles = fd.askopenfilenames(
      title='Open files',
      initialdir=self.currentPath,
      filetypes=(
        ('JSON files', '*.json'),
        ('All files', '*.*')
      ),
      defaultextension='.json'
    )

    self.clearResults()
    if (self.inputFiles):
      self.printLine('[%s] Files selected: %s\n' % (currentTime(), list(self.inputFiles)))
      # self.printLine('[%s] File selected: %s\n' % (currentTime(), os.path.normpath(self.inputFile)))
      self.filler = {}
      for _, file in enumerate(self.inputFiles):
        self.printLine('[%s] Loaded JSON into filler memory: %s\n' % (currentTime(), file))
        self.loadedFiles += os.path.basename(file) + '\n'

        if ('data.json' in file):
          with open(os.path.normpath(file), mode='r', encoding='utf-8') as freshdata:
            self.filler = json.load(freshdata)
            
        if file:
          with open(os.path.normpath(file), mode='r', encoding='utf-8') as jsonBuffer:
            self.loadedJson.update(json.load(jsonBuffer))
      # self.selected_files.configure(text=loadedFiles)
    else:
      self.printLine('[%s] No JSON files selected\n' % currentTime())

  def doQuasiCompile(self):
    if ('weapons'    in self.loadedJson): Arsenal.processWeapons(self, self.loadedJson['weapons'], False)
    if ('equipment'  in self.loadedJson): Arsenal.processEquipment(self, self.loadedJson['equipment'], False)
    if ('modeffect'  in self.loadedJson): Arsenal.processModEffect(self, self.loadedJson['modeffect'], False)
    if ('assemblies' in self.loadedJson): Arsenal.processAssemblies(self, self.loadedJson, False)

  def clearWindow(self):
    self.printLine('[%s] Clearing window\n' % currentTime())
    self.clearResults()

  def doCompile(self):
    if ('weapons'    in self.loadedJson): Arsenal.processWeapons(self, self.loadedJson['weapons'], True)
    if ('equipment'  in self.loadedJson): Arsenal.processEquipment(self, self.loadedJson['equipment'], True)
    if ('modeffect'  in self.loadedJson): Arsenal.processModEffect(self, self.loadedJson['modeffect'], True)
    if ('assemblies' in self.loadedJson): Arsenal.processAssemblies(self, self.loadedJson, True)

  def doOutput(self, name):
    self.outputData = fd.asksaveasfile(
      title='Save file as..',
      initialfile=name,
      initialdir=self.currentPath,
      filetypes=(
        ('Text files', '*.txt'),
        ('All files', '*.*')
      )
    )
    if (not self.outputData): 
      self.clearResults()
      self.printLine('[%s] No file chosen\n' % currentTime())
      self.compileArsenal.configure(state='disabled')
      return 0

  def handleColors(self, dict: dict, str: str, method: str):
    if (not str or len(dict) < 1): 
      self.printLine('[%s] No data found to process\n' % currentTime())
      return 'false'

    noColors = 1
    
    for i in dict:
      if ('colors' in i):
        noColors = 0

    if (noColors): 
      self.printLine('[%s] No such property: colors\n' % currentTime())
      return 'false'

    for i in dict:
      if ('colors' in i):
        colors = dict[i].items()
        for colorKey, colorValue in colors:
          str = str.replace('['+colorKey+']', '\\c'+colorValue if method == 'revert' else '')

    return str


  def processWeapons(self, weapons, doOutput):
    if (not weapons): return 0
    self.printLine('[%s] Parsing WEAPONS database\n' % currentTime())
    
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
    weaponLanguage    : list = list()
    weaponDescription : list = list()
    weaponSDescription: list = list()
    demonicArtifacts  : list = list()
    weaponMods        : list = list()
    weaponModEffects  : list = list()
    weaponModList     : dict = {}
    # weaponArtifacts = ''

    for weapon in weapons:
      weaponDescription  = list()
      weaponSDescription = list()
      weaponMods         = list()
      # weaponArtifacts = ''
      
      if ('mods' in weapon):
        weaponModEffects.append('{', f'"RL{weapon["name"]}", "{weapon["mods"]["bulk"]}", "{weapon["mods"]["power"]}", "{weapon["mods"]["agility"]}", "{weapon["mods"]["technical"]}", "{weapon["mods"]["sniper"]}", "{weapon["mods"]["firestorm"]}", "{weapon["mods"]["nano"]}"', '},')
        weaponModMax     += 1

        modsLen = len(weapon['mods'])
        for i, modsFragment in enumerate(weapon['mods']):
          modsFragment = modsFragment.replace('\n', '/n')
          weaponMods.append(f'"{weapon['mods'][modsFragment]}{self.separatorToken}"')

          if (i < modsLen - 1):
            weaponMods.append(f'\n')

        weapon['actualMods'] = ''.join(weaponMods)

      if ('corruptions' in weapon):
        demonicArtifacts.append('{', f'"RL{weapon["name"]}", "{weapon["corruptions"][0]}", "{weapon["corruptions"][1]}", "{weapon["corruptions"][2]}"', '},')
        demonicWeapons   += 1

        # artifactsLen = len(weapon['corruptions'])
        # for i, artifactsFragment in enumerate(weapon['corruptions']):
        #   artifactsFragment = artifactsFragment.replace('\n', '/n')
        #   weaponArtifacts += f'"{artifactsFragment}|"'

        #   if i < artifactsLen - 1:
        #     weaponArtifacts += f'\n'

        # weapon['actualArtifacts'] = weaponArtifacts
      
      if ('tier' in weapon):
        match weapon['tier']:
          case 'Basic':    basicModMax    += 1
          case 'Advanced': advancedModMax += 1
          case 'Master':   masterModMax   += 1
          case _: pass
      
      if ('description' in weapon):
        descLen = len(weapon['description'])
        for i, descFragment in enumerate(weapon['description']):
          descFragment       = descFragment.replace('\n', '/n')
          weaponDescription.append(f'"{descFragment}"')

          if (i < descLen - 1):
            weaponDescription.append(f'\n')

        weapon['actualDescription'] = ''.join(weaponDescription)
      
      if ('specialdesc' in weapon):
        descLen = len(weapon['specialdesc'])
        
        for i, descFragment in enumerate(weapon['specialdesc']):
          descFragment        = descFragment.replace('\n', '/n')
          weaponSDescription.append(f'"{descFragment}"')

          if i < descLen - 1:
            weaponSDescription.append(f'\n')

        weapon['actualSpecialDesc'] = ''.join(weaponSDescription)

      weapon['flatname'] = Arsenal.handleColors(self, self.filler, weapon['prettyname'], 'strip')
      weaponLanguage.append(Arsenal.LANGUAGE_WEAPONS(self, weapon))
      weaponLanguage.append('\n')

      
    weaponModList['max']         = weaponModMax
    weaponModList['dmax']        = demonicWeapons
    weaponModList['basicmax']    = basicModMax
    weaponModList['advancedmax'] = advancedModMax
    weaponModList['mastermax']   = masterModMax
    weaponModList['list']        = ''.join(weaponModEffects)
    weaponModList['dlist']       = ''.join(demonicArtifacts)
  
    # Arsenal.doOutput(self, 'modeffects.idb')
    # modEffectsDB = Arsenal.PDA_MOD(self, weaponModList)
    # modEffectsDB = modEffectsDB.replace("'", '"')

    # if (self.outputData):
    #   with open(self.outputData.name, mode='w', encoding='utf-8') as file:
    #     file.write(modEffectsDB)

    # self.printLine('[%s] Created modeffects array list as modeffects.idb\n' % currentTime())

    tempString: str = ''.join(weaponLanguage)
    tempString = Arsenal.handleColors(self, self.filler, tempString, 'revert')

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
      
      if (self.outputData):
        with open(self.outputData.name, mode='w', encoding='utf-8') as file:
          file.write(languageWeaponOutput)
    
      self.printLine('[%s] Ending weapons processing. Created language.auto.weapons\n' % currentTime())
    else: 
      self.printLine('[%s] Ending weapons processing.\n' % currentTime())
      self.printLine('[%s] %s.\n' % (currentTime(), languageWeaponOutput))
    
  def processEquipment(self, equipment, doOutput):
    if (not equipment): return 0
    self.printLine('[%s] Reading EQUIPMENT...\n' % currentTime())

    # headerArmorList  : str = ''
    # languageArmorList: str = ''
    equipmentMax     : int = 0
    # equipDescription : str = ''
    languageArmorList: list = list()
    headerArmorList  : list = list()
    equipDescription : list = list()
    

    for equip in equipment:
      equipDescription = ''
      headerArmorList.append('{', f'"RL{equip['name']}", "{equip['name'].upper()}"', '},')
      # headerArmorList += '{'
      # headerArmorList += f'''"RL{equip['name']}", "{equip['name'].upper()}"'''
      # headerArmorList += '},'
      equipmentMax    += 1

      if ('description' in equip):
        for descFragment in equip['description']:
          descFragment = descFragment.replace('\n', '/n')
          equipDescription.append(f'"{descFragment}"\n')
          # equipDescription += f'"{descFragment}"\n'
          
        equip['actualDescription'] = ''.join(equipDescription)

      languageArmorList.append(Arsenal.LANGUAGE_EQUIPMENT(self, equip))
      languageArmorList.append('\n')

    equipmentList: dict   = {}
    equipmentList['max']  = equipmentMax
    equipmentList['list'] = ''.join(headerArmorList)

    arsenalDB = Arsenal.PDA_ARM(self, equipmentList)
    arsenalDB = arsenalDB.replace("'", '"')

    tempString: str = ''.join(languageArmorList)
    
    if (doOutput):
      Arsenal.doOutput(self, 'equipment.idb')
      if (self.outputData):
        with open(self.outputData.name, mode='w', encoding='utf-8') as file:
          file.write(arsenalDB)

      self.printLine('[%s] Created ACS array list for EQUIPMENT as equipment.idb\n' % currentTime())
    else: 
      self.printLine('[%s] Created ACS array list for EQUIPMENT\n' % currentTime())
      self.printLine('[%s] %s\n' % (currentTime(), arsenalDB))

    for i in self.filler:
      if ('attributes' in i):
        attributes = self.filler[i].items()
        
        for attributeKey, attributeValue in attributes:
          tempString = tempString.replace(attributeKey, attributeValue)

    self.printLine('[%s] Keywords translated into attributes\n' % currentTime())

    tempString = re.sub('/(\n)/g', '\\n', tempString)
    tempString = re.sub('/(;)\\n/gm', ';', tempString)
    tempString = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', '', tempString)
    
    tempString = tempString.replace('/n', '\\n')
    
    tempString = Arsenal.handleColors(self, self.filler, tempString, 'revert')

    languageArmorOutput = Arsenal.language_warning + tempString
    
    if (doOutput):
      Arsenal.doOutput(self, 'language.auto.equipment')
      
      if (self.outputData):
        with open(self.outputData.name, mode='w', encoding='utf-8') as file:
          file.write(languageArmorOutput)
          
      self.printLine('[%s] Done with processing equipment. Generated language.auto.equipment\n' % currentTime())
    else:
      self.printLine('[%s] Done with processing equipment.\n' % currentTime())
      self.printLine('[%s] %s.\n' % (currentTime(), languageArmorOutput))

        
  def processModEffect(self, mods, doOutput):
    if (not mods): return 0

    # modEffectList = ''
    modEffectList: list = list()
    for mod in mods:
      modEffectListLen: int = len(mod['effect'])
        
      if (type(mod['effect']) == str) :
        # modEffectList += f'''{mod['name']} = "{mod['effect']}";'''
        modEffectList.append(f'''{mod['name']} = "{mod['effect']}";''')
        
      if (type(mod['effect']) == list or type(mod['effect']) == dict) :
        # modEffectList += f'''{mod['name']} = '''
        modEffectList.append(f'''{mod['name']} = ''')
        
        for i, modEffectFragment in enumerate(mod['effect']):
          # modEffectList += f'"{modEffectFragment}"'
          modEffectFragment = modEffectFragment.replace('\n', '/n')
          modEffectList.append(f'"{modEffectFragment}"')

          if i < modEffectListLen - 1:
            # modEffectList += f'\n'
            modEffectList.append(f'\n')
            
        # modEffectList += f';'
        modEffectList.append(f';')
        
      # modEffectList += '\n'
      modEffectList.append('\n')

    # modEffectList = Arsenal.handleColors(self, self.filler, ''.join(modEffectList), 'revert')
    # languageModOutput = Arsenal.language_warning + modEffectList
    
    tempString: str = ''.join(modEffectList)
    tempString = Arsenal.handleColors(self, self.filler, tempString, 'revert')
    
    languageModOutput = Arsenal.language_warning + tempString
    
    self.printLine('[%s] Done parsing mod effects DB.\n' % currentTime())

    if (doOutput):
      Arsenal.doOutput(self, 'language.auto.mods')
      if (self.outputData):
        with open(self.outputData.name, mode='w', encoding='utf-8') as file:
          file.write(languageModOutput)
      self.printLine('[%s] Created language.auto.mods\n' % currentTime())
    else: 
      self.printLine('[%s] \n'  % currentTime())
      self.printLine('[%s] %s.\n' % (currentTime(), languageModOutput))

        
  def processAssemblies(self, data, doOutput):
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
    assemblyDescription : list = list()
    headerAssemblyList  : list = list()
    languageAssemblyList: list = list()
    headerExoticList    : list = list()

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
      
      headerAssemblyList.append('{', f'''"RL{assembly['name']}AssemblyLearntToken", "PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}"''', '},')
      headerAssemblyMax += 1

      match assembly['tier']:
        case 'Basic':    basicMax    += 1
        case 'Advanced': advancedMax += 1
        case 'Master':   masterMax   += 1
        case _: pass

      if ('description' in assembly):
        descLen = len(assembly['description'])
        
        for i, descFragment in enumerate(assembly['description']):
          descFragment = descFragment.replace('\n', '/n')
          
          if i < descLen - 1:
            assemblyDescription.append(f'"{descFragment}"\n')
          else:
            assemblyDescription.append(f'"{descFragment}"')
            
        assembly['actualDescription'] = ''.join(assemblyDescription)

      languageAssemblyList.append(Arsenal.LANGUAGE_ASSEMBLIES(self, assembly))
      languageAssemblyList.append('\n')

    tempString: str = ''.join(languageAssemblyList)
    
    tempString = re.sub('/(\n)/g', '\\n', tempString)
    tempString = re.sub('/(;)\\n/gm', ';', tempString)
    tempString = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', '', tempString)
    
    tempString = tempString.replace('/n', '\\n')
    
    tempString = Arsenal.handleColors(self, self.filler, tempString, 'revert')
  
    for weapon in data['weapons']:
      if (weapon['tier'] == 'Unique' or weapon['tier'] == 'Demonic' or weapon['tier'] == 'Legendary'):
        if ('unmoddable' in weapon):
          headerExoticList.append('{', f'''"RL{weapon['name']}", "null", "null", "null"''', '},')
        else:
          headerExoticList.append('{', f'''"RL{weapon['name']}", "RL{weapon['name']}SniperLearntToken", "RL{weapon['name']}FirestormLearntToken", "RL{weapon['name']}NanoLearntToken"''', '},')
          
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
      
      if (self.outputData):
        with open(self.outputData.name, mode='w', encoding='utf-8') as file:
          file.write(languageAssemblyOutput)

      self.printLine('[%s] Created language.auto.assemblies\n' % currentTime())
    else:
      self.printLine('[%s] Created nothing\n' % currentTime())
      self.printLine('[%s] %s.\n' % (currentTime(), languageAssemblyOutput))

    assemblyList: dict          = {}
    
    assemblyList['list']        = ''.join(headerAssemblyList)
    assemblyList['exotics']     = ''.join(headerExoticList)
    
    assemblyList['max']         = headerAssemblyMax
    assemblyList['uniquemax']   = headerUniqueMax
    assemblyList['basicmax']    = basicMax
    assemblyList['advancedmax'] = advancedMax
    assemblyList['mastermax']   = masterMax
    

    self.printLine('[%s] Finished compilation\n' % currentTime())

    # assembliesDB = Arsenal.PDA_ASM(self, assemblyList)
    # assembliesDB = assembliesDB.replace("'", '"')
    # if (doOutput):
    #   Arsenal.doOutput(self, 'assemblies.idb')
    #   if (self.outputData):
    #     with open(self.outputData.name, mode='w', encoding='utf-8') as file:
    #       file.write(assembliesDB)
    #   self.printLine('[%s] Created assemblies.idb\n' % currentTime())
    # else: 
    #   self.printLine('[%s] Created nothing\n' % currentTime())
    #   self.printLine('[%s] %s\n' % (currentTime(), assembliesDB))


  def PDA_MOD(self, weapons):
    construct = f'''#library "PDA_MOD"

// These, however, are deprecated.
/*
#define DRLA_WEAPONMAX {weapons['max']}
#define DRLA_DEMONWEAPONMAX {weapons['dmax']}
#define DRLA_BASICMODMAX {weapons['basicmax']}
#define DRLA_ADVANCEDMODMAX {weapons['advancedmax']}
#define DRLA_MASTERMODMAX {weapons['mastermax']}
#define DRLA_WEAPONMODELEMENTS 8
#define DRLA_DEMONWEAPONELEMENTS 4

str DRLA_WeaponModList[DRLA_WEAPONMAX][DRLA_WEAPONMODELEMENTS] = {{{weapons['list']}}};

str DRLA_ArtifactEffectList[DRLA_DEMONWEAPONMAX][DRLA_DEMONWEAPONELEMENTS] = {{{weapons['dlist']}}};
*/
    '''

    return construct

  def PDA_ARM(self, equipment):
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

  def PDA_ASM(self, assemblies):
    construct = f'''#library "PDA_ASM"

#define DRLA_ASSEMBLYMAX {assemblies['max']}
#define DRLA_ASSEMBLYELEMENTS 2
#define DRLA_EXOTICEFFECTS_MAX {assemblies['uniquemax']}
#define DRLA_EXOTICELEMENTS 4
#define DRLA_BASICMAX {assemblies['basicmax']}
#define DRLA_ADVANCEDMAX {assemblies['advancedmax']}
#define DRLA_MASTERMAX {assemblies['mastermax']}

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
str     DRLA_CurrentAssemblerState[MAX_PLAYERS] = {{"","","","","","","",""}};

str     DRLA_CurrentExoticModInfo[MAX_PLAYERS];

str     DRLA_CurrentSniperState[MAX_PLAYERS]    = {{"","","","","","","",""}},
        DRLA_CurrentFirestormState[MAX_PLAYERS] = {{"","","","","","","",""}},
        DRLA_CurrentNanoState[MAX_PLAYERS]      = {{"","","","","","","",""}};

str DRLA_Assemblies[DRLA_ASSEMBLYMAX][DRLA_ASSEMBLYELEMENTS] = {{{assemblies['list']}}};

str DRLA_UniqueExoticModEffects[DRLA_EXOTICEFFECTS_MAX][DRLA_EXOTICELEMENTS] = {{{assemblies['exotics']}}};'''

    return construct

  def LANGUAGE_WEAPONS(self, weapon):
    if ('name' not in weapon):
      return ''

    bigname = weapon['name'].upper()

    # fragment = f'''PDA_WEAPON_{bigname}_ACTOR = "RL{bigname}";\n'''
    fragment: list = list(f'''PDA_WEAPON_{bigname}_ACTOR = "RL{bigname}";\n''')

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

  def resPadder(str, len):
    return str.rjust(len, ' ')

  def LANGUAGE_EQUIPMENT(self, equipment: any): 
    if (not self.filler): 
      print("self.filler is empty")
      return 0
    if ('name' not in equipment): 
      print("Name not found in equipment")
      return 0

    bigname         : str = equipment['name'].upper()
    coloredequipment: str = equipment['prettyname']
    flatequipment   : str = Arsenal.handleColors(self, self.filler, equipment['prettyname'], 'strip')

    atts: list = list()
    for attr in equipment['attributes']:
      atts.append(f'''" {attr}\\n"''')

    for f in self.filler:
      if ('colors' in f):
        colors = self.filler[f].items()
        for colorKey, colorValue in colors:
          if (colorKey.upper() == equipment['tier'].upper()):
            coloredequipment = f'''\\c{colorValue}{equipment['prettyname']}\\c-'''

    construct: list = list(f'''
PDA_ARMOR_{bigname}_ICON = "{equipment['icon']}";
PDA_ARMOR_{bigname}_NAME = "{coloredequipment}";
PDA_ARMOR_{bigname}_FLATNAME = "{flatequipment}";
PDA_ARMOR_{bigname}_DESC = {equipment['actualDescription']};
PDA_ARMOR_{bigname}_PROT = "{Arsenal.resPadder(' ', 4 - len(equipment['protection']))}{equipment['protection']}% [GOLD]Protection[END]";
PDA_ARMOR_{bigname}_RENPROT = "{Arsenal.resPadder(' ', 4 - len(equipment['renprotection']))}{equipment['renprotection']}% [GOLD]Protection[END]";''')

    if 'resistances' in equipment:
      res: dict = equipment['resistances']
      construct.append(f'''
PDA_ARMOR_{bigname}_RES = 
  "{Arsenal.resPadder(' ', 4 - len(res['melee']))}{res['melee']}% [DARKGRAY]Melee[END]  "
  "{Arsenal.resPadder(' ', 4 - len(res['bullet']))}{res['bullet']}% [GRAY]Bullet[END] \\n"
  "{Arsenal.resPadder(' ', 4 - len(res['fire']))}{res['fire']}% [RED]Fire[END]   "
  "{Arsenal.resPadder(' ', 4 - len(res['cryo']))}{res['cryo']}% [CYAN]Cryo[END]   \\n"
  "{Arsenal.resPadder(' ', 4 - len(res['plasma']))}{res['plasma']}% [BLUE]Plasma[END] "
  "{Arsenal.resPadder(' ', 4 - len(res['electric']))}{res['electric']}% [YELLOW]Electric[END]\\n"
  "{Arsenal.resPadder(' ', 4 - len(res['poison']))}{res['poison']}% [PURPLE]Poison[END] "
  "{Arsenal.resPadder(' ', 4 - len(res['radiation']))}{res['radiation']}% [GREEN]Radiation[END]\\n";''')
      construct.append('\n')
    
    if 'cyborgstats' in equipment:
      cybres: dict = equipment['cyborgstats']['resistances']
      construct.append(f'''PDA_ARMOR_{bigname}_CYBRES =''')
      if 'kinetic' in cybres:   construct.append(f'''"{Arsenal.resPadder(' ', 4 - len(cybres['kinetic']))}{cybres['kinetic']}% [WHITE]Kinetic Plating[END]\\n"''')
      if 'thermal' in cybres:   construct.append(f'''"{Arsenal.resPadder(' ', 4 - len(cybres['thermal']))}{cybres['thermal']}% [RED]Thermal Dampeners[END]\\n"''')
      if 'refractor' in cybres: construct.append(f'''"{Arsenal.resPadder(' ', 4 - len(cybres['refractor']))}{cybres['refractor']}% [BLUE]Refractor Field[END]\\n"''')
      if 'organic' in cybres:   construct.append(f'''"{Arsenal.resPadder(' ', 4 - len(cybres['organic']))}{cybres['organic']}% [GREEN]Organic Recovery[END]\\n"''')
      construct.append(f'''"{Arsenal.resPadder(' ', 4 - len(cybres['hazard']))}{cybres['hazard']}% [YELLOW]Hazard Shielding[END]\\n";''')

    construct.append(f'''
PDA_ARMOR_{bigname}_CYBAUG = "{equipment['cyborgstats']['augment']}";
PDA_ARMOR_{bigname}_ATTR = {''.join(atts)};
    ''')

    return ''.join(construct)

    
  def LANGUAGE_ASSEMBLIES(self, assembly: dict):
    if (not self.filler): return 0
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
      for f in self.filler:
        if ('colors' in f):
          colors = self.filler[f].items()
          
          for colorKey, colorValue in colors:
            if (colorKey.upper() == mod):
              mods.append(f'''\\c{colorValue}{mod[0]}\\c-''')

    for f in self.filler:
      if ('colors' in f):
        colors = self.filler[f].items()
        
        for colorKey, colorValue in colors:
          if (colorKey.upper() == assembly['tier'].upper()):
            coloredname = f'''\\c{colorValue}{assembly['prettyname']}\\c-'''

    descLen = len(assembly['valid'])
    
    for i, validassemblies in enumerate(assembly['valid']):
      validassemblies = validassemblies.replace('\n', '/n')
      
      if i < descLen - 1:
        valid.append(f'''"{validassemblies}"\n''')
      else:
        valid.append(f'''"{validassemblies}"''')

    descLen = len(assembly['validlist'])
    for i, validweapon in enumerate(assembly['validlist']):
      validweapon = validweapon.replace('\n', '/n')
      
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
  # };