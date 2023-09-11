# -*- mode: python; python-indent: 4 -*-
__author__ = "@alfsando"
__version__ = "1.0.0"
__status__ = "Release"

import requests

class RESTCONF_Connector():
    """This class is a handler for NSO restconf interactions.
    The staging devices must be already loaded in this NSO node along with their corresponding NEDs.
    """
    def __init__(self, address:str, port:int, token:str) -> None:
        """Staging NSO parameters 

        Args:
            address (str): Staging NSO IP address
            port (int): Staging NSO RESTCONF port
            token (str): RESTCONF connection auth token
        """
        self.HEADERS = {
            'Content-Type': 'application/yang-data+xml', 
            'Accept': 'application/yang-data+xml', 
            'Authorization': f'Basic {token}'
        }
        self.address = address
        self.port = port
        self.BASE_URL = f'http://{self.address}:{self.port}/restconf/'
    
    def restconf_send(self, url:str, method:str, payload:str=None) -> str:
        """Issues a RESTCONF calling to the staging NSO server using the parameters provided.
        The result is handled back in XML encoding.

        Args:
            url (str): Endpoint to query (provide the segment after http://{address}:{port}/restconf/)
            method (str): GET/POST/DELETE supported
            payload (str): Request body in XML format. Defaults to None

        Returns:
            str: Result of the RESTCONF operation in XML format
        """
        if method.upper() in ['GET','POST','DELETE']:
            restconf_result = requests.request(
                method=method,
                url=f'{self.BASE_URL}{url}',
                headers=self.HEADERS
            ) if payload is None else requests.request(
                method=method,
                url=f'{self.BASE_URL}{url}',
                headers=self.HEADERS,
                data=payload
            )
            if restconf_result.status_code not in [200,204,201]:
                error_payload = str(restconf_result.content).replace('\\n','\n')
                raise Exception(f"\nERROR: {error_payload} ... \nURL: {self.BASE_URL}{url}\n")
            return str(restconf_result.content.decode('utf-8')).replace('\\n','\n')
        raise Exception('ERROR: RESTCONF operation not supported ...')