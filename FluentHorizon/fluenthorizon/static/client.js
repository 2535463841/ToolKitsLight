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
        this.listResource = function(resource_name, onload_callback, onerror_callback= null){
            this.wetoolFS.postAction({'name': `list_${resource_name}`}, onload_callback, onerror_callback)
        };
    }
}

function delItemsAfter(array, afterIndex){
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
};

class ChartPieUsed {
    constructor(eleId, title) {
        this.elemId = eleId;
        this.title = title;
        this.data = {};
        this.chart = null;

        this.setData = function(data){
            // used: >= 1.8 -> red
            //       >= 1   -> oranage
            //       <1     -> blue
            let color = 'rgb(66, 139, 202)';
            if (data.length >= 2){
                if(data[1].value > 0){
                    let usedPercent = data[0].value / data[1].value;
                    if(usedPercent >= 1.8){
                        color = 'rgb(217, 83, 79)';
                    }else if(usedPercent >= 1){
                        color = 'rgb(255, 193, 7)'
                    }
                }
            }
            this.chart.setOption({
                title: {text: title, left: 'center'},
                tooltip: {trigger: 'item'},
                series: [{
                    name: title, type: 'pie', radius: '80%',
                    color:[color, 'rgb(206, 206, 206)'],
                    label: {show: false},
                    data: data,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'}
                    }},
                ]
            });
        };
        this.init = function(){
            let elem = document.getElementById(this.elemId);
            this.chart = echarts.init(elem);
        };
        this.reset = function(){
            this.chart = null;
        };
        this.refresh = function(data){
            let elem = document.getElementById(this.elemId);
            if (elem == null){
                return
            }
            if (this.chart == null){
                this.chart = echarts.init(elem);
            };
            var dataList = [];
            for (var key in data) {
                let value = data[key];
                dataList.push({value: value, name: key});
            }
            this.setData(dataList);
        }
    }
}

class LOGGER {
    constructor(bvToast) {
        this.bvToast = bvToast;

        this.debug = function (msg, autoHideDelay = 1000, title = 'Debug') {
            if (this.debug == false) {
                return
            }
            this.bvToast.toast(msg, {
                title: title,
                variant: 'default',
                autoHideDelay: autoHideDelay
            });
        },

        this.info  = function (msg, autoHideDelay = 1000, title = 'Info') {
            this.bvToast.toast(msg, {
                title: title,
                variant: 'success',
                autoHideDelay: autoHideDelay
            });
        },
        this.warn = function (msg, autoHideDelay = 1000, title = 'Warn') {
            this.bvToast.toast(msg, {
                title: title,
                variant: 'warning',
                autoHideDelay: autoHideDelay
            });
        },
        this.error = function (msg, autoHideDelay = 5000, level = 'Error') {
            this.bvToast.toast(msg, {
                title: level,
                variant: 'danger',
                autoHideDelay: autoHideDelay
            });
        }
    }
}