#!/bin/python3
import json
import logging
from datetime import datetime

import pandas as pd
import requests
import yaml
from dateutil.relativedelta import relativedelta

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
    wrap_and_send_v1,
)


class manufacturer():
    def __init__(self):
        pass

    def get_bat_id(self, address):
        result = send_to_rest_api(f"state/{address}")
        result = json.loads(result)
        url = base_url + f'/blocks/{result["head"]}'
        response = requests.get(url, timeout=None)
        batch_id = response.json()['data']['header']['batch_ids'][0]
        return batch_id

    def manufacture(self, manufacturer_name, medicine_name, batch_id, manufacture_date, expiry_date, owner):
        logging.info('manufacture %s', medicine_name)
        date_product_dt = datetime.strptime(manufacture_date, '%Y-%m-%d')
        date_expire_dt = datetime.strptime(expiry_date, '%Y-%m-%d')
        date_expire_minus_2_months = date_expire_dt - relativedelta(months=2)
        today = datetime.today()
        if date_product_dt <= today and date_expire_minus_2_months >= today:
            manufacturer_address = getManufacturerAddress(manufacturer_name)
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
        else:
            return "Vui lòng kiểm tra lại ngày sản xuất và hạn sử dụng. Hạn sử dụng phải tối thiểu 2 tháng."

    def giveToDistributor(self, manufacturer_name, distributer, batch_id, date):
        distributer_address = getDistributerAddress(distributer, "request")
        manufacturer_address = getManufacturerAddress(manufacturer_name)
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
        address = getManufacturerAddress(manufacturer_name)
        result = listClients(address)
        if result:
            list_add = list(dict.fromkeys(result.split(",")))
            data = [listClients(getBatchAddress(i)) for i in list_add]
            medicines = [item.split(',')[2].strip() for item in data]
            df = pd.DataFrame({'medicines': medicines, 'batch_id': list_add})
            return df
        else:
            return None
