
osType=''
grep -i ubuntu /etc/os-release > /dev/null
if [[ $? -eq 0 ]]; then
    osType="ubuntu"
fi
if [[ -z "${osType}" ]]; then
    grep -i centos /etc/os-release > /dev/null
    if [[ $? -eq 0 ]]; then
        osType="centos"
    fi
fi

if [[ -z "${osType}" ]]; then
    echo "ERROR:" "OS is unknown"
    exit 1
fi

echo "INFO:" "OS is ${osType}"

echo "INFO:" "Install python dev"
case ${osType} in
    ubuntu)
        apt autoremove;
        apt-get install python-dev || exit 1
        ;;
    centos)
        yum install -y python-dev || exit 1
        ;;
    *)
        ;;
esac

for component in FluentCore FluentBingImg FluentHttpFS
do
    cd ${component}
    echo "INFO:" "======= Install $component ======"
    if [[ -f requirements.txt ]]; then
        echo pip3 install -r requirements.txt
        pip3 install -r requirements.txt > /dev/null
    fi
    python3 setup.py install > /dev/null || exit 1
    cd ../
done
