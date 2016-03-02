var create_uploader = function(params, filesizes) {
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    var path = params['path'];

    var uploader = new plupload.Uploader({
        browse_button: 'pickfiles',
        // TODO: Customize runtimes
        runtimes : 'html5,gears,silverlight',

        url : params['url'],
        max_file_size : params['max_file_size'],
        chunk_size : params['chunk_size'],
        drop_element: params['drop_element'],
        unique_names : false,
        multipart_params: {
            "csrfmiddlewaretoken" : csrf_token,
            "model": String(params['model_name']),
            "pk": String(params['model_id'])
        },

        // Silverlight settings
        silverlight_xap_url : params['STATIC_URL'] + 'js/Moxie.xap',

        init: {
            StateChanged: function(up) {
                if (up.state == plupload.STARTED) {
                    for (var file_id in up.files) {
                        var file = up.files[file_id];
                        post_values = {
                            'name':  file.name,
                            'csrfmiddlewaretoken': csrf_token,
                            "model": String(params['model_name']),
                            "pk": String(params['model_id']),
                            "filesize": file.size,
                        }
                        $.ajax({
                          type: 'POST',
                          url: params['url'] + "set_file_info",
                          data: post_values,
                          async: false
                        });
                    }
                }
            },

            BeforeUpload: function(up, file) {
                var loaded = filesizes[file['name']];
                if (loaded !== undefined) {
                    file.loaded = loaded;
                }
            },

            FileUploaded: function(up, file, info) {
                var json = JSON.parse(info.response);
                var currentVal = $('#' + params['id']).val();
                var newVal = json.id;
                if (currentVal) {
                    newVal = currentVal + ',' + newVal;
                }
                $('#' + params['id']).val(newVal);
            },
            PostInit: function() {
                document.getElementById('uploadfiles').onclick = function() {
                    uploader.start();
                    return false;
                };
            },
            FilesAdded: function(up, files) {
                plupload.each(files, function(file) {
                    var fileStatus = '<span class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">0%</span>';
                    var fileDelete = '<a href="#" class="icon-upload icon-delete"></a>';
                    var fileName = file.name;
                    var fileType = fileName.substr(fileName.lastIndexOf('.') + 1).toLowerCase();
                    document.getElementById('filelist').innerHTML +=
                    '<tr id="' +
                    file.id +
                    '"><td class="file-type"><span class="icon-file icon-' +
                    fileType +
                    '"></span></td><td class="file-name">' +
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
