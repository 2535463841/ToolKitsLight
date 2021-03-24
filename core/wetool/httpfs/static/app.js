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
        this.deleteDir = function (dir, filename, onload_callback, onerror_callback = null) {
            var action = {
                name: 'delete_dir',
                params: { path: dir, file: filename }
            };
            console.log(action);
            this.postAction(action, onload_callback, onerror_callback = onerror_callback);
        };
        this.renameDir = function (filename, dir, newName, onload_callback, onerror_callback = null) {
            var action = {
                name: 'rename_dir',
                params: {path: dir, file: filename, new_name: newName}
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
        wetoolFS: new WetoolFS(),
        renameItem: {name: '', newName: ''}
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
        logDebug: function(msg, autoHideDelay=1000, title='Debug',){
            this.$bvToast.toast(msg, {
                title: title,
                variant: 'default',
                autoHideDelay: autoHideDelay
            });
        },

        logInfo: function(msg, autoHideDelay=1000, title='Info'){
            this.$bvToast.toast(msg, {
                title: title,
                variant: 'success',
                autoHideDelay: autoHideDelay
            });
        },
        logWarn: function(msg, autoHideDelay=1000, title='Warn'){
            this.$bvToast.toast(msg, {
                title: title,
                variant: 'warning',
                autoHideDelay: autoHideDelay
            });
        },
        logError: function(msg, autoHideDelay=5000, level='Error'){
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
        renameDir: function(){
            var self = this;
            if (self.renameItem.name == self.renameItem.newName || self.renameItem.newName == ''){
                self.logError('文件名不合法');
                return;
            }
            this.wetoolFS.renameDir(
                self.renameItem.name, self.currentDir, self.renameItem.newName,
                function(status, data){
                    if (status == 200){
                        self.logInfo('重命名成功');
                        self.refreshChildren();
                    }else{
                        self.logError(`重命名失败, ${status}, ${data.error}`, autoHideDelay=5000)
                    }
                },
                function(){
                    self.logError('请求失败')
                }
            )
            // this.logError('该功能未实现');
        },
        showRenameModal: function(item){
            this.renameItem = {name: item.name, newName: item.name}
        }
    },
    created: function(){
        this.changeDirectory('', pushHistory=true);
    }
});
