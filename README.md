# Info
This program helps managing the favorites for the Richard Burns rally game when using the rsf plugin.

This program shows the data regarding all stages and allows the creation of custom favorites listings.

It uses rsf's favorites handling methodology and replaces the currents favorites file with the one selected in the application.

It's primary goal is to allow checking an online rally stages from the [RSF's website](https://rallysimfans.hu/rbr/rally_online.php), and, using the application, create a new favorites file with all the stages from the online rally, this will allow the players to see all the selected stages in the "Favorites" category of the "Practice" mode.

# Installation
Download the zip from the [releases](https://github.com/digoblin/rbr_favorites_manager/releases) and extract it. The executable will be available on the extracted folder.

## Compilation
If you would rather compile it yourself, you can use **pyinstaller** to do so:
```
pyinstaller -w -n rbr_favorites_manager gui.py
```
# How to use
This is the program's main window:
![Main window](menu.png)

1. Start by selecting the RBR install folder, if needed press the "Set RBR Install folder" button
2. This will display all created favorites listing so far, they are saved as "favorite_[name]" in the **./favorites/** folder
3. Search for maps or/and use the filters
4. Use the button to include or exclude maps to the current selected favorites (double clicking a row also works)
5. Save the current favorites with a name (for creating custom listings)
6. Insert the URL from an online rally from [RSF's website](https://rallysimfans.hu/rbr/rally_online.php) to automatically load the stages (only works if online rally is using the original names)
7. You **MUST** press this to view the favorites in RBR. Sets the current favorites as the ones to use in RBR. 