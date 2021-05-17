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
            xhr.open("POST", '/actions', true);
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
                xhr.send(JSON.stringify({action: body }));
            }
        };
        this.uploadFile = function (path_list, file, onload_callback, onerror_callback = null, uploadCallback = null) {
            var action = {
                name: 'upload_file',
                params: { path_list: path_list , relative_path: file.webkitRelativePath}
            };
            var formData = new FormData();
            formData.append('action', JSON.stringify(action));
            formData.append('file', file);
            this.postAction(formData, onload_callback, onerror_callback = onerror_callback, uploadCallback = uploadCallback);
        };
        this.get = function (body, onload_callback, onerror_callback = null, uploadCallback = null) {
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
        this.getServerInfo = function(onload_callback, onerror_callback = null){
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
            xhr.open("GET", '/server', true);
            xhr.send();
        };

    }
}

function delItemsAfter(array, afterIndex){
    // Delete array items after <afterIndex>
    while(array.length > afterIndex +1){
        array.pop();
    }
}

function getItemsBefore(array, beforeIndex){
    let items = [];
    if (beforeIndex >= array.length){
        items = [].concat(array);
    }else{
        for (let index = 0; index <= beforeIndex; index++) {
            items.push(array[index]);
        }
    }
    return items;
}