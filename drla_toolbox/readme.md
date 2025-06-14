# DoomRL Arsenal Toolbox

## PDA Helper
To use the PDA helper, click `Open JSON Files` and then select every `.json` file that
comes packaged. Currently, these are:
* armors
* assemblies
* data
* items
* mods
* weapons 

These can be selected all at once via clicking and dragging, or via clicking one file, 
holding the SHIFT key, and then selecting the last file.

The `Build (No output)` button goes through the compilation process, but does 
not export the output into a separate series of files.

The `Compile` button goes through the compilation process, but asks the user to 
define the folder and file they will be exporting to. 
The default naming scheme for the exported files are: 
* `language.auto.[assemblies/equipment/mods/weapons]`
* `equipment.idb`

## SBARINFO

The `#MERGE` command inside the skeleton files currently expects the file-to-include
to be within the same folder as the skeleton.

Make sure you have an appropriate condition surrounding either the merge command, or 
within the separated `statusbar_` or `fullscreen_` file


Afterwards, to use, select one of the sbarinfo `.skeleton` files, then hit compile.