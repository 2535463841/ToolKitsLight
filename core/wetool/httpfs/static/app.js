class WetoolFS {
    constructor() {
        this.postAction = function (action, onload_callback, onerror_callback = null) {
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
            xhr.send(JSON.stringify({action: action}));
        };
        this.getDir = function(currentDir, showAll, onload_callback, onerror_callback = null) {
            var action = {
                name: 'list_dir',
                params: { path: currentDir, all: showAll }
            };
            this.postAction(action, onload_callback, onerror_callback=onerror_callback);
        };
        this.deleteDir = function (filename, dir, onload_callback, onerror_callback = null) {
            var action = {
                name: 'delete_dir',
                params: { path: dir, file: filename }
            };
            this.postAction(action, onload_callback, onerror_callback = onerror_callback);
        };
    }
}
var app = new Vue({
    el: '#app',
    data: {
        currentDir: '',
        children: [],
        historyPath: [],
        linkQrcode: '',
        downloadFile: {name: '', qrcode: ''},
        showAll: true,
        wetoolFS: new WetoolFS()
    },
    methods: {
        changeDirectory: function(path, pushHistory=false){
            if (pushHistory){
                this.historyPath.push(this.currentDir);
            }
            if (this.currentDir == '/'){
                this.currentDir = this.currentDir + path;
            }else{
                this.currentDir = this.currentDir + '/' + path;
            }
            this.refreshChildren();
        },
        goBack: function(){
            var lastHref = this.historyPath.pop();
            if (typeof(lastHref) == 'undefined'){
                lastHref = '/';
            }
            this.currentDir = lastHref;
            this.refreshChildren();
        },
        goHome: function(){
            if (this.currentDir != '/'){
                this.historyPath.push(this.currentDir);
                this.currentDir = '/';
                this.refreshChildren();
            }
        },
        logDebug: function(msg, level='Debug', autoHideDelay=1000){
            this.$bvToast.toast(msg, {
                title: level,
                variant: 'default',
                autoHideDelay: autoHideDelay
            });
        },

        logInfo: function(msg, level='Info', autoHideDelay=1000){
            this.$bvToast.toast(msg, {
                title: level,
                variant: 'success',
                autoHideDelay: autoHideDelay
            });
        },
        logWarn: function(msg, level='Warn', autoHideDelay=1000){
            this.$bvToast.toast(msg, {
                title: level,
                variant: 'warning',
                autoHideDelay: autoHideDelay
            });
        },
        logError: function(msg, level='Error', autoHideDelay=1000){
            this.$bvToast.toast(msg, {
                title: level,
                variant: 'danger',
                autoHideDelay: autoHideDelay
            });
        },
        refreshChildren: function(){
            this.logDebug('更新目录');
            var self = this;
            if (this.currentDir == ''){
                return
            }
            this.wetoolFS.getDir(
                self.currentDir, self.showAll,
                function (status, data) {
                    if (status == 200){self.children = data.dir.children;}
                    else{
                        self.logError(`请求失败，${status}, ${data.error}`);
                        self.currentDir = self.historyPath.pop();
                    }
                },
                function () {self.logError('请求失败');}
            )
        },
        getAbsPath: function(child){
            var absPath = this.currentDir;
            if (absPath == '/'){
                absPath += child.name;
            }else{
                absPath += '/' + child.name;
            }
            return absPath;
        },
        clickPath: function(child){
            if (child.type == "folder") {
                this.changeDirectory(child.name, pushHistory=true);
            }
        },
        showQrcode: function(child){
            this.downloadFile = child;
        },
        getDownloadUrl: function(item){
            return '/download/' + encodeURIComponent(item.name) + '?path=' + encodeURIComponent(this.currentDir)
        },
        deleteDir: function(item){
            var self = this;
            this.wetoolFS.deleteDir(
                self.currentDir, item.name,
                function(status, data){
                    if (status == 200){
                        self.logInfo('删除成功'); self.refreshChildren();
                    }else{
                        self.logError(`删除失败, ${status}, ${data.error}`);
                    }
                },
                function(){
                    self.logError('请求失败');
                }
            );
        },
        toggleShowAll: function(){
            this.showAll = ! this.showAll;
            this.refreshChildren();
        },
        renameDir: function(item){
            this.logError('该功能未实现');
        }
    },
    created: function(){
        this.changeDirectory('', pushHistory=true);
    }
});
