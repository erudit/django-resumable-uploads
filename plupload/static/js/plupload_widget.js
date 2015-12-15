var create_uploader = function(params) {
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    var path = params['path'];

    var uploader = new plupload.Uploader({
        browse_button: 'pickfiles',
        // TODO: Customize runtimes
        runtimes : 'html5,gears,silverlight',

        url : params['url'],
        max_file_size : params['max_file_size'],
        chunk_size : params['chunk_size'],
        unique_names : false,
        multipart_params: {"csrfmiddlewaretoken" : csrf_token },

        // Silverlight settings
        silverlight_xap_url : params['STATIC_URL'] + 'js/Moxie.xap',

        init: {
            FileUploaded: function(up, file, info) {
                $('#' + params['id']).val(path + "/" + file.name);
            },
            PostInit: function() {
		document.getElementById('filelist').innerHTML = '';

		document.getElementById('uploadfiles').onclick = function() {
		    uploader.start();
		    return false;
		};
	    },
	    FilesAdded: function(up, files) {
		plupload.each(files, function(file) {
        var fileStatus = '<span class="progress"><span class="progress-bar progress-bar-striped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">0%</span></span>';
        var fileDelete = '<a href="#"><span class="fa fa-remove"></span></a>';
		    document.getElementById('filelist').innerHTML +=
            '<tr id="' +
            file.id +
            '"><td class="file-name"><span>' +
            file.type +
            '</span> ' +
            file.name +
            '</td><td class="file-size">' +
            plupload.formatSize(file.size) +
            '</td><td class="file-status">' +
            fileStatus +
            '</td><td class="file-delete">' +
            fileDelete +
            '</td></tr>';
		});
	    },

	    UploadProgress: function(up, file) {
          var progressBar = document.getElementById(file.id).getElementsByClassName('progress-bar')[0];
          progressBar.innerHTML = file.percent + "%";
          progressBar.style.width = file.percent + "%";
	    },

	    Error: function(up, err) {
		document.getElementById('console').appendChild(document.createTextNode("\nError #" + err.code + ": " + err.message));
	    }

        }
    });

    uploader.init();
};
