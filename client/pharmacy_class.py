#!/bin/python3
import yaml

from client import (
    DISTRIBUTERS_TABLE,
    PHARMACY_TABLE,
    getBatchAddress,
    getDistributerAddress,
    getPharmacyAddress,
    listClients,
    wrap_and_send,
)


class pharmacy():
    def __init__(self):
        pass

    def getFromDistributor(self, distributer, pharmacy, batchID, date, action):
        l = [distributer, pharmacy, batchID, date, action]
        command_string = ','.join(l)
        distributer_address = getDistributerAddress(distributer, "has")
        pharmacy_req_address = getPharmacyAddress(pharmacy, "request")
        pharmacy_has_address = getPharmacyAddress(pharmacy, "has")
        batch_address = getBatchAddress(batchID)
        input_address_list = [DISTRIBUTERS_TABLE, PHARMACY_TABLE,
                              pharmacy_req_address, pharmacy_has_address, distributer_address, batch_address]
        output_address_list = [distributer_address, distributer_address,
                               pharmacy_has_address, pharmacy_req_address, batch_address]
        response = wrap_and_send(
            "getFromDistributer", command_string, input_address_list, output_address_list, wait=5)
        return yaml.safe_load(response)['data'][0]['status']

    def listMedicines(self, pharmacy_name, qualifier='has'):
        address = getPharmacyAddress(pharmacy_name, qualifier)
        result = listClients(address)
        if result:
            list_add = list(dict.fromkeys(result.split(",")))
            data = [listClients(getBatchAddress(i)) for i in list_add]
            medicines = [item.split(',')[3].strip() for item in data]
            return medicines
        else:
            return "No medicines"

    def readMedicineBatch(self, batchid):
        address = getBatchAddress(batchid)
        result = listClients(address)
        if result:
            return result
        else:
            return "No such medicine batch"
