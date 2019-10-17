var create_uploader = function(params, filesizes) {
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    var path = params['path'];

    function addIdToUploadField(new_id) {
        var currentVal = $('#' + params['id']).val();
        var newVal = new_id;
        if (currentVal) {
            var ids = currentVal.split(',');
            ids.push(newVal);
            var uids = [];
            $.each(ids, function(i, el){if($.inArray(String(el), uids) === -1) uids.push(String(el));});
            newVal = uids.join(',');
        }
        $('#' + params['id']).val(newVal);
    }

    function removeIdFromUploadField(file_id) {
        var currentVal = $('#' + params['id']).val();
        var newVal = '';
        if (currentVal) {
            var ids = currentVal.split(',');
            ids = ids.filter(function(el) {
                return el !== String(file_id);
            });
            newVal = ids.join(',');
        }
        $('#' + params['id']).val(newVal);
    }

    function getMaxFileCount() {
        return params['max_file_count'] !== undefined ? params['max_file_count'] : 1;
    }

    function getCurrentFileCount() {
        return $('#filelist').children().length;
    }

    function triggerBrowseButton(up) {
        up.disableBrowse(getCurrentFileCount() >= getMaxFileCount());
    }

    // This object is used to keep track of the data that is transferred
    var upload = {
        file: null,
        offset: 0
    };

    var options = {
        multipart_params: {
            "csrfmiddlewaretoken" : csrf_token,
            "model": String(params['model_name']),
            "pk": String(params['model_id'])
        },

        // Silverlight settings
        silverlight_xap_url : params['STATIC_URL'] + 'js/Moxie.xap',

        init: {
            init: function(up) {
                // Disable the browse button if we have more files than the max allowed.
                triggerBrowseButton(up);
            },

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
                        }).done(function(response){
                            addIdToUploadField(response.id);
                        });
                    }
                }
            },

            BeforeUpload: function(up, file) {
                // Update upload state
                upload.file = file;
                upload.offset = 0;

                // Update input' data attributes
                var filesAddedCount = $('#' + params['id']).data('files-added');
                filesAddedCount = (filesAddedCount) ? parseInt(filesAddedCount) - 1 : 0;
                var filesUploadingCount = $('#' + params['id']).data('files-uploading');
                filesUploadingCount = (filesUploadingCount) ? parseInt(filesUploadingCount) + 1 : 1;
                $('#' + params['id']).data('files-added', filesAddedCount);
                $('#' + params['id']).data('files-uploading', filesUploadingCount);

                var loaded = filesizes[file['name']];
                if (loaded !== undefined) {
                    file.loaded = loaded;
                }
            },

            ChunkUploaded: function (up, file, info) {
                // Update upload state
                upload.offset = info.offset;
            },

            FileUploaded: function(up, file, info) {
                // Update upload state
                upload.file = null;

                var json = JSON.parse(info.response);
                addIdToUploadField(json.id);
                $('#' + file.id).data('resumable-file-id', json.id);

                // Update input' data attributes
                var filesUploadingCount = $('#' + params['id']).data('files-uploading');
                filesUploadingCount = (filesUploadingCount) ? parseInt(filesUploadingCount) - 1 : 0;
                $('#' + params['id']).data('files-uploading', filesUploadingCount);
            },
            PostInit: function(up) {
                $('#uploadfiles').on('click', function() {
                    up.start();
                });
            },
            FilesAdded: function(up, files) {
                plupload.each(files, function(file) {
                    if (getCurrentFileCount() >= getMaxFileCount()) {
                        up.removeFile(file);
                        return;
                    }

                    var filesAddedCount = $('#' + params['id']).data('files-added');
                    if (filesAddedCount) {
                        $('#' + params['id']).data('files-added', filesAddedCount + 1);
                    } else {
                        $('#' + params['id']).data('files-added', files.length);
                    }

                    var fileStatus = '<span class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">0%</span>';
                    var fileDelete = '<a href="#" class="delete-file icon-upload icon-delete"></a>';
                    var fileName = file.name;
                    var fileType = fileName.substr(fileName.lastIndexOf('.') + 1).toLowerCase();
                    document.getElementById('filelist').innerHTML +=
                    '<tr data-resumable-file-name="' + fileName + '" id="' +
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

                // Automatic upload of added files.
                if (params['auto_upload']) {
                    up.start();
                }

                // Disable the browse button if we have more files than the max allowed.
                triggerBrowseButton(up);
            },

            UploadProgress: function(up, file) {
                var progressBar = document.getElementById(file.id).getElementsByClassName('progress-bar')[0];
                progressBar.innerHTML = file.percent + "%";
                progressBar.style.width = file.percent + "%";
            },

            Error: function(up, err) {
                if(err.code !== plupload.HTTP_ERROR) {
                    return true;
                }
                uploader.stop();
                console.warn('[plupload] stopped (HTTP Error)');
                window.setTimeout(retry, 5000);
            }

        }
    };

    var uploader = new plupload.Uploader($.extend(options, params))

    uploader.init();

    var retry = function () {
        console.log('[plupload] restarted (retry)');
        upload.file.loaded = upload.offset;
        upload.file.status = plupload.UPLOADING;
        // the following is similar to uploader.start()
        // but starts a specific file at a specific position
        uploader.state = plupload.STARTED;
        uploader.trigger('UploadFile', upload.file);
    };

    window.addEventListener('offline', function () {
        console.log('[plupload] stopped (offline)');
        uploader.stop();
    }, false);

    window.addEventListener('online', function() {
        if(upload.file === null) {
            return false;
        }
        retry();
    }, false);

    $(document).on('click', 'a.delete-file', function(ev){
        ev.preventDefault();

        var $fileRow = $(this).parents('tr');
        var fileId = $fileRow.data('resumable-file-id');
        var fileAttrId = $fileRow.attr('id');
        var fileName = $fileRow.data('resumable-file-name');

        if (!$fileRow.length) return;

        r = confirm(gettext("Vous allez supprimer le fichier " + fileName + ", cliquez sur « Annuler » pour le conserver ou sur « Ok » pour poursuivre la suppression."));
        if (r !== true) { return; }

        if (fileId) {
            post_values = {
                'csrfmiddlewaretoken': csrf_token,
                "pk": fileId,
            }
            $.ajax({
              type: 'POST',
              url: params['url'] + "resumable-file/" + fileId + "/delete/",
              data: post_values,
              async: false
            }).done(function(response){
                if (fileAttrId) uploader.removeFile(fileAttrId);
                removeIdFromUploadField(fileId);
                $fileRow.remove();
                filesizes[fileName] = undefined;
            });
        } else {
            uploader.removeFile(fileAttrId);
            $fileRow.remove();
            var filesAddedCount = $('#' + params['id']).data('files-added');
            filesAddedCount = (filesAddedCount) ? parseInt(filesAddedCount) - 1 : 0;
            $('#' + params['id']).data('files-added', filesAddedCount);
        }

        // Enable the browse button if we have less files than the max allowed.
        triggerBrowseButton(uploader);
    });

    // Set custom validation message for the input field.
    var input = document.getElementById(params['id']);
    input.oninvalid = function(ev) {
        ev.target.setCustomValidity();
        if (!ev.target.validity.valid) {
            ev.target.setCustomValidity(gettext('Veuillez ajouter un fichier.'));
        }
    };
    input.oninput = function(ev) {
        ev.target.setCustomValidity();
    };
};

$(document).ready(function(){
    $('.upload-container').each(function(){
      var json_params = $(this).data('json-params');
      var filesizes = $(this).data('filesizes');
      create_uploader(
        json_params,
        filesizes
      );
    });
});
