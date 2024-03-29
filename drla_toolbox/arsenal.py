import os.path
import sys
import customtkinter
import json
import re
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from datetime import datetime

# TODO: Examine memory footprint of all loaded JSON modules (currently around 555KB worth of JSON)
# TODO: Optimize loading
# TODO: Perhaps there's a better way to parse and compile all this data instead of smashing it all in memory?

class Arsenal:
  outputData = ''
  language_warning = '[enu default]\n\n// Please do not modify this file directly, it\'s specifically compiled and any changes may be lost.\n\n'

  def arsenal_doInput(self):
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
      self.printLine('[%s] Files selected: %s\n' % (datetime.now().strftime("%H:%M:%S"), list(self.inputFiles)))
      # self.printLine('[%s] File selected: %s\n' % (datetime.now().strftime("%H:%M:%S"), os.path.normpath(self.inputFile)))
      self.filler = {}
      loadedFiles = ''
      for _, file in enumerate(self.inputFiles):
        self.printLine('[%s] Loaded JSON into filler memory: %s\n' % (datetime.now().strftime("%H:%M:%S"), file))
        loadedFiles += os.path.basename(file) + '\n'

        if ('data.json' in file):
          with open(os.path.normpath(file), mode='r', encoding='utf-8') as freshdata:
            self.filler = json.load(freshdata)
            
        if file:
          with open(os.path.normpath(file), mode='r', encoding='utf-8') as jsonBuffer:
            self.loadedJson.update(json.load(jsonBuffer))
      self.selected_files.configure(text=loadedFiles)
    else:
      self.printLine('[%s] No JSON files selected\n' % datetime.now().strftime("%H:%M:%S"))

  def arsenal_doCompile(self):
    if ('weapons' in self.loadedJson): Arsenal.arsenal_processWeapons(self, self.loadedJson['weapons'])
    if ('equipment' in self.loadedJson): Arsenal.arsenal_processEquipment(self, self.loadedJson['equipment'])
    if ('modeffect' in self.loadedJson): Arsenal.arsenal_processModEffect(self, self.loadedJson['modeffect'])
    if ('assemblies' in self.loadedJson): Arsenal.arsenal_processAssemblies(self, self.loadedJson)

  def arsenal_doOutput(self, name):
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
      self.printLine('[%s] No file chosen\n' % datetime.now().strftime("%H:%M:%S"))
      self.compileArsenal.configure(state='disabled')
      return 0

  def arsenal_revertColors(self, dict, str):
    if (not str or len(dict) < 1): 
      self.printLine('[%s] No data found to process\n' % datetime.now().strftime("%H:%M:%S"))
      return 'false'

    noColors = 1
    
    for i in dict:
      if ('colors' in i):
        noColors = 0

    if (noColors): 
      self.printLine('[%s] No such property: colors\n' % datetime.now().strftime("%H:%M:%S"))
      return 'false'

    for i in dict:
      if ('colors' in i):
        colors = dict[i].items()
        for colorKey, colorValue in colors:
          str = str.replace('['+colorKey+']', '\c'+colorValue)

    return str

  def arsenal_processWeapons(self, weapons):
    if (not weapons): return 0
    self.printLine('[%s] Parsing WEAPONS database\n' % datetime.now().strftime("%H:%M:%S"))
    
    weaponModEffects = ''
    weaponModMax = 0
    demonicWeapons = 0
    demonicArtifacts = ''
    weaponLanguage = ''
    basicModMax = 0
    advancedModMax = 0
    masterModMax = 0
    weaponDescription = ''
    weaponSDescription = ''
    weaponModList = {}

    for weapon in weapons:
      weaponDescription = ''
      weaponSDescription = ''
      if ('mods' in weapon):
        weaponModEffects += '{'
        weaponModEffects += f'"RL{weapon["name"]}", "{weapon["mods"]["bulk"]}", "{weapon["mods"]["power"]}", "{weapon["mods"]["agility"]}", "{weapon["mods"]["technical"]}", "{weapon["mods"]["sniper"]}", "{weapon["mods"]["firestorm"]}", "{weapon["mods"]["nano"]}"'
        weaponModEffects += '},'
        weaponModMax+=1

      if ('corruptions' in weapon):
        demonicArtifacts += '{'
        demonicArtifacts += f'"RL{weapon["name"]}", "{weapon["corruptions"][0]}", "{weapon["corruptions"][1]}", "{weapon["corruptions"][2]}"'
        demonicArtifacts += '},'
        demonicWeapons+=1
      
      if ('tier' in weapon):
        if (weapon['tier'] == 'Basic'):
          basicModMax+=1
        
        if (weapon['tier'] == 'Advanced'):
          advancedModMax+=1
        
        if (weapon['tier'] == 'Master'):
          masterModMax+=1
      
      if ('description' in weapon):
        descLen = len(weapon['description'])
        for i, descFragment in enumerate(weapon['description']):
          descFragment = descFragment.replace('\n', '/n')
          if i < descLen - 1:
            weaponDescription += f'"{descFragment}"\n'
          else:
            weaponDescription += f'"{descFragment}"'
        weapon['actualDescription'] = weaponDescription
      
      if ('specialdesc' in weapon):
        descLen = len(weapon['specialdesc'])
        for i, descFragment in enumerate(weapon['specialdesc']):
          descFragment = descFragment.replace('\n', '/n')
          if i < descLen - 1:
            weaponSDescription += f'"{descFragment}"\n'
          else:
            weaponSDescription += f'"{descFragment}"'
        weapon['actualSpecialDesc'] = weaponSDescription

      weaponLanguage += Arsenal.LANGUAGE_WEAPONS(self, weapon)
      weaponLanguage += '\n'
      
    weaponModList['max'] = weaponModMax
    weaponModList['list'] = weaponModEffects
    weaponModList['dmax'] = demonicWeapons
    weaponModList['dlist'] = demonicArtifacts
    weaponModList['basicmax'] = basicModMax
    weaponModList['advancedmax'] = advancedModMax
    weaponModList['mastermax'] = masterModMax
  
    Arsenal.arsenal_doOutput(self, 'modeffects.idb')
    modEffectsDB = Arsenal.PDA_MOD(self, weaponModList)
    modEffectsDB = modEffectsDB.replace("'", '"')

    if (self.outputData):
      with open(self.outputData.name, mode='w', encoding='utf-8') as file:
        file.write(modEffectsDB)

    self.printLine('[%s] Created modeffects array list as modeffects.idb\n' % datetime.now().strftime("%H:%M:%S"))

    weaponLanguage = Arsenal.arsenal_revertColors(self, self.filler, weaponLanguage)

    weaponLanguage = weaponLanguage.replace('[INNERQUOTE]', '\\"')
    weaponLanguage = re.sub('/(\n)/g', '\\n', weaponLanguage)
    weaponLanguage = re.sub('/(;)\\n/gm', ';', weaponLanguage)
    weaponLanguage = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', '', weaponLanguage)
    weaponLanguage = re.sub('/( {3,})\\n/gm', '', weaponLanguage)
    weaponLanguage = re.sub('/^\\n( {1,})/gm', '', weaponLanguage)
    weaponLanguage = weaponLanguage.replace('/n', '\\n')

    Arsenal.arsenal_doOutput(self, 'language.auto.weapons')
    languageWeaponOutput = Arsenal.language_warning + weaponLanguage
    if (self.outputData):
      with open(self.outputData.name, mode='w', encoding='utf-8') as file:
        file.write(languageWeaponOutput)
    
    self.printLine('[%s] Ending weapons processing. Created language.auto.weapons\n' % datetime.now().strftime("%H:%M:%S"))

    
  def arsenal_processEquipment(self, equipment):
    if (not equipment): return 0
    self.printLine('[%s] Reading EQUIPMENT...\n' % datetime.now().strftime("%H:%M:%S"))

    headerArmorList = ''
    languageArmorList = ''
    equipmentMax = 0
    equipDescription = ''

    for equip in equipment:
      headerArmorList += '{'
      headerArmorList += f'''"RL{equip['name']}", "{equip['name'].upper()}"'''
      headerArmorList += '},'
      equipmentMax+=1

      if ('description' in equip):
        for descFragment in equip['description']:
          descFragment = descFragment.replace('\n', '/n')
          equipDescription += f'"{descFragment}"\n'
        equip['actualDescription'] = equipDescription

      languageArmorList += Arsenal.LANGUAGE_EQUIPMENT(self, equip)
      languageArmorList += '\n'

    equipmentList = {}
    equipmentList['max'] = equipmentMax
    equipmentList['list'] = headerArmorList

    Arsenal.arsenal_doOutput(self, 'equipment.idb')
    arsenalDB = Arsenal.PDA_ARM(self, equipmentList)
    arsenalDB = arsenalDB.replace("'", '"')

    if (self.outputData):
      with open(self.outputData.name, mode='w', encoding='utf-8') as file:
        file.write(arsenalDB)

    self.printLine('[%s] Created ACS array list for EQUIPMENT as equipment.idb\n' % datetime.now().strftime("%H:%M:%S"))

    for i in self.filler:
      if ('attributes' in i):
        attributes = self.filler[i].items()
        for attributeKey, attributeValue in attributes:
          languageArmorList = languageArmorList.replace(attributeKey, attributeValue)

    self.printLine('[%s] Keywords translated into attributes\n' % datetime.now().strftime("%H:%M:%S"))

    languageArmorList = re.sub('/(\n)/g', '\\n', languageArmorList)
    languageArmorList = re.sub('/(;)\\n/gm', ';', languageArmorList)
    languageArmorList = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', '', languageArmorList)
    languageArmorList = languageArmorList.replace('/n', '\\n')
    languageArmorList = Arsenal.arsenal_revertColors(self, self.filler, languageArmorList)

    Arsenal.arsenal_doOutput(self, 'language.auto.equipment')
    languageArmorOutput = Arsenal.language_warning + languageArmorList
    if (self.outputData):
      with open(self.outputData.name, mode='w', encoding='utf-8') as file:
        file.write(languageArmorOutput)
    self.printLine('[%s] Done with processing equipment. Generated language.auto.equipment\n' % datetime.now().strftime("%H:%M:%S"))

        
  def arsenal_processModEffect(self, mods):
    if (not mods): return 0

    modEffectList = ''
    for mod in mods:
      modEffectList += f'''{mod['name']} = "{mod['effect']}";'''
      modEffectList += '\n'

    modEffectList = Arsenal.arsenal_revertColors(self, self.filler, modEffectList)

    languageModOutput = Arsenal.language_warning + modEffectList
    
    self.printLine('[%s] Done pasing mod effects DB.\n' % datetime.now().strftime("%H:%M:%S"))

    Arsenal.arsenal_doOutput(self, 'language.auto.mods')
    if (self.outputData):
      with open(self.outputData.name, mode='w', encoding='utf-8') as file:
        file.write(languageModOutput)
    self.printLine('[%s] Created language.auto.mods\n' % datetime.now().strftime("%H:%M:%S"))

        
  def arsenal_processAssemblies(self, data):
    if (not data): return 0

    headerAssemblyList = ''
    headerAssemblyMax = 0
    headerUniqueMax = 0
    headerExoticList = ''
    languageAssemblyList = ''
    basicMax = 0
    advancedMax = 0
    masterMax = 0
    assemblyDescription = ''

    for assembly in data['assemblies']:
      assemblyDescription = ''
      headerAssemblyList += '{'
      headerAssemblyList += f'''"RL{assembly['name']}AssemblyLearntToken", "PDA_ASSEMBLY_{assembly['tier'].upper()}_{assembly['name'].upper()}"'''
      headerAssemblyList += '},'
      headerAssemblyMax+=1

      if (assembly['tier'] == 'Basic'): basicMax+=1
      if (assembly['tier'] == 'Advanced'): advancedMax+=1
      if (assembly['tier'] == 'Master'): masterMax+=1

      if ('description' in assembly):
        descLen = len(assembly['description'])
        for i, descFragment in enumerate(assembly['description']):
          descFragment = descFragment.replace('\n', '/n')
          if i < descLen - 1:
            assemblyDescription += f'"{descFragment}"\n'
          else:
            assemblyDescription += f'"{descFragment}"'
        assembly['actualDescription'] = assemblyDescription

      languageAssemblyList += Arsenal.LANGUAGE_ASSEMBLIES(self, assembly)
      languageAssemblyList += '\n'

    languageAssemblyList = re.sub('/(\n)/g', '\\n', languageAssemblyList)
    languageAssemblyList = re.sub('/(;)\\n/gm', ';', languageAssemblyList)
    languageAssemblyList = re.sub('/\\n(?=(?:[^"]*"[^"]*")*[^"]*$)/gm', '', languageAssemblyList)
    languageAssemblyList = languageAssemblyList.replace('/n', '\\n')
    languageAssemblyList = Arsenal.arsenal_revertColors(self, self.filler, languageAssemblyList)

    languageAssemblyOutput = Arsenal.language_warning + languageAssemblyList
    Arsenal.arsenal_doOutput(self, 'language.auto.assemblies')
    if (self.outputData):
      with open(self.outputData.name, mode='w', encoding='utf-8') as file:
        file.write(languageAssemblyOutput)

    self.printLine('[%s] Created language.auto.assemblies\n' % datetime.now().strftime("%H:%M:%S"))
  
    for weapon in data['weapons']:
      if (weapon['tier'] == 'Unique' or weapon['tier'] == 'Demonic' or weapon['tier'] == 'Legendary'):
        if ('unmoddable' in weapon):
          headerExoticList += '{'
          headerExoticList += f'''"RL{weapon['name']}", "null", "null", "null"'''
          headerExoticList += '},'
        else:
          headerExoticList += '{'
          headerExoticList += f'''"RL{weapon['name']}", "RL{weapon['name']}SniperLearntToken", "RL{weapon['name']}FirestormLearntToken", "RL{weapon['name']}NanoLearntToken"'''
          headerExoticList += '},'
        headerUniqueMax+=1

    assemblyList = {}
    assemblyList['max'] = headerAssemblyMax
    assemblyList['list'] = headerAssemblyList
    assemblyList['uniquemax'] = headerUniqueMax
    assemblyList['basicmax'] = basicMax
    assemblyList['advancedmax'] = advancedMax
    assemblyList['mastermax'] = masterMax
    assemblyList['exotics'] = headerExoticList

    assembliesDB = Arsenal.PDA_ASM(self, assemblyList)
    assembliesDB = assembliesDB.replace("'", '"')
    Arsenal.arsenal_doOutput(self, 'assemblies.idb')
    if (self.outputData):
      with open(self.outputData.name, mode='w', encoding='utf-8') as file:
        file.write(assembliesDB)
    self.printLine('[%s] Created assemblies.idb\n' % datetime.now().strftime("%H:%M:%S"))


  def PDA_MOD(self, weapons):
    construct = f'''#library "PDA_MOD"

#define DRLA_WEAPONMAX {weapons['max']}
#define DRLA_DEMONWEAPONMAX {weapons['dmax']}
#define DRLA_BASICMODMAX {weapons['basicmax']}
#define DRLA_ADVANCEDMODMAX {weapons['advancedmax']}
#define DRLA_MASTERMODMAX {weapons['mastermax']}
#define DRLA_WEAPONMODELEMENTS 8
#define DRLA_DEMONWEAPONELEMENTS 4

str DRLA_WeaponModList[DRLA_WEAPONMAX][DRLA_WEAPONMODELEMENTS] = {{{weapons['list']}}};

str DRLA_ArtifactEffectList[DRLA_DEMONWEAPONMAX][DRLA_DEMONWEAPONELEMENTS] = {{{weapons['dlist']}}};
    '''

    return construct

  def PDA_ARM(self, equipment):
    construct = f'''#library "PDA_ARM"
    
#define DRLA_ARMORMAX {equipment['max']}
#define DRLA_ARMORELEMENTS 2
#define DRLA_ARMORSETMAX 18

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

    if ('prettyname' in weapon): 
      fragment = f'''PDA_WEAPON_{bigname}_NAME = "{weapon['prettyname']}";\n'''
    if ('actualDescription' in weapon): 
      fragment += f'''PDA_WEAPON_{bigname}_DESC = {weapon['actualDescription']};\n'''
    if ('specialpretty' in weapon): 
      fragment += f'''PDA_WEAPON_{bigname}DEMONARTIFACTS_NAME = "{weapon['specialpretty']}";\n'''
    if ('specialdesc' in weapon): 
      fragment += f'''PDA_WEAPON_{bigname}DEMONARTIFACTS_DESC = {weapon['actualSpecialDesc']};\n'''

    return fragment

  def resPadder(str, len):
    return str.rjust(len, ' ')

  def LANGUAGE_EQUIPMENT(self, equipment): 
    if (not self.filler): 
      print("self.filler is empty")
      return 0
    if ('name' not in equipment): 
      print("Name not found in equipment")
      return 0

    bigname = equipment['name'].upper()
    coloredequipment = equipment['prettyname']

    atts = ''
    for attr in equipment['attributes']:
      atts += f'''" {attr}\\n"'''

    for f in self.filler:
      if ('colors' in f):
        colors = self.filler[f].items()
        for colorKey, colorValue in colors:
          if (colorKey.upper() == equipment['tier'].upper()):
            coloredequipment = f'''\\c{colorValue}{equipment['prettyname']}\\c-'''

    construct = f'''
