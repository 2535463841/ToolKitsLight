class WetoolFS {
    constructor() {
        this.postAction = function (body, onload_callback, onerror_callback = null, uploadCallback = null) {
            var xhr = new XMLHttpRequest();
            xhr.onload = function () {
                var data = JSON.parse(xhr.responseText);
                onload_callback(xhr.status, data);
            };
            xhr.onerror = function () {
                if (onerror_callback != null) {
                    onerror_callback();
                }
            };
            xhr.open("POST", '/action', true);
            if (body.constructor.name == 'FormData') {
                xhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        if (uploadCallback != null) {
                            uploadCallback(e.loaded, e.total);
                        }
                    }
                });

                xhr.send(body);
            } else {
                xhr.send(JSON.stringify({ action: body }));
            }
        };
        this.getDir = function (currentDir, showAll, onload_callback, onerror_callback = null) {
            var action = {
                name: 'list_dir',
                params: { path: currentDir, all: showAll }
            };
            this.postAction(action, onload_callback, onerror_callback = onerror_callback);
        };
        this.deleteDir = function (dir, filename, onload_callback, onerror_callback = null) {
            var action = {
                name: 'delete_dir',
                params: { path: dir, file: filename, force: true }
            };
            console.log(action);
            this.postAction(action, onload_callback, onerror_callback = onerror_callback);
        };
        this.renameDir = function (filename, dir, newName, onload_callback, onerror_callback = null) {
            var action = {
                name: 'rename_dir',
                params: { path: dir, file: filename, new_name: newName }
            };
            this.postAction(action, onload_callback, onerror_callback = onerror_callback);
        };
        this.createDir = function (path, dirName, onload_callback, onerror_callback = null) {
            var action = {
                name: 'create_dir',
                params: { path: path, dir_name: dirName }
            };
            this.postAction(action, onload_callback, onerror_callback = onerror_callback);
        };
        this.getFileContent = function (dir, filename, onload_callback, onerror_callback = null) {
            var action = {
                name: 'get_file',
                params: { path: dir, file: filename }
            };
            this.postAction(action, onload_callback, onerror_callback = onerror_callback);
        };
        this.uploadFile = function (dir, file, onload_callback, onerror_callback = null, uploadCallback = null) {
            var action = {
                name: 'upload_file',
                params: { path: dir , relative_path: file.webkitRelativePath}
            };
            var formData = new FormData();
            formData.append('action', JSON.stringify(action));
            formData.append('file', file);
            this.postAction(formData, onload_callback, onerror_callback = onerror_callback, uploadCallback = uploadCallback);
        }
    }
}
