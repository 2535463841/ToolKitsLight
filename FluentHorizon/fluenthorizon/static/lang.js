var DIRECOTRY = {
    ok: { en: 'ok', zh: '确定' },
    cancel: { en: 'Cancel', zh: '取消' },

    lang: { en: 'Language', zh: '语言' },
    en: { en: 'English', zh: '英文' },
    zh: { en: 'Chinese', zh: '中文' },

    user: { en: 'User', zh: '用户' },
    setting: { en: 'setting', zh: '设置' },
    signOut: { en: 'sing out', zh: '注销' },

    fileUploadProgress: { en: 'File upload progress', zh: '文件上传进度' },

    scanLink: { en: 'Scan to connect ', zh: '扫一扫连接' },
    scanUsePhoneBrower: { en: 'Please use the mobile browser to scan', zh: '请使用手机浏览器扫一扫' },
    search: { en: 'search', zh: '搜索' },

    uploadFiles: { en: 'upload files', zh: '上传文件' },
    uploadDir: { en: 'upload directory', zh: '上传目录' },
    newFile: { en: 'create file', zh: '新建文件' },
    newDir: { en: 'create dirctory', zh: '新建目录' },

    delete: { en: 'delete', zh: '删除' },
    rename: { en: 'rename', zh: '重命名' },
    view: { en: 'view', zh: '预览' },
    displayDownloadQRCode: { en: 'Display Download QR code ', zh: '显示下载二维码' },
    download: {en: 'download', zh: '下载'},

    file: { en: 'file', zh: '文件' },
    size: { en: 'size', zh: '大小' },
    modifyTime: { en: 'modify time', zh: '修改时间' },
    operation: { en: 'operation', zh: '操作' },
    displayAll: { en: 'display all ', zh: '显示全部' },

    root: { en: 'roog', zh: '根目录' },
    back: { en: 'back', zh: '返回' },
    refresh: { en: 'refresh', zh: '刷新' },

    filename: { en: 'roog', zh: '根目录' },
    newFilename: { en: 'new file name', zh: '新文件名' },
    pleaseInputFileName: { en: 'please input file name', zh: '请输入新文件名' },

    pleaseInput: { en: 'please input ...', zh: '请输入...' },
    createDirsTips: { en: 'Use / to create multi-level directories, such as foo/bar ', zh: '使用 / 创建多层目录，例如 foo/bar' },
    diskUsage: {en: 'disk usage', zh: '磁盘空间'},

    oldPassword: {en: 'old password', zh: '旧密码'},
    newPassword: {en: 'new password', zh: '新密码'},

    service: {en: 'service ', zh: '服务'},
    serviceEndpoint: {en: 'service endpoint', zh: '服务端点'},
    apiAccess: {en: 'api access ', zh: '访问API'},
    viewCredentials: {en: 'view credentials', zh: '查看凭据'},
    downloadOpenstackRcFile: {en: 'download openstack rc file', zh: '下载openstackRC文件'},

    instances: {en: 'instances', zh: '实例'},

    images: {en: 'images', zh: '镜像'},
    createImage: {en: 'delete image', zh: '创建镜像'},
    owner: {en: 'owner', zh: '拥有者'},
    name: {en: 'name', zh: '名字'},
    type: {en: 'type', zh: '类型'},
    status: {en: 'status', zh: '状态'},
    visibility: {en: 'visibility', zh: '可见'},
    protected: {en: 'protected', zh: '保护'},
    diskFormat: {en: 'disk format', zh: '磁盘格式'},
    action: {en: 'action', zh: '操作'},
    actions: {en: 'action', zh: '操作'},
    flavors: {en: 'flavors', zh: '规格'},
    createFlavor: {en: 'create flavor', zh: '新建规格'},
    deleteFlavor: {en: 'delete flavor', zh: '删除规格'},
    updateMetadata: {en: 'update metadata', zh: '更新元数据'},

    keypairs: {en: 'keypairs', zh: '密钥对'},
    createKeypair: {en: 'create keypair', zh: '新建keypair'},
    deleteKeypair: {en: 'delete keypair', zh: '删除keypair'},
    deleteKeypairs: {en: 'delete keypair', zh: '删除keypair'},
    importPublicKey: {en: 'import public key', zh: '导入公钥'},

    CPU: {en: 'CPU', zh: 'CPU'},
    RAM: {en: 'RAM', zh: '内存'},
    fip: {en: 'floating ip', zh: '浮动IP'},
    sg: {en: 'security group', zh: 'CPU'},

    overreview: {en: 'overreview', zh: '概览'},
    hypervisors: {en: 'hypervisors', zh: '虚拟化'},
    limitSumary: {en: 'Limit Sumary', zh: '配额摘要'},
    deleteKeyPair: {en: 'Delete Key Pair', zh: '删除密钥对'},
    deleteKeyPairs: {en: 'Delete Key Pairs', zh: '删除密钥对'},

};
var SUPPORT_LANG = ['en', 'zh'];

function getUserSettedLang() {
    const cookies = document.cookie.split(';');
    for (let index = 0; index < cookies.length; index++) {
        const config = cookies[index].split('=');
        if (config[0].trim() == 'language') {
            return config[1].trim();
        }
    }
    return null;
}

function getDispalyLang() {
    let useLang = getUserSettedLang();
    if (useLang != null && SUPPORT_LANG.indexOf(useLang) >= 0) { return useLang; }
    useLang = navigator.language || navigator.userLanguage;
    if (SUPPORT_LANG.indexOf(useLang) >= 0) { return useLang; }
    useLang = useLang.split('-')[0];
    if (SUPPORT_LANG.indexOf(useLang) >= 0) { return useLang; }
    return 'en';
}


function setDisplayLang(language) {
    document.cookie = `language=${language}`;
}


var USE_LANG = getDispalyLang();

var translate = function (content) {
    if (!DIRECOTRY.hasOwnProperty(content)) {
        return content;
    }
    return DIRECOTRY[content][USE_LANG];
}

