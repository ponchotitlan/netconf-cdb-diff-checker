# -*- mode: python; python-indent: 4 -*-
__author__ = "@alfsando"
__version__ = "1.0.0"
__status__ = "Release"

import datetime
from difflib import HtmlDiff
from ncclient import manager
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

class Device():
    def __init__(self, inventory:dict, nso_cnx:RESTCONF_Connector=None) -> None:
        """Device class

        Args:
            inventory (dict): Inventory dict format from yaml file: {hostname, device_type, version, address, username, password}
            nso_cnx (RESTCONF_Connector): Staging NSO connector instance. This is optional (for NETCONF mode)
        """
        try:
            self.hostname = inventory['hostname']
            self.device_type = inventory['device_type']
            self.version = inventory['version']
            self.address = inventory['address']
            self.username = inventory['username']
            self.password = inventory['password']
            self.nso_cnx = nso_cnx
            self.netconf_config = ''
            self.cdb_config = ''
        except Exception():
            print('ERROR: inventory dict format is: {hostname, device_type, version, address, username, password}')
                
    def __repr__(self) -> str:
        """Printing of this Device instance

        Returns:
            str: hostname - device_type
        """
        return f'{self.hostname} - {self.device_type}'
    
    def __str__(self) -> str:
        """String representation of this Device instance

        Returns:
            str: hostname
        """
        return self.hostname
    
    @log_action          
    def extract_NETCONF(self) -> str:
        """Extraction of 'running' config via NETCONF from the staging device.
        The result is a xml encoded string.

        Returns:
            str: Config in XML format
        """
        try:
            with manager.connect(
                host=self.address,
                port="830",
                username=self.username,
                password=self.password,
                hostkey_verify=False,
                device_params={'name':self.device_type}) as m:
                    self.netconf_config = m.get_config(source='running').data_xml
                    self._log_payload(self.netconf_config,'NETCONF','xml')
        except Exception as exception:
            return f'ERROR: {str(exception)}'
    
    @log_action
    def extract_CDB(self) -> str:
        """RESTCONF query to the staging NSO server for retrieving the CDB config associated to this device.
        Resulting config is XML encoded.

        Returns:
            str: XML encoded device config from CDB
            
        Raises:
            exception: RESTCONF GET didn't return OK
        """
        self.cdb_config = self.nso_cnx.restconf_send(
            url=f'data/tailf-ncs:devices/device={self.hostname}?content=config',
            method='GET'
        )
        self._log_payload(self.cdb_config,'CDB','xml')

    def _log_payload(self, payload:str,filename:str,extension:str) -> None:
        """Writes a log file in the local directory with the specified payload.
        The name of the final file will be the following: <filename>_<datetime>.<extension>

        Args:
            payload (str): Content to write in the file
            filename (str): Name of the file
            extension (str): Extension of the file
        """
        with open(f'reports/{filename}_{str(self.hostname).replace(".","_")}_{self.device_type}_{self.version}_{datetime.datetime.now().strftime("%m_%d_%Y__%H_%M_%S")}.{extension}','w') as file:
            file.write(payload)
   
    @log_action
    def diff_calculation(self) -> str:
        """Generates a HTML file with formatted diff between the retrieved payloads.
        The NETCONF payload is contrasted against the CDB payload.

        Returns:
            str: Route of the generated HTML report
        """
        d = HtmlDiff(wrapcolumn=10)
        difference = d.make_file(self.netconf_config,self.cdb_config)
        report_name = f'reports/DIFF_{self.hostname}_{self.device_type}_{self.version}_{datetime.datetime.now().strftime("%m_%d_%Y__%H_%M_%S")}.html'
        with open(report_name, "w") as f:
            for line in difference.splitlines():
                print (line, file=f)
        return report_name