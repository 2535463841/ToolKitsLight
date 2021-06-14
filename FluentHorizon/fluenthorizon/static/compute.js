

var app = new Vue({
    el: '#app',
    data: {
        name: 'compute',
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
        timeZones: ['UTC', 'US', 'ZH'],
        tzSelected: 'UTC',
        itemNumsList: [10, 20, 30, 40, 50],
        logLinesList: [50, 60, 80, 100],
        itemsSelected: 30,
        linesSelected: 50,
        intervalId: null,
        failedTimes: 0,
        usageStart: 0,
        usageEnd: 0,
        display: 'overreview',
        menuTree: ['overreview', 'instances', 'hypervisors', 'images', 'flavors'],
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
            ports: [], routers: [],
            hypervisors: [],
            servers: [], images: [], flavors: [], keypairs: [],
            quotas: {},
            floatingips: [], security_groups: []
        },
        usage: {
            memory: {used: 0, total: 0},
        },
        auth: {},
        instanceQuota: new ChartPieUsed('instancesQuota', translate('instances')),
        vcpuQuota: new ChartPieUsed('vcpuQuota', translate('CPU')),
        ramQuota: new ChartPieUsed('ramQuota', translate('RAM')),
        fipQuota: new ChartPieUsed('fipQuota', translate('fip')),
        sgQuota: new ChartPieUsed('sgQuota', translate('sg')),
        usedCpu: 0,
        usedRam: 0,
        usage: {server_usages: []}
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

        changeDisplay: function(name) {
            this.display = name;
            if (this.display != 'overreview'){
                this.instanceQuota.reset();
                this.vcpuQuota.reset();
                this.ramQuota.reset();
                this.fipQuota.reset();
                this.sgQuota.reset();
            }
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
        listResource: function(resource_name){
            var self = this;
            this.wetoolFS.postAction(
                {'name': `list_${resource_name}`},
                function(status, data){
                    if(status == 200){
                        self.resources[resource_name] = data[resource_name];
                        if (resource_name == 'hypervisors'){
                            self.usage['memory'] = {used: 0, total: 0}
                            self.resources[resource_name].forEach(function(item) {
                                self.usage['memory']['used'] += item.memory_mb_used;
                                self.usage['memory']['total'] += item.memory_mb;
                            });
                        }else if(resource_name == 'servers'){
                            let usedCpu = 0;
                            let usedRam = 0;
                            self.resources[resource_name].forEach(function(item) {
                                usedCpu += item.flavor.vcpus;
                                usedRam += item.flavor.ram;
                            });
                            self.usedCpu = usedCpu;
                            self.usedRam = usedRam;
                        }
                    }else{
                        self.logError(`list ${resource_name} failed,  ${status}, ${data.error}`)
                        self.failedTimes += 1;
                    }
                    // self.draw();
                }
            )
        },
        showChartPieUsed: function(eleId, title, data){
            var chart = echarts.init(document.getElementById(eleId));
            chart.setOption({
                title: {text: title, left: 'center'},
                tooltip: {trigger: 'item'},
                series: [{
                    name: title, type: 'pie', radius: '50%',
                    color:['rgb(215, 102, 98)', 'rgb(206, 206, 206)'],
                    data: data,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'}
                    }},
                ]
            });
        },
        getAuthInfo: function(){
            var self = this;
            this.wetoolFS.postAction(
                {'name': 'get_auth_info'},
                function(status, data){
                    if(status == 200){
                        self.auth = data.auth;
                    }else{
                        self.logError('get auth info failed')
                    }
                }
            );
        },
        getPublicEndpoint: function(service_id){
            for(var i = 0; i < this.resources.endpoints.length; i++){
                let endpoint = this.resources.endpoints[i];
                if (endpoint.service_id == service_id && endpoint.interface == 'public'){
                    return endpoint
                }
            }
        },
        draw: function(){
            this.instanceQuota.refresh({
                'Used': this.resources.servers.length,
                'Avalialble': this.resources.quotas.instances - this.resources.servers.length});

            let usedCpu = 0, usedRam = 0;
            this.resources['servers'].forEach(function(item) {
                usedCpu += item.flavor.vcpus;
                usedRam += item.flavor.ram;
            });
            this.vcpuQuota.refresh({
                'Used': usedCpu,
                'Avalialble': this.resources.quotas.cores - usedCpu});
            this.ramQuota.refresh({
                'Used': usedRam,
                'Avalialble': this.resources.quotas.ram - usedRam});

            this.fipQuota.refresh({
                'Used': this.resources.floatingips.length,
                'Avalialble': this.resources.quotas.floating_ips - this.resources.floatingips.length});
            this.sgQuota.refresh({
                'Used': this.resources.security_groups.length,
                'Avalialble': this.resources.quotas.security_groups - this.resources.security_groups.length});
        },
        getImage: function(image_id){
            for(let i=0; i< this.resources.images; i++ ){
                let image = this.resources.images[i];
                if (image.id == image_id){
                    return image
                }
            }
            return {}
        },
        doAction: function(action, params, callback){
            this.wetoolFS.postAction(
                {'name': action, params: params},
                function(status, data){
                    if(status == 200){
                        callback(data)
                    }else{
                        self.logError(`do action ${action} failed.`)
                    }
                })
        },
        showUsages: function(){
            var self = this;
            this.logInfo(`usageStart = ${this.usageStart}, usageEnd = ${this.usageEnd}`);
            if (this.usageStart == 0 || this.usageEnd == 0){
                return;
            }
            this.doAction('show_usages', {start: this.usageStart, end: this.usageEnd}, function(data){
                self.usage = data.usage;
            })
        }
    },
    mounted: function() {
        this.getAuthInfo();
        this.listResource('services');
        this.listResource('endpoints');
        this.listResource('users');
        this.listResource('projects');
        this.listResource('keypairs');
        this.listResource('quotas');
        this.listResource('images');
        this.listResource('flavors');
        this.listResource('servers');
        this.listResource('hypervisors');
        var self = this;

        this.doAction('show_usages', {}, function(data){
            self.usage = data.usage;
        })
        // this.listResource('usages');
        var self = this;

        self.intervalId = setInterval(function(){
            // self.listResource('hypervisors');
            self.listResource('servers');
            if(self.failedTimes >= 3){
                self.logError(`list resources failed ${self.failedTimes}, stop ${self.intervalId}`);
                clearInterval(self.intervalId);
            }
        }, 5000);

        setInterval(function(){self.draw();}, 2000);
    }
});
