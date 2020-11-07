/*
 * View model for OctoPrint-Cifs
 *
 * Author: Ryan Mullett
 * License: AGPLv3
 */
$(function() {
    function CifsViewModel(parameters) {
        var self = this;
	self.settings = undefined;
	self.btnUpload = undefined;
	self.btnUploadTest = undefined;

	self.loginState = parameters[0];
	self.printerState = parameters[1];
	self.settings = parameters[2];
	
	self.upload = function() {
		$.ajax({
			url: API_BASEURL + "plugin/cifs",
			type: "POST",
			dataType: "json",
			data: JSON.stringify({
				command: "file_find"
			}),
			contentType: "application/json; charset=UTF-8",
		});
	};
	
	self.btnUploadClick = function() {
		self.upload()
	};

	self.initializeButton = function() {
		var buttonContainer = $('.fileinput-button')[0].parentElement;
		       	/*buttonContainer.children[0].style.width = "100px";
                        buttonContainer.children[0].style.marginBottom = "10px";
                        buttonContainer.children[1].style.marginLeft = "0";
                        buttonContainer.children[1].style.marginRight = "0";*/
			                        
                        self.btnUpload = document.createElement("button");
                        self.btnUpload.id = "job_preheat";
                        self.btnUpload.classList.add("btn");
                        self.btnUpload.classList.add("span4");
                        self.btnUpload.addEventListener("click", self.btnUploadClick);
			self.btnUpload.name = "Upload from Cifs";
			self.btnUpload.style.width = "268px";
			self.btnUpload.style.marginLeft="0px";
			self.btnUpload.style.marginBottom = "10px";
                        
                        self.btnUploadText = document.createTextNode(" ");
                        self.btnUpload.appendChild(self.btnUploadText);
                        
                        self.btnUploadText.nodeValue = " Upload From Cifs ";
                        
                        buttonContainer.appendChild(self.btnUpload);
	};

	self.onDataUpdaterPluginMessage = function(plugin, data) {
		if (plugin == "cifs" && data.type == "not_mounted") {
			new PNotify({
				title: 'CIFS share not mounted',
				text: 'CIFS share is not mounted. Please mount it and try again',
				type: 'warning'
			});
		}
		if (plugin == "cifs" && data.type == "upload_successful") {
			new PNotify({
				title: 'Files uploaded',
				text: 'Files uploaded successfully!',
				type: 'success'
			});
		}
	}

	self.initializeButton();

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
	}
    OCTOPRINT_VIEWMODELS.push({

        construct: CifsViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "loginStateViewModel", "filesViewModel", /*"settingsViewModel",*/ "printerStateViewModel"/* "loginStateViewModel", "settingsViewModel" */ ],
        // Elements to bind to, e.g. #settings_plugin_cifs, #tab_plugin_cifs, ...
        elements: [ /* ... */ ]
    });
});
