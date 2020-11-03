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
import flask
import fnmatch
import subprocess
import re

class CifsPlugin(octoprint.plugin.SettingsPlugin,
                 octoprint.plugin.AssetPlugin,
                 octoprint.plugin.TemplatePlugin,
		 octoprint.plugin.StartupPlugin,
		 octoprint.plugin.SimpleApiPlugin,
		):

	def get_api_commands(self):
		return dict(
			file_find = []
		)

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			url="example.com"
			# put your plugin's default settings here
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/cifs.js"],
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
	#TODO: add state about when the last time that file_find got ran and instead of doing 10 minutes, look back to that timestamp
        def file_find(self):
            self.startTime = time.time()
	    self._logger.info("Button was pressed at: " + str(self.startTime))
	    self.fileList = []
	    for r, d, f in os.walk('/home/pi/.octoprint/remote/3dprinting'):
		for file in f:
		    if ".gcode" in file:
			    self.fileList.append(os.path.join(r, file))
            self.filesLastTenMins = []
            for i in self.fileList:
                #if (self.startTime - os.path.getctime(i)) < 600:
		# 1 minute for testing
                if (self.startTime - os.path.getctime(i)) < 60:
                    self.filesLastTenMins.append(i)
            self._logger.info("The files from the last ten minutes are: " + str(self.filesLastTenMins))
            return self.filesLastTenMins

	def mount_check(self):
            self.cifsUrl = self._settings.get(["url"])

            if self.cifsUrl != "example.com":
                    self._logger.info("Confirming that %s is mounted" % self.cifsUrl)
            elif self.cifsUrl == "example.com":
                    self._logger.info("CIFS URL is set to example.com. Skipping mount.")
            elif self.cifsUrl == None:
                    self._logger.info("CIFS URL is unset. Skipping mount.")
            self.p = subprocess.Popen(["df"], shell=False, stdout=subprocess.PIPE)
            self.output = self.p.communicate()
            self.checkRegex = re.compile(str(self.cifsUrl))
            self.regexSearcher = self.checkRegex.search(str(self.output))

            if self.regexSearcher is not None:
                self._logger.info("Cifs share is already mounted!")
            else:
                self._logger.info("Cifs share is NOT mounted!")
		fstab_regex = re.compile('#cifs_share')
		with open('/etc/fstab', 'rw') as f:
		    for line in f:
			result = fstab_regex.search(line)
		    f.close()
		self._logger.info("%s found in fstab" % result)
		if result == None:
			fstabAppend = open("/etc/fstab", "a")
			fstabAppend.write('\#cifs_share')
			fstabAppend.close()
		else:
		    self._logger.info("#cifs_share was found")


        def on_after_startup(self):
	    os.chmod('/etc/fstab', stat.S_IWOTH)
	    self.mount_check()

	def get_template_vars(self):
	    return dict(cifs_share=self._settings.get(["cifs_share"]))

	def get_template_configs(self):
	    return [
		    dict(type="settings", custom_bindings=False),
	    ]

        def on_settings_save(self, data):
            old_value = self._settings.get(["cifs_share"])

            octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

            new_value = self._settings.get(["cifs_share"])

            #TODO: change this to actually make the required changes in fstab and add the updated CIFS share on setting save. For now we log it as a test to ensure functionality
            if old_value != new_value:
                self._logger.info("cifs_share changed from %s to %s" %(old_value, new_value))

	    self.mount_check()

	def on_api_command(self, command, data):
		if command == "file_find":
			self.file_find()


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

