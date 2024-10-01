#!/bin/python3
import json
import logging

import requests
import yaml

from client import (
    DISTRIBUTERS_TABLE,
    MANUFACTURERS_TABLE,
    base_url,
    getBatchAddress,
    getDistributerAddress,
    getManufacturerAddress,
    listClients,
    send_to_rest_api,
    wrap_and_send,
)


class manufacturer():
    def __init__(self):
        pass

    def get_bat_id(self, address):
        print("Listing clients: ", address)
        result = send_to_rest_api(f"state/{address}")
        result = json.loads(result)
        url = base_url + f'/blocks/{result["head"]}'
        response = requests.get(url, timeout=None)
        batch_id = response.json()['data']['header']['batch_ids'][0]
        return batch_id

    def manufacture(self, manufacturer_name, medicine_name, batch_id, manufacture_date, expiry_date, owner):
        logging.info('manufacture %s', medicine_name)
        manufacturer_address = getManufacturerAddress(manufacturer_name)
        # batch_id = self.get_bat_id(manufacturer_address)
        l = [manufacturer_name, medicine_name,
             batch_id, manufacture_date, expiry_date]
        batch_address = getBatchAddress(batch_id)
        command_string = ','.join(l)
        input_address_list = [MANUFACTURERS_TABLE,
                              manufacturer_address, batch_address]
        output_address_list = [manufacturer_address, batch_address]

        response = wrap_and_send(
            "manufacture", command_string, input_address_list, output_address_list, wait=5)
        return yaml.safe_load(response)['data'][0]['status']

    def giveToDistributor(self, manufacturer_name, distributer, batch_id, date):
        distributer_address = getDistributerAddress(distributer, "request")
        print("distributer address: ", distributer_address)
        manufacturer_address = getManufacturerAddress(manufacturer_name)
        print("manufacturer address: ", manufacturer_address)
        # batch_id = self.get_bat_id(manufacturer_address)
        # batch_id = '40fea18aed583b3baba631492537137e8cb6754ee2a8030ccfdf0a87512d90ce5b3644605ab68942c6ce348c517cc6f76352506e6a060756a2d517234febcdbc'
        print("Manufacturer address batch id: ", batch_id)
        l = [manufacturer_name, distributer, batch_id, date]
        command_string = ','.join(l)
        batch_address = getBatchAddress(batch_id)
        input_address_list = [DISTRIBUTERS_TABLE, MANUFACTURERS_TABLE,
                              manufacturer_address, distributer_address, batch_address]
        output_address_list = [manufacturer_address,
                               distributer_address, batch_address]
        response = wrap_and_send(
            "giveToDistributer", command_string, input_address_list, output_address_list, wait=5)
        return yaml.safe_load(response)['data'][0]['status']

    def listMedicines(self, manufacturer_name):
        print("Tên nhà sản xuất thuốc: ", manufacturer_name)
        address = getManufacturerAddress(manufacturer_name)
        print("Address: ", address)
        result = listClients(address)
        if result:
            print("result: ", result)
            list_add = list(dict.fromkeys(result.split(",")))
            # print(list_add)
            # list_ = [list_add.remove(list_add[i]) for i in range(
            #     len(list_add)) if len(str(list_add[i])) == 0]
            # print("list: ", list_)
            data = [listClients(getBatchAddress(i)) for i in list_add]
            medicines = [item.split(',')[2].strip() for item in data]
            return medicines
        else:
            return "No medicines"
