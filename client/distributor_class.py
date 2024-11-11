#!/bin/python3
import pandas as pd
import yaml

from client import (
    DISTRIBUTERS_TABLE,
    MANUFACTURERS_TABLE,
    PHARMACY_TABLE,
    getBatchAddress,
    getDistributerAddress,
    getManufacturerAddress,
    getPharmacyAddress,
    listClients,
    wrap_and_send,
    wrap_and_send_v1,
)


class distributer():
    def __init__(self):
        pass

    def getFromManufacturer(self, manufacturer_name, distributer, batchID, date, action):
        l = [manufacturer_name, distributer, batchID, date, action]
        command_string = ','.join(l)
        distributer_req_address = getDistributerAddress(distributer, "request")
        distributer_address = getDistributerAddress(distributer, "has")
        manufacturer_address = getManufacturerAddress(manufacturer_name)
        batch_address = getBatchAddress(batchID)
        input_address_list = [DISTRIBUTERS_TABLE, MANUFACTURERS_TABLE,
                              manufacturer_address, distributer_address, distributer_req_address, batch_address]
        output_address_list = [
            manufacturer_address, distributer_address, distributer_req_address, batch_address]
        response = wrap_and_send(
            "getFromManufacturer", command_string, input_address_list, output_address_list, wait=5)
        return yaml.safe_load(response)['data'][0]['status']

    def giveToPharmacy(self, distributer, pharmacy, batchID, date):
        l = [distributer, pharmacy, batchID, date]
        command_string = ','.join(l)
        distributer_address = getDistributerAddress(distributer, "has")
        pharmacy_address = getPharmacyAddress(pharmacy, "request")
        batch_address = getBatchAddress(batchID)
        input_address_list = [DISTRIBUTERS_TABLE, PHARMACY_TABLE,
                              pharmacy_address, distributer_address, batch_address]
        output_address_list = [pharmacy_address,
                               distributer_address, batch_address]
        response = wrap_and_send(
            "giveToPharmacy", command_string, input_address_list, output_address_list, wait=5)
        return yaml.safe_load(response)['data'][0]['status']

    def listMedicines(self, distributerName, qualifier='has'):
        address = getDistributerAddress(distributerName, qualifier)
        result = listClients(address)
        if result:
            list_add = list(dict.fromkeys(result.split(",")))
            data = [listClients(getBatchAddress(i)) for i in list_add]
            medicines = [item.split(',')[3].strip() for item in data]
            df = pd.DataFrame({'Medicines': medicines, 'Batch id': list_add})
            return df
        else:
            return None

    def listMedicines_v1(self, distributerName, qualifier='has'):
        address = getDistributerAddress(distributerName, qualifier)
        result = listClients(address)
        if result:
            list_add = list(dict.fromkeys(result.split(",")))
            data = [listClients(getBatchAddress(i)) for i in list_add]
            medicines = [item.split(',')[2].strip() for item in data]
            df = pd.DataFrame({'Medicines': medicines, 'Batch id': list_add})
            return df
        else:
            return None
