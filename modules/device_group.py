# -*- mode: python; python-indent: 4 -*-
__author__ = "@alfsando"
__version__ = "1.0.0"
__status__ = "Release"

import uuid
import xml.etree.ElementTree as ET
from typing import List, Union
from modules.device import Device
from modules.restconf_connector import RESTCONF_Connector

def log_action(function):
    """Decorator for logging in default stdout the function being executed
    """
    def wrapper_log_action(*args, **kwargs):
        print(f'-> ({str(*args)}) {function.__name__} started ...')
        result = function(*args, **kwargs)
        print(f'-> ({str(*args)}) {function.__name__} done!')
        return result
    return wrapper_log_action

class DeviceGroup():
    def __init__(self, nso_cnx:RESTCONF_Connector, devices:List[Device]) -> None:
        """DeviceGroup class

        Args:
            nso_cnx (RESTCONF_Connector): Staging NSO connector instance
            devices (List[Device]): List of Device class instances
        """
        self.nso_cnx = nso_cnx
        self.name = str(uuid.uuid4().hex)[:8]
        self.devices = devices
        self._create_dummy_device_group()
        
    def __repr__(self) -> str:
        """Printing of this Device group

        Returns:
            str: device group name
        """
        return self.name
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._delete_dummy_device_group()
        
    def _get_device(self, device_name: str) -> Union[Device,None]:
        """Fetches the provided hostname within the internal list of Device instances

        Args:
            device_name (str): Device instance hostname parameter

        Returns:
            Union[Device,None]: Matching Device instance. None in case it is not found
        """
        for device in self.devices:
            if device_name == device.hostname:
                return device
        return None
        
    @log_action    
    def _create_dummy_device_group(self) -> None:
        """Creation of this dummy Device Group on the staging NSO server using RESTCONF
        """
        dummy_group_payload = f'''
        <device-group>
            <name>{self.name}</name>
            PLACEHOLDER
        </device-group>
        '''
        device_group_components = ''
        for device in self.devices:
            device_group_components += f'<device-name>{device}</device-name>'
        dummy_group_payload = dummy_group_payload.replace('PLACEHOLDER',device_group_components)
        self.nso_cnx.restconf_send(
            method='POST',
            url='data/tailf-ncs:devices',
            payload=dummy_group_payload
        )
        
    @log_action
    def _delete_dummy_device_group(self) -> None:
        """Deletion of this dummy Device Group on the staging NSO server using RESTCONF
        """
        self.nso_cnx.restconf_send(
            method='DELETE',
            url=f'data/tailf-ncs:devices/device-group={self.name}'
        )
        
    @log_action
    def sync_from_device_group(self) -> Union[List[Device],List[Device]]:
        """Execution of a sync-from of this dummy Device Group on the staging NSO server using RESTCONF

        Returns:
            Union[List[Device],List[Device]]: List of synced devices, list of unsynced devices
        """
        synced_devices = []
        unsynced_devices = []
        result = self.nso_cnx.restconf_send(
            method='POST',
            url=f'data/tailf-ncs:devices/device-group={self.name}/sync-from'
        )
        result_parse = ET.ElementTree(ET.fromstring(result))
        root = result_parse.getroot()
        for child in root:
            synced_devices.append(self._get_device(child[0].text)) if child[1].text == 'true' else unsynced_devices.append(self._get_device(child[0].text))
        return synced_devices, unsynced_devices