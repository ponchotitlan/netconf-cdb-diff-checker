# -*- mode: python; python-indent: 4 -*-
__author__ = "@alfsando"
__version__ = "1.0.0"
__status__ = "Release"

import yaml, argparse
from yaml.loader import SafeLoader
from modules.restconf_connector import RESTCONF_Connector
from modules.device import Device
from modules.device_group import DeviceGroup

def nso_diff_mode(address:str, port:int, token:str, inventory:dict, nso_only:bool):
    """Extraction of NETCONF and NSO configs from the devices in the inventory file.
    A diff report is generated and dumped in the root directory.

    Args:
        address (str): NSO IP address
        port (int): NSO http/s port
        token (str): NSO RESTCONF connection token
        inventory (dict): inventory.yaml dict with the elements from 'staging-devices'
        nso_only (bool): Only do NSO CDB extraction and reporting. No NETCONF nor diff reporting
    """
    # Creation of an NSO connector to the staging server
    nso_connector = RESTCONF_Connector(
        address= address,
        port= port,
        token= token
    )
    # Processing of every device within the yaml file
    target_devices = []
    for device_inv in inventory:
        target_devices.append(Device(
            inventory=device_inv,
            nso_cnx=nso_connector
        ))
    # Check sync of devices using a dummy device group
    with DeviceGroup(nso_connector,target_devices) as dummy_device_group:
        synced_devices, unsynced_devices = dummy_device_group.sync_from_device_group()
        if len(unsynced_devices) > 0:
            print(f'--> The following devices are not valid for delta anaylsis: {unsynced_devices}')
        # Processing delta of synced devices
        for valid_device in synced_devices:
            valid_device.extract_CDB()
            # Diff (default) mode
            if not nso_only:
                valid_device.extract_NETCONF()
                print(f'!!! Report file available -> ({valid_device.diff_calculation()})')
            
def netconf_mode(inventory:dict):
    """Extraction of NETCONF configs from the devices in the inventory file.
    A report is generated and dumped in the root directory.

    Args:
        inventory (dict): inventory.yaml dict with the elements from 'staging-devices'
    """
    for device_inv in inventory:
        Device(
            inventory=device_inv
        ).extract_NETCONF()

def main():
    # Operational mode parsing
    parser = argparse.ArgumentParser(
        description= "Configuration diff checker - NSO CDB vs device NETCONF."
    )
    parser.add_argument(
        '-netconf', '-netconf', required=False, action='store_true', help='Just extract the NETCONF settings from all the devices in the inventory.yaml file. NSO is not required. No diff report is rendered.'
    )
    parser.add_argument(
        '-nso', '-nso', required=False, action='store_true', help='Just extract the CDB configs from all the devices in the inventory.yaml file. NSO staging server is required. No diff report is rendered.'
    )
    
    # Extraction execution
    with open('inventory.yaml') as f:
        inventory = yaml.load(f, Loader=SafeLoader)
        args = parser.parse_args()
        if args.netconf:
            netconf_mode(
                inventory= inventory['staging-devices']
            )
            return
        nso_diff_mode(
            address= inventory['staging-nso']['address'],
            port= inventory['staging-nso']['port'],
            token= inventory['staging-nso']['token'],
            inventory= inventory['staging-devices'],
            nso_only= args.nso
        )
    
if __name__ == '__main__':
    main()