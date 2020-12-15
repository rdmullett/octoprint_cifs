# OctoPrint-Cifs

Octoprint-Cifs is an Octoprint plugin created to facilitate an easy way to pull new gcode files from a CIFS share of your choosing

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/rdmullett/octoprint_cifs/archive/master.zip

After installation, you will need to ensure that your cifs share is mounted at a location accessible by the pi user. Additionally, you will need to configure the Cifs Plugin in settings, and ensure that the "CIFS Share Path" is updated to reflect the path where you have mounted your CIFS share. Because of the way in which this plugin is implemented, I strongly recommend mounting as low level a directory as you can. For example if you have a CIFS share with multiple folders, I recommend having one that is dedicated to 3d printing only, and only mounting that. This will make the search for gcode files faster, and more efficient.

After confirming that your cifs share is mounted at the same location that you have defined in the CIFS Share Path, you will find there is a new button on your octoprint interface named "Upload from Cifs". When pressing this button the first time it will not upload any files. After that, you will find that every time you press it, it will find all new gcode files and will copy them onto your Octoprint file manager location. 

## Configuration

The primary configuration option available is **CIFS Share Path**. This should reflect the path at which you have mounted your cifs share containing gcode files. 

##Limitations and Considerations

- The plugin cannot currently be configured to modify the time in which it will look backwards. It will only look backwards to the previous run, and grab all files since the last run. 

- This plugin may have a performance hit. At the time of writing that has not been tested, as this has only been developed on a non-functioning 3d printer. While looking at CPU and Memory usage after pressing the button it seems fine (even only on a Raspberry Pi Zero for testing), however I would recommend caution when running this with a print running until it has been tested further. In the future a functionality to limit the ability to upload while a print is running may be implemented, but for now it has not been until further testing is performed.

