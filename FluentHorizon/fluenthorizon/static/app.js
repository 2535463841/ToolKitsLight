
var app = new Vue({
    el: '#app',
    data: {
        server: {name: '', version: ''},
        children: [],
        historyPath: [],
        linkQrcode: '',
        downloadFile: {name: '', qrcode: '' },
        showAll: false,
        wetoolFS: new WetoolFS(),
        renameItem: { name: '', newName: '' },
        newDir: { name: '' },
        fileEditor: { name: '', content: '' },
        uploadProgess: { loaded: 0, total: 100 },
        uploadQueue: { completed: 0, tasks: [] },
        debug: true,
        pathItems: [],
        diskUsage: {used: 0, total: 100},
        searchPartern: '',
        searchResult: [],
        showPardir: false,
        display: 'ports',

        menuTree: {
            identity: ['projects', 'users', 'services', 'endpoints'],
            compute: ['instances', 'flavors'],
            networking: ['routers', 'networks', 'subnets', 'ports'],
            image: ['images']
        },
        users: [],
        projects: [],
        services: [],
        endpoints: [],
        
        routers: [],
        networks: [],
        subnets: [],
        ports: [],
        agents: [],
        resources: {
            'ports': [],
            'routers': [],
        },

    },
    methods: {
        logDebug: function (msg, autoHideDelay = 1000, title = 'Debug') {
            if (this.debug == false) {
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
            this.goTo(this.pathItems.length - 1);
        },
        getAbsPath: function (child) {
            if (absPath == '/') {
                absPath += child.name;
            } else {
                absPath += '/' + child.name;
            }
            return absPath;
        },
        clickPath: function (child) {
            if (child.type != "folder") {
                return
            }
            var self = this;
            let pathItems = self.getPathText(self.pathItems).concat(child.name);

            this.wetoolFS.listDir(
                pathItems, self.showAll,
                function (status, data) {
                    if (status == 200) {
                        self.pathItems.push({text: child.name, href: '#' })
                        self.children = data.dir.children;
                        self.diskUsage = data.dir.disk_usage;
                    } else {
                        self.logError(`请求失败，${status}, ${data.error}`);
                    }
                }
            );
        },
        getPathText: function(pathItems){
            let pathText = [];
            pathItems.forEach(function(item) {
                pathText.push(item.text);
            });
            return pathText;
        },
        goTo: function (clickIndex) {
            var self = this;
            self.showPardir = false;
            let pathItems = self.getPathText(getItemsBefore(self.pathItems, clickIndex));
            this.wetoolFS.listDir(
                pathItems, self.showAll,
                function (status, data) {
                    if (status == 200) {
                        delItemsAfter(self.pathItems, clickIndex);
                        self.children = data.dir.children;
                        self.diskUsage = data.dir.disk_usage;
                    } else {
                        self.logError(`请求失败，${status}, ${data.error}`);
                    }
                }
            );
        },
        showQrcode: function (child) {
            this.downloadFile = child;
        },
        getDownloadUrl: function (item) {
            let urlParams = [];
            item.pardir.forEach(function(dir) {
                urlParams.push(`path_list=${dir}`);
            });
            return `/download/${encodeURIComponent(item.name)}?${urlParams.join('&')}`
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
                self.renameItem.name, self.getPathText(self.pathItems), self.renameItem.newName,
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
        },
        showRenameModal: function (item) {
            this.renameItem = { name: item.name, newName: item.name }
        },

        showFileModal: function (item) {
            var self = this;
            self.wetoolFS.getFileContent(
                self.getPathText(self.pathItems), item.name,
                function (status, data) {
                    if (status == 200) {
                        self.fileEditor = data.file;
                    } else {
                        self.logError(`文件内容获取失败, ${status}, ${data.error}`, autoHideDelay = 5000)
                    }
                },
                function () {
                    self.logError('请求失败');
                }
            )
        },
        updateFile: function () {
            this.logError('文件修改功能未实现');
        },
        getServerInfo: function(){
            var self = this;
            this.wetoolFS.getServerInfo(
                function(status, data){
                    if (status == 200) {
                        self.server = data.server;
                    } else {
                        self.logError(`请求失败, ${status}, ${data.error}`, autoHideDelay = 5000)
                    }
                }
            );
        },
        changeDisplay: function(name) {
            this.display = name;
        },
        listUsers: function(){
            var self = this;
            this.wetoolFS.postAction(
                {'name': 'list_users'},
                function(status, data){
                    if(status == 200){
                        self.users = data.users;
                    }else{
                        self.logError('get users failed')
                    }
                }
            )
        },
        listProjects: function(){
            var self = this;
            this.wetoolFS.postAction(
                {'name': 'list_projects'},
                function(status, data){
                    if(status == 200){
                        self.projects = data.projects;
                    }else{
                        self.logError('get users failed')
                    }
                }
            )
        },
        listServices: function(){
            var self = this;
            this.wetoolFS.postAction(
                {'name': 'list_services'},
                function(status, data){
                    if(status == 200){
                        self.services = data.services;
                    }else{
                        self.logError('get services failed')
                    }
                }
            )
        },
        listEndpoints: function(){
            var self = this;
            this.wetoolFS.postAction(
                {'name': 'list_endpoints'},
                function(status, data){
                    if(status == 200){
                        self.endpoints = data.endpoints;
                    }else{
                        self.logError('get endpoints failed')
                    }
                }
            )
        },
        listResource: function(resource_name){
            var self = this;
            this.wetoolFS.postAction(
                {'name': `list_${resource_name}`},
                function(status, data){
                    if(status == 200){
                        self.resources[resource_name] = data[resource_name];
                        console.log(self.resources);
                    }else{
                        self.logError(`list ${resource_name} failed,  ${status}, ${data.error}`)
                    }
                }
            )
        },
    },
    created: function () {
        this.getServerInfo();
        this.listUsers();
        this.listProjects();
        this.listServices();
        this.listEndpoints();
        this.listResource('networks');
        this.listResource('subnets');
        // this.listResource('routers')
        this.listResource('ports');

        // this.goTo(-1);
        // this.changeDirectory('', pushHistory = true);
    }
});