PDA_ARMOR_{bigname}_ICON = "{equipment['icon']}";
PDA_ARMOR_{bigname}_NAME = "{coloredequipment}";
PDA_ARMOR_{bigname}_DESC = {equipment['actualDescription']};
PDA_ARMOR_{bigname}_PROT = "{Arsenal.resPadder(' ', 4 - len(equipment['protection']))}{equipment['protection']}% [GOLD]Protection[END]";
PDA_ARMOR_{bigname}_RENPROT = "{Arsenal.resPadder(' ', 4 - len(equipment['renprotection']))}{equipment['renprotection']}% [GOLD]Protection[END]";'''

    if 'resistances' in equipment:
      res = equipment['resistances']
      construct += f'''
PDA_ARMOR_{bigname}_RES = 
  "{Arsenal.resPadder(' ', 4 - len(res['melee']))}{res['melee']}% [DARKGRAY]Melee[END]  "
  "{Arsenal.resPadder(' ', 4 - len(res['bullet']))}{res['bullet']}% [GRAY]Bullet[END] \\n"
  "{Arsenal.resPadder(' ', 4 - len(res['fire']))}{res['fire']}% [RED]Fire[END]   "
  "{Arsenal.resPadder(' ', 4 - len(res['cryo']))}{res['cryo']}% [CYAN]Cryo[END]   \\n"
  "{Arsenal.resPadder(' ', 4 - len(res['plasma']))}{res['plasma']}% [BLUE]Plasma[END] "
  "{Arsenal.resPadder(' ', 4 - len(res['electric']))}{res['electric']}% [YELLOW]Electric[END]\\n"
  "{Arsenal.resPadder(' ', 4 - len(res['poison']))}{res['poison']}% [PURPLE]Poison[END] "
  "{Arsenal.resPadder(' ', 4 - len(res['radiation']))}{res['radiation']}% [GREEN]Radiation[END]\\n";'''
      construct += '\n'
    
    if 'cyborgstats' in equipment:
      cybres = equipment['cyborgstats']['resistances']
      construct += f'''PDA_ARMOR_{bigname}_CYBRES ='''
      if 'kinetic' in cybres:   construct += f'''"{Arsenal.resPadder(' ', 4 - len(cybres['kinetic']))}{cybres['kinetic']}% [WHITE]Kinetic Plating[END]\\n"'''
      if 'thermal' in cybres:   construct += f'''"{Arsenal.resPadder(' ', 4 - len(cybres['thermal']))}{cybres['thermal']}% [RED]Thermal Dampeners[END]\\n"'''
      if 'refractor' in cybres: construct += f'''"{Arsenal.resPadder(' ', 4 - len(cybres['refractor']))}{cybres['refractor']}% [BLUE]Refractor Field[END]\\n"'''
      if 'organic' in cybres:   construct += f'''"{Arsenal.resPadder(' ', 4 - len(cybres['organic']))}{cybres['organic']}% [GREEN]Organic Recovery[END]\\n"'''
      construct += f'''"{Arsenal.resPadder(' ', 4 - len(cybres['hazard']))}{cybres['hazard']}% [YELLOW]Hazard Shielding[END]\\n";'''

    construct += f'''
