# MistWorld Auto Profession building instructions.

## Translations

Translation is fully supported - there are only a few messages of note. Gettext translations must be placed into `addon\locale\<lang>/LC_MESSAGES\nvda.po`. 

## To package the add-on for distribution:

- Install scons (via pip) `pip install scons`
- Open a command line, change to the folder that has the **SCONSTRUCT** file (usually the root of your add-on development folder) and run the **scons** command. The created add-on, if there were no errors, is placed in the current directory.
- You can further customize variables in the **buildVars.py** file if needed. Also see **addon\manifest.ini** for compatibility with later versions of NVDA.
