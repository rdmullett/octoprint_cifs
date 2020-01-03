# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import octoprint.util
import os
import time
import glob
import flask

class CifsPlugin(octoprint.plugin.SettingsPlugin,
                 octoprint.plugin.AssetPlugin,
                 octoprint.plugin.TemplatePlugin,
		 octoprint.plugin.StartupPlugin,
		 octoprint.plugin.SimpleApiPlugin):

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			# put your plugin's default settings here
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/cifs.js"],
			css=["css/cifs.css"],
			less=["less/cifs.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			cifs=dict(
				displayName="Cifs Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="rdmullett",
				repo="octoprint_cifs",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/rdmullett/octoprint_cifs/archive/{target_version}.zip"
			)
		)

        # file_find() looks to gather any .gcode files that were modified in the last ten minutes and import them
        def file_find(self):
            self.startTime = time.time()
	    # TODO: this list isn't quite what we need (doesn't collect top level files. os.walk is being funny on loops so need to play with that too....
            self.fileList = glob.glob('/home/pi/.octoprint/remote/' + '**/*.gcode')
            self.filesLastTenMins = []
            for i in self.fileList:
                #if (self.startTime - os.path.getctime(i)) < 600:
		# 1 minute for testing
                if (self.startTime - os.path.getctime(i)) < 60:
                    self.filesLastTenMins.append(i)
            self._logger.info("The files from the last ten minutes are: " + str(self.filesLastTenMins))
            return self.filesLastTenMins

        def on_after_startup(self):
            # run file_find() every 2 minutes
	    #self.fileTimer = octoprint.util.RepeatedTimer(120, self.file_find)
	    # every 20 seconds for testing
	    self.fileTimer = octoprint.util.RepeatedTimer(20, self.file_find)
            self.fileTimer.start()

	def get_template_configs(self):
	    return [
		    dict(type="sidebar", custom_bindings=False)
		   ]

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Cifs Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = CifsPlugin()

	
	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