PDA_ARMOR_{bigname}_CYBAUG = "{equipment['cyborgstats']['augment']}";
PDA_ARMOR_{bigname}_ATTR = {atts};
    '''

    return construct

    
  def LANGUAGE_ASSEMBLIES(self, assembly):
    if (not self.filler): return 0
    if ('name' not in assembly):
      print('Name not found in assembly data')
      return ''

    bigname = assembly['name'].upper()
    bigtier = assembly['tier'].upper()
    coloredname = ''

    mods = ''
    valid = ''
    validlist = ''

    for mod in assembly['mods']:
      for f in self.filler:
        if ('colors' in f):
          colors = self.filler[f].items()
          for colorKey, colorValue in colors:
            if (colorKey.upper() == mod):
              mods += f'''\\c{colorValue}{mod[0]}\\c-'''

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
        valid += f'''"{validassemblies}"\n'''
      else:
        valid += f'''"{validassemblies}"'''

    descLen = len(assembly['validlist'])
    for i, validweapon in enumerate(assembly['validlist']):
      validweapon = validweapon.replace('\n', '/n')
      if i < descLen - 1:
        validlist += f'''"{validweapon}"\n'''
      else:
        validlist += f'''"{validweapon}"'''

    valid = valid.replace('->', '[YELLOW]->[END]')

    return f'''
PDA_ASSEMBLY_{bigtier}_{bigname} = "{assembly['prettyname']} [GRAY][[END]{mods}[GRAY]][END]";
PDA_ASSEMBLY_{bigtier}_{bigname}_NAME = "{coloredname}";
PDA_ASSEMBLY_{bigtier}_{bigname}_MODS = "[GRAY][[END]{mods}[GRAY]][END]";
PDA_ASSEMBLY_{bigtier}_{bigname}_ICON = "{assembly['icon']}";
PDA_ASSEMBLY_{bigtier}_{bigname}_HEIGHT = "0";
PDA_ASSEMBLY_{bigtier}_{bigname}_DESC = {assembly['actualDescription']}"[GREEN]Valid Weapons:[END]/n"\n{valid};
PDA_ASSEMBLY_{bigtier}_{bigname}_REQ = {validlist};
    '''
  # };