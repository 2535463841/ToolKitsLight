
var app = new Vue({
    el: '#app',
    data: {
        currentDir: '',
        children: [],
        historyPath: [],
        linkQrcode: '',
        downloadFile: { name: '', qrcode: '' },
        showAll: false,
        wetoolFS: new WetoolFS(),
        renameItem: { name: '', newName: '' },
        newDir: { name: '' },
        fileEditor: { name: '', content: '' },
        uploadProgess: { loaded: 0, total: 100 },
        uploadQueue: { completed: 0, tasks: [] },
        debug: false
    },
    methods: {
        // translate: translate,
        changeDirectory: function (path, pushHistory = false) {
            if (pushHistory) {
                this.historyPath.push(this.currentDir);
            }
            if (this.currentDir == '/') {
                this.currentDir = this.currentDir + path;
            } else {
                this.currentDir = this.currentDir + '/' + path;
            }
            this.refreshChildren();
        },
        goBack: function () {
            var lastHref = this.historyPath.pop();
            if (typeof (lastHref) == 'undefined') {
                lastHref = '/';
            }
            this.currentDir = lastHref;
            this.refreshChildren();
        },
        goHome: function () {
            if (this.currentDir != '/') {
                this.historyPath.push(this.currentDir);
                this.currentDir = '/';
                this.refreshChildren();
            }
        },
        logDebug: function (msg, autoHideDelay = 1000, title = 'Debug') {
            if (this.debug == false){
                return
            }
            this.$bvToast.toast(msg, {
                title: title,
                variant: 'default',
                autoHideDelay: autoHideDelay
            });
        },

        logInfo: function (msg, autoHideDelay = 1000, title = 'Info') {
            this.$bvToast.toast(msg, {
                title: title,
                variant: 'success',
                autoHideDelay: autoHideDelay
            });
        },
        logWarn: function (msg, autoHideDelay = 1000, title = 'Warn') {
            this.$bvToast.toast(msg, {
                title: title,
                variant: 'warning',
                autoHideDelay: autoHideDelay
            });
        },
        logError: function (msg, autoHideDelay = 5000, level = 'Error') {
            this.$bvToast.toast(msg, {
                title: level,
                variant: 'danger',
                autoHideDelay: autoHideDelay
            });
        },
        refreshChildren: function () {
            this.logDebug('更新目录');
            var self = this;
            if (this.currentDir == '') {
                return
            }
            this.wetoolFS.getDir(
                self.currentDir, self.showAll,
                function (status, data) {
                    if (status == 200) { self.children = data.dir.children; }
                    else {
                        self.logError(`请求失败，${status}, ${data.error}`);
                        self.currentDir = self.historyPath.pop();
                    }
                },
                function () { self.logError('请求失败'); }
            )
        },
        getAbsPath: function (child) {
            var absPath = this.currentDir;
            if (absPath == '/') {
                absPath += child.name;
            } else {
                absPath += '/' + child.name;
            }
            return absPath;
        },
        clickPath: function (child) {
            if (child.type == "folder") {
                this.changeDirectory(child.name, pushHistory = true);
            }
        },
        showQrcode: function (child) {
            this.downloadFile = child;
        },
        getDownloadUrl: function (item) {
            return '/download/' + encodeURIComponent(item.name) + '?path=' + encodeURIComponent(this.currentDir)
        },
        deleteDir: function (item) {
            var self = this;
            this.wetoolFS.deleteDir(
                self.currentDir, item.name,
                function (status, data) {
                    if (status == 200) {
                        self.logInfo('删除成功'); self.refreshChildren();
                    } else {
                        self.logError(`删除失败, ${status}, ${data.error}`);
                    }
                },
                function () {
                    self.logError('请求失败');
                }
            );
        },
        toggleShowAll: function () {
            this.showAll = !this.showAll;
            this.refreshChildren();
        },
        renameDir: function () {
            var self = this;
            if (self.renameItem.name == self.renameItem.newName) {
                return;
            }
            if (self.renameItem.newName == '') {
                self.logError('文件名不能为空');
                return;
            }
            this.wetoolFS.renameDir(
                self.renameItem.name, self.currentDir, self.renameItem.newName,
                function (status, data) {
                    if (status == 200) {
                        self.logInfo('重命名成功');
                        self.refreshChildren();
                    } else {
                        self.logError(`重命名失败, ${status}, ${data.error}`, autoHideDelay = 5000)
                    }
                },
                function () {
                    self.logError('请求失败')
                }
            )
            // this.logError('该功能未实现');
        },
        showRenameModal: function (item) {
            this.renameItem = { name: item.name, newName: item.name }
        },
        createDir: function () {
            var self = this;
            if (self.newDir.name == '') {
                self.logWarn('目录不能为空')
                return;
            }
            self.wetoolFS.createDir(
                self.currentDir, self.newDir.name,
                function (status, data) {
                    if (status == 200) {
                        self.logInfo('目录创建成功');
                        self.refreshChildren();
                    } else {
                        self.logError(`目录创建失败, ${status}, ${data.error}`, autoHideDelay = 5000)
                    }
                    self.newDir = { name: '' }
                },
                function () {
                    self.logError('请求失败');
                }
            )
        },
        uploadFiles: function(files){
            var self = this;
            if (files.length == 0) { return };
            self.logInfo(`准备上传 ${files.length} 个文件`);
            for (let index = 0; index < files.length; index++) {
                const file = files[index];
                const progress = {file: file.name, loaded: 0, total: 100};
                self.uploadQueue.tasks.push(progress);
    
                self.wetoolFS.uploadFile(
                    self.currentDir, file,
                    function (status, data) {
                        if (status != 200) {
                            self.logError(`文件上传失败, ${status}, ${data.error}`, autoHideDelay = 5000)
                        }
                        self.uploadQueue.completed += 1;
                    },
                    function () { self.logError('请求失败') },
                    function (loaded, total) {
                        progress.loaded = loaded;
                        progress.total = total;
                    }
                )
            }
        },
        uploadFile: function () {
            var form = document.forms["formFileUpload"];
            this.uploadFiles(form.inputUploadFile.files);
        },
        uploadDir: function () {
            var form = document.forms["formDirUpload"];
            this.uploadFiles(form.inputUploadDir.files);
        },
        showFileModal: function (item) {
            var self = this;
            self.wetoolFS.getFileContent(
                self.currentDir, item.name,
                function (status, data) {
                    if (status == 200) {
                        self.fileEditor = data.file;
                    } else {
                        self.logError(`文件内容获取失败, ${status}, ${data.error}`, autoHideDelay = 5000)
                    }
                    self.newDir = { name: '' }
                },
                function () {
                    self.logError('请求失败');
                }
            )
        },
        updateFile: function () {
            this.logError('文件修改功能未实现');
        }
    },
    created: function () {
        this.changeDirectory('', pushHistory = true);
    }
});
