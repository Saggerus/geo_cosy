This is a Home Assistant custom integration that allows control of Geo Cosy thermostats (https://cosy.support.geotogether.com/en/support/solutions/articles/7000011187-introducing-cosy)

I've only provided support for a single thermostat and zone (you're welcome to try it with multiple, but I only have the one so don't know what would happen)

Note: This is an unofficial ingtegration, which uses the same calls as the Cosy website.  As it is unofficial, I cannot guarantee that Geo won't block it's use or your account especially if you are making a crazy number of calls to their site.  Use at your own risk.  I've not had any issues myself so far, but will post here should I encounter any problems.

******INSTALLATION*********
Pretty standard install.  Create a folder within your Home Assistant custom_components folder called geo_cosy.  Download the zip of this repository, extract it and copy all the files (not the folder) into the geo_cosy folder you created.  Restart home assistant, then under Settings/Devices and Services Choose add Integration and search for Cosy  and it should bring up the Geo Cosy integration.
Click on it and enter your Cosy username and password.  That should do it.

Add a Thermostat card to your front end, and under features add the preset mode and hvaq mode options
![image](https://github.com/user-attachments/assets/1eb2f02a-0f22-4e5f-8eda-58e4f4f8cd82)


******Usage********
The flame icon button at the bottom turns hibernate off, the power button turns it on.
Select the mode (slumber, comfy or cosy) from the drop down box.
By default the large number in the middle is the target temperature for the currently selected mode, and the small number is the current temperature.  You can switch these around by flicking the 'Show current temperature as primary information' switch in the card settings.
To change the target temperature, either use the + and - buttons on the card, or drag the white crcle with the orange border on the arc.  The light grey dot on the arc signifies the current temperature, so you can see if the target temp is below or above the current temp.

