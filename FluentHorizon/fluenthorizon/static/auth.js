var app = new Vue({
    el: '#app',
    data: {
        name: 'auth',
        showAll: false,
        wetoolFS: new WetoolFS(),
        debug: true,
        itemNumsList: [10, 20, 30, 40, 50],
        logLinesList: [50, 60, 80, 100],
        itemsSelected: 30,
        resources: {services: [], endpoints: []},
        auth: {},
        logger: null,
    },
    methods: {
        listResource: function(resource_name){
            var self = this;
            this.wetoolFS.postAction(
                {'name': `list_${resource_name}`},
                function(status, data){
                    if(status == 200){
                        self.resources[resource_name] = data[resource_name];
                    }else{
                        self.logger.error(`list ${resource_name} failed,  ${status}, ${data.error}`)
                        self.failedTimes += 1;
                    }
                }
            )
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
    },
    mounted: function() {
        console.log(this.$bvToast)
        this.logger = new LOGGER(this.$bvToast);
        this.getAuthInfo();
        this.logger.info('sed request ...')
        this.listResource('services');
        this.listResource('endpoints');
    }
});
