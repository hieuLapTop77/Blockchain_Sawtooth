#!/bin/python3
from client import *

class distributer():
	def __init__(self):
		pass

	def getFromManufacturer(self, manufacturerName, distributer, batchID, date, action):
		l = [manufacturerName, distributer, batchID, date, action]
		command_string = ','.join(l)
		distributerReqAddress = getDistributerAddress(distributer, "request")
		distributerAddress = getDistributerAddress(distributer, "has")
		manufacturerAddress = getManufacturerAddress(manufacturerName)
		batchAddress = getBatchAddress(batchID)
		input_address_list = [DISTRIBUTERS_TABLE, MANUFACTURERS_TABLE, manufacturerAddress, distributerAddress, distributerReqAddress, batchAddress]
		output_address_list = [manufacturerAddress, distributerAddress, distributerReqAddress, batchAddress]
		response = wrap_and_send("getFromManufacturer", command_string, input_address_list, output_address_list, wait = 5)
		return yaml.safe_load(response)['data'][0]['status']

	def giveToPharmacy(self, distributer, pharmacy, batchID, date):
		l = [distributer, pharmacy, batchID, date]
		command_string = ','.join(l)
		distributerAddress = getDistributerAddress(distributer, "has")
		pharmacyAddress = getPharmacyAddress(pharmacy, "request")
		batchAddress = getBatchAddress(batchID)
		input_address_list = [DISTRIBUTERS_TABLE, PHARMACY_TABLE,pharmacyAddress, distributerAddress, batchAddress]
		output_address_list = [pharmacyAddress, distributerAddress, batchAddress]
		response = wrap_and_send("giveToPharmacy", command_string, input_address_list, output_address_list, wait = 5)
		return yaml.safe_load(response)['data'][0]['status']

	def listMedicines(self, distributerName, qualifier = 'has'):
		address = getDistributerAddress(distributerName, qualifier)
		result = listClients(address)
		if result:
			return result
		else:
			return "No medicines"