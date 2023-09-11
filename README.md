# NSO config diff checker
NETCONF vs CDB configuration delta reporter for devices on a staging NSO server

## Pre-requisites
On a virtual environment install the required python libraries
```
pip -r install requirements.txt
```

For each target device an object of the following type needs to be populated:
```
staging-devices:
  - hostname: '<same name as device in NSO in case the script is used in "nso" mode. Irrelevant for "netconf" mode>'
    device_type: '| 'huawei' | 'iosxr' | 'junos' |'
    version: '<version (just for report name purposes)>'
    address: '<device_ip>'
    username: '<SSH_device_username>'
    password: '<SSH_device_password>'
```

## Usage
### NETCONF mode
Execute the script with the following command:
```
python config_diff_ckecher.py --netconf
```

The output will be the following depending on your devices within the ```inventory.yaml``` file:
```
% python config_diff_check.py 
-> (junos224) extract_NETCONF started ...
-> (junos224) extract_NETCONF done!
```

A report entitled ```reports/NETCONF_{hostname}_{device_type}_{version}_{datetime}.xml``` will be generated afterwards.

### NSO mode
The first object within the file ```inventory.yaml``` must be populated with the connection details to your NSO staging server:
```
staging-nso:
  address: '127.0.0.1'
  port: '8080'
  token: 'bnNvYWRtaW46QXV0MG1hdDMh'
```

The **NSO staging server** should have the target devices already onboarded and connection should be feasible (authentication, SSH host-keys).

The NSO staging server must also have ```RESTCONF``` enabled.

Execute the script with the following command:
```
python config_diff_ckecher.py --nso
```

The output will be the following depending on your devices within the ```inventory.yaml``` file:
```
% python config_diff_check.py 
-> (4ad02c06) _create_dummy_device_group started ...
-> (4ad02c06) _create_dummy_device_group done!
-> (4ad02c06) sync_from_device_group started ...
-> (4ad02c06) sync_from_device_group done!
-> (junos224) extract_CDB started ...
-> (junos224) extract_CDB done!
-> (4ad02c06) _delete_dummy_device_group started ...
-> (4ad02c06) _delete_dummy_device_group done!
```

The following actions will take place sequentially:
1. A dummy device group is created in the NSO staging server with all the devices within the inventory
2. The device group is synced. Any devices with a failed sync-from will not be processed further and a message will be displayed on the default stdout
3. The retrieved configs in CDB operational state are extracted and saved on a xml file under the following route: ```reports/CDB_{hostname}_{device_type}_{version}_{datetime}.xml```

## Default mode

The same prerequisites as in ```NSO mode``` must be fulfilled.

Execute the script with the following command:
```
python config_diff_ckecher.py
```
The output will be the following depending on your devices within the ```inventory.yaml``` file:
```
% python3 config_diff_check.py 
-> (4ad02c06) _create_dummy_device_group started ...
-> (4ad02c06) _create_dummy_device_group done!
-> (4ad02c06) sync_from_device_group started ...
-> (4ad02c06) sync_from_device_group done!
-> (junos224) extract_NETCONF started ...
-> (junos224) extract_NETCONF done!
-> (junos224) extract_CDB started ...
-> (junos224) extract_CDB done!
-> (junos224) diff_calculation started ...
-> (junos224) diff_calculation done!
!!! Report file available -> (reports/DIFF_junos224_junos_22.4_07_21_2023__12_11_53.html)
-> (4ad02c06) _delete_dummy_device_group started ...
-> (4ad02c06) _delete_dummy_device_group done!
```

The following actions will take place sequentially:
1. A dummy device group is created in the NSO staging server with all the devices within the inventory
2. The device group is synced. Any devices with a failed sync-from will not be processed further and a message will be displayed on the default stdout
3. The devices which were successfully synced are processed forward: the NETCONF running configurations of the device is extracted and saved on a xml file under the following route: ```reports/NETCONF_{hostname}_{device_type}_{version}_{datetime}.xml```
4. The retrieved configs in CDB operational state are extracted and saved on a xml file under the following route: ```reports/CDB_{hostname}_{device_type}_{version}_{datetime}.xml```
5. The delta between the two configurations is calculated and saved on a HTML file under the following route: ```reports/DIFF_{hostname}_{device_type}_{version}_{datetime}.html```