# DRLAPDA
## About
The PDA for the DoomRL Arsenal mod. It allows for relatively quick and painless previewing of the hundreds of weapons and equipment items present in the mod via a mouse-driven user interface. Coded entirely through GDCC-ACC.

---

## Notice
While the repository is still being set up, the code cleaned up and adjusted, I apologize for any colorful remarks in the code that I might have left over from long ago.

---

## Thanks
### Alison
For their generous, in-depth knowledge on programming and tricks with ZDoom that helped iron out some interesting issues.

### Yholl
For making the DoomRL Arsenal mod to begin with.

(More credits will come with time as I remember the contributions)

---

## Structure
### acs/
While not present, this is where the compiled bytecode is output to.

### graphics/
Normally assets/, this is to help modern ZDoom-based ports read graphics data.

### source/
Can be named anything, only stores the necessary project files.

---

## Technologies used
### GDCC-ACC
A compiler that can take (extended-)ACS code and output bytecode that ZDoom can then read.

### ASEPRITE
Pixel art focused program which was used to produce a fair few of the graphics

### Photoshop
Creative program which was used to help align and prototype layouts

### Visual Studio Code
Used to work on the new database interpreter for the PDA
