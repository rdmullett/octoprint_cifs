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
import datetime
import flask
import fnmatch
import re
import stat
import shutil

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
			path="/example/path/to/cifs/mount",
			timelastrun=0.0
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

	# this is to find the time that octoprint_cifs was last run and import everything since then
	def time_delta_set(self):
	    self.timeNow = time.time()
	    self.timeLastRun = self._settings.get(["timelastrun"])
	    if self.timeLastRun == 0.0:
		self._logger.info("Looks like this is being run for the first time or the button was double clicked. Skipping upload")
		self._logger.info("Time of current run %s" % self.timeNow)
		self._settings.set_float(["timelastrun"],self.timeNow)
		delta = 0
		return self.timeNow, delta
	    else:
		delta = self.timeNow - self.timeLastRun
		self._logger.info("Time of current run %s" % self.timeNow)
		self._settings.set_float(["timelastrun"],self.timeNow)
		return self.timeNow, delta

        def mount_check(self):
            self.cifsPath = self._settings.get(["path"])
            if self.cifsPath != "/example/path/to/cifs/mount":
                    self._logger.info("Confirming that %s is mounted" % self.cifsPath)
		    if os.path.ismount(self.cifsPath):
                	self._logger.info("Cifs share is mounted.")
			return True
		    else:
	                self._logger.warn("Cifs share is NOT mounted!")
	                self._plugin_manager.send_plugin_message(self._identifier, dict(type="not_mounted"))
			return False
			
            elif self.cifsPath == "/example/path/to/cifs/mount":
                    self._logger.info("CIFS path is set to /example/path/to/cifs/mount. Please set with the proper path to the cifs mount and try again.")
		    return False
            elif self.cifsPath == None:
                    self._logger.info("CIFS path is unset. Please set with the proper path to the cifs mount and try again.")
		    return False

        # file_find() looks to gather any .gcode files that were modified since the last run and upload them
	#TODO: add refresh on the files plugin so that the file shows right away. for now can just click the button
        def file_find(self):
	    self.timeStart, self.timeDelta = self.time_delta_set()
	    self.mounted = self.mount_check()
	    self.timeDeltaMinutes = (self.timeDelta / 60)
	    if not self.mounted:
		self.uploaded = "No files uploaded."
		self._logger.warning(self.uploaded)
		return self.uploaded
	    elif self.mounted:
	            self.startTime = time.time()
		    self.fileList = []
		    for r, d, f in os.walk(self.cifsPath):
			for file in f:
			    if ".gcode" in file:
				    self.fileList.append(os.path.join(r, file))
	            self.filesSinceLastRun = []
	            for i in self.fileList:
	                if (self.timeStart - os.path.getctime(i)) < self.timeDelta:
	                    self.filesSinceLastRun.append(i)
	            self._logger.info("The files from the last %s minutes are: %s" %(str(self.timeDeltaMinutes), str(self.filesSinceLastRun)))
		    for i in self.filesSinceLastRun:
			uploadPath = "/home/pi/.octoprint/uploads/" + os.path.basename(i)
			shutil.copyfile(i, uploadPath)
			self._logger.info("Uploaded %s" %uploadPath)

        def on_after_startup(self):
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

