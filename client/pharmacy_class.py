#!/bin/python3
from client import *

class pharmacy():
	def __init__(self):
		pass

	def getFromDistributor(self, distributer, pharmacy, batchID, date, action):
		l = [distributer, pharmacy, batchID, date, action]
		command_string = ','.join(l)
		distributerAddress = getDistributerAddress(distributer, "has")
		pharmacyReqAddress = getPharmacyAddress(pharmacy,"request")
		pharmacyHasAddress = getPharmacyAddress(pharmacy,"has")
		batchAddress = getBatchAddress(batchID)
		input_address_list = [DISTRIBUTERS_TABLE, PHARMACY_TABLE, pharmacyReqAddress, pharmacyHasAddress, distributerAddress, batchAddress]
		output_address_list = [distributerAddress, distributerAddress, pharmacyHasAddress, pharmacyReqAddress, batchAddress]
		response = wrap_and_send("getFromDistributer", command_string, input_address_list, output_address_list, wait = 5)
		return yaml.safe_load(response)['data'][0]['status']


	def listMedicines(self, pharmacyName, qualifier = 'has'):
		address = getPharmacyAddress(pharmacyName, qualifier)
		result = listClients(address)
		if result:
			return result
		else:
			return "No medicines"
		
	def readMedicineBatch(self, batchid):
		address = getBatchAddress(batchid)
		result = listClients(address)
		if result:
			return result
		else:
			return "No such medicine batch"