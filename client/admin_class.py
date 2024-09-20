#!/bin/python3
import psycopg2

from client import *


class admin():
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="postgres", user="postgres", password="123", host="postgres", port="5432"
        )
        self.cursor = self.conn.cursor()

    def addManufacturer(self, manufacturerName):
        logging.info('addManufacturer({})'.format(manufacturerName))
        input_address_list = [MANUFACTURERS_TABLE]
        print(input_address_list, manufacturerName, MANUFACTURERS_TABLE)
        output_address_list = [MANUFACTURERS_TABLE,
                               getManufacturerAddress(manufacturerName)]
        response = wrap_and_send(
            "addManufacturer", manufacturerName, input_address_list, output_address_list, wait=5)
        print("manufacture response: {}".format(response))
        return yaml.safe_load(response)['data'][0]['status']

    def addManufacturer_v1(self, manufacturerName):
        logging.info('addManufacturer({})'.format(manufacturerName))
        input_address_list = [MANUFACTURERS_TABLE]
        output_address_list = [MANUFACTURERS_TABLE,
                               getManufacturerAddress(manufacturerName)]
        response = wrap_and_send(
            "addManufacturer", manufacturerName, input_address_list, output_address_list, wait=5
        )

        # Lưu vào PostgreSQL
        if yaml.safe_load(response)['data'][0]['status'] == 'COMMITTED':
            self.cursor.execute(
                "INSERT INTO public.manufacturers (name, address_input, address_output) VALUES (%s, %s, %s)",
                (manufacturerName, MANUFACTURERS_TABLE,
                 getManufacturerAddress(manufacturerName))
            )
            self.conn.commit()

        return yaml.safe_load(response)['data'][0]['status']

    # def addDistributer(self, distributerName):
    #     logging.info('addDistributer({})'.format(distributerName))
    #     distHasAddress = getDistributerAddress(distributerName, "has")
    #     distReqAddress = getDistributerAddress(distributerName, "request")
    #     input_address_list = [DISTRIBUTERS_TABLE]
    #     output_address_list = [DISTRIBUTERS_TABLE,
    #                            distHasAddress, distReqAddress]
    #     response = wrap_and_send(
    #         "addDistributor", distributerName, input_address_list, output_address_list, wait=5)
    #     print("manufacture response: {}".format(response))
    #     return yaml.safe_load(response)['data'][0]['status']

    # def addPharmacy(self, PharmacyName):
    #     logging.info('addPharmacy({})'.format(PharmacyName))
    #     PharmacyReqAddress = getPharmacyAddress(PharmacyName, "request")
    #     PharmacyHasAddress = getPharmacyAddress(PharmacyName, "has")
    #     input_address_list = [PHARMACY_TABLE]
    #     output_address_list = [PHARMACY_TABLE,
    #                            PharmacyHasAddress, PharmacyReqAddress]
    #     response = wrap_and_send(
    #         "addPharmacy", PharmacyName, input_address_list, output_address_list, wait=5)
    #     # print ("manufacture response: {}".format(response))
    #     return yaml.safe_load(response)['data'][0]['status']

    def addDistributer(self, distributerName):
        logging.info('addDistributer({})'.format(distributerName))
        distHasAddress = getDistributerAddress(distributerName, "has")
        distReqAddress = getDistributerAddress(distributerName, "request")
        input_address_list = [DISTRIBUTERS_TABLE]
        output_address_list = [DISTRIBUTERS_TABLE,
                               distHasAddress, distReqAddress]
        response = wrap_and_send(
            "addDistributor", distributerName, input_address_list, output_address_list, wait=5
        )

        # Lưu vào PostgreSQL
        if yaml.safe_load(response)['data'][0]['status'] == 'COMMITTED':
            self.cursor.execute(
                "INSERT INTO public.distributers (name, has_address, req_address, address_input) VALUES (%s, %s, %s, %s)",
                (distributerName, distHasAddress,
                 distReqAddress, DISTRIBUTERS_TABLE)
            )
            self.conn.commit()

        return yaml.safe_load(response)['data'][0]['status']

    def addPharmacy(self, PharmacyName):
        logging.info('addPharmacy({})'.format(PharmacyName))
        PharmacyReqAddress = getPharmacyAddress(PharmacyName, "request")
        PharmacyHasAddress = getPharmacyAddress(PharmacyName, "has")
        input_address_list = [PHARMACY_TABLE]
        output_address_list = [PHARMACY_TABLE,
                               PharmacyHasAddress, PharmacyReqAddress]
        response = wrap_and_send(
            "addPharmacy", PharmacyName, input_address_list, output_address_list, wait=5
        )

        # Lưu vào PostgreSQL
        if yaml.safe_load(response)['data'][0]['status'] == 'COMMITTED':
            self.cursor.execute(
                "INSERT INTO public.pharmacies (name, has_address, req_address, address_input) VALUES (%s, %s, %s, %s)",
                (PharmacyName, PharmacyHasAddress,
                 PharmacyReqAddress, PHARMACY_TABLE)
            )
            self.conn.commit()

        return yaml.safe_load(response)['data'][0]['status']

    def listClients(self, clientAddress):
        print("Listing clients: ", clientAddress)
        result = send_to_rest_api("state/{}".format(clientAddress))
        print("Results: {}".format(result))
        try:
            return (base64.b64decode(yaml.safe_load(result)["data"])).decode()
        except BaseException:
            return None

    # def listPharmacies(self):
    #     return self.listClients(PHARMACY_TABLE)

    # def listDistributers(self):
    #     return self.listClients(DISTRIBUTERS_TABLE)

    # def listManufacturers(self):
    #     return self.listClients(MANUFACTURERS_TABLE)

    def listPharmacies(self):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "select distinct address_input from public.pharmacies")
            manufacturers = cursor.fetchall()
            # a = 'ae78c62c13f4e53a448da6c47b7ce87236b6f9272be81500481f35c1ec11d4de8b0fa4'
            list_address = [manufacturer[0] for manufacturer in manufacturers]
            return [self.listClients(i) for i in list_address]
        except Exception as e:
            logging.error(f"Error retrieving pharmacies: {e}")
            return None
        finally:
            self.close_connection()

    def listDistributers(self):
        logging.info('Retrieving all distributers')
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "select distinct address_input from public.distributers")
            manufacturers = cursor.fetchall()
            # a = 'ae78c62c13f4e53a448da6c47b7ce87236b6f9272be81500481f35c1ec11d4de8b0fa4'
            list_address = [manufacturer[0] for manufacturer in manufacturers]
            return [self.listClients(i) for i in list_address]
        except Exception as e:
            logging.error(f"Error retrieving manufacturers: {e}")
            return None
        finally:
            self.close_connection()

    def listManufacturers(self):
        logging.info('Retrieving all manufacturers')
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "select distinct address_input from public.manufacturers")
            manufacturers = cursor.fetchall()
            # a = 'ae78c62c13f4e53a448da6c47b7ce87236b6f9272be81500481f35c1ec11d4de8b0fa4'
            list_address = [manufacturer[0] for manufacturer in manufacturers]
            return [self.listClients(i) for i in list_address]
        except Exception as e:
            logging.error(f"Error retrieving manufacturers: {e}")
            return None
        finally:
            self.close_connection()

    # Thêm phương thức đóng kết nối khi không sử dụng nữa

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
