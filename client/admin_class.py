#!/bin/python3
import base64
import logging

import yaml

from client import (
    DISTRIBUTERS_TABLE,
    MANUFACTURERS_TABLE,
    PHARMACY_TABLE,
    getDistributerAddress,
    getManufacturerAddress,
    getPharmacyAddress,
    send_to_rest_api,
    wrap_and_send,
)


class admin():
    def __init__(self):
        pass

    def addManufacturer(self, manufacturer_name):
        logging.info('addManufacturer %s', manufacturer_name)
        input_address_list = [MANUFACTURERS_TABLE]
        output_address_list = [MANUFACTURERS_TABLE,
                               getManufacturerAddress(manufacturer_name)]
        response = wrap_and_send(
            "addManufacturer", manufacturer_name, input_address_list, output_address_list, wait=5)
        print("manufacture response: ", response)
        return yaml.safe_load(response)['data'][0]['status']

    def addDistributer(self, distributer_name):
        logging.info('addDistributer %s', distributer_name)
        dist_has_address = getDistributerAddress(distributer_name, "has")
        dist_req_address = getDistributerAddress(distributer_name, "request")
        input_address_list = [DISTRIBUTERS_TABLE]
        output_address_list = [DISTRIBUTERS_TABLE,
                               dist_has_address, dist_req_address]
        response = wrap_and_send(
            "addDistributor", distributer_name, input_address_list, output_address_list, wait=5)
        print("manufacture response: ", response)
        return yaml.safe_load(response)['data'][0]['status']

    def addPharmacy(self, pharmacy_name):
        logging.info('addPharmacy %s', pharmacy_name)
        pharmacy_req_address = getPharmacyAddress(pharmacy_name, "request")
        Pharmacy_has_address = getPharmacyAddress(pharmacy_name, "has")
        input_address_list = [PHARMACY_TABLE]
        output_address_list = [PHARMACY_TABLE,
                               Pharmacy_has_address, pharmacy_req_address]
        response = wrap_and_send(
            "addPharmacy", pharmacy_name, input_address_list, output_address_list, wait=5)
        return yaml.safe_load(response)['data'][0]['status']

    def listClients(self, client_address):
        print("Listing clients: ", client_address)
        result = send_to_rest_api(f"state/{client_address}")
        print("Results: ", result)
        try:
            return (base64.b64decode(yaml.safe_load(result)["data"])).decode()
        except BaseException:
            return None

    def listPharmacies(self):
        return self.listClients(PHARMACY_TABLE)

    def listDistributers(self):
        return self.listClients(DISTRIBUTERS_TABLE)

    def listManufacturers(self):
        return self.listClients(MANUFACTURERS_TABLE)
