import requests

import config

class RSpaceRequest:
    """builds a request to rs"""
    def __init__(self, rsid=None, rs_api_function=None):
        self.rsid = rsid
        self.rs_api_function = rs_api_function

    self.response = get_resource_data(self.rsid, self.rs_api_function)



def get_resource_data(rsid, rs_api_function, **kwargs):
    pass
