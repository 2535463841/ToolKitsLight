

var app = new Vue({
    el: '#app',
    data: {
        name: 'identity',
        wetoolFS: new WetoolFS(),
        debug: true,
        itemNumsList: [10, 20, 30, 40, 50],
        logLinesList: [50, 60, 80, 100],
        itemsSelected: 30,
        linesSelected: 50,
        intervalId: null,
        failedTimes: 0,
        resources: {projects: [], users: [], groups: [], roles: []},
        auth: {},
        logger: null,
        checked: false,
    },
    methods: {
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
                        self.logger.error(`list ${resource_name} failed,  ${status}, ${data.error}`)
                        self.failedTimes += 1;
                    }
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
                        self.logger.error('get auth info failed')
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
        }
    },
    mounted: function() {
        this.logger = new LOGGER(this.$bvToast);
        this.getAuthInfo();
        this.listResource('projects');
        this.listResource('users');
        this.listResource('groups');
        this.listResource('roles');

    }
});
