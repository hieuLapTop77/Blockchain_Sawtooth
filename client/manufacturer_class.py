#!/bin/python3
from client import *

class manufacturer():
	def __init__(self):
		pass

	def manufacture(self, manufacturerName, medicineName, batchID, manufactureDate, expiryDate, owner):
		logging.info ('manufacture({})'.format(medicineName))
		l = [manufacturerName, medicineName, batchID, manufactureDate, expiryDate]
		manufacturerAddress = getManufacturerAddress(manufacturerName)
		batchAddress = getBatchAddress(batchID)
		command_string = ','.join(l)
		input_address_list = [MANUFACTURERS_TABLE, manufacturerAddress, batchAddress]
		output_address_list = [manufacturerAddress, batchAddress]
		response = wrap_and_send("manufacture", command_string, input_address_list, output_address_list, wait = 5)
		# print ("manufacture response: {}".format(response))
		return yaml.safe_load(response)['data'][0]['status']

	def giveToDistributor(self, manufacturerName, distributer, batchID, date):
		l = [manufacturerName, distributer, batchID, date]
		command_string = ','.join(l)
		distributerAddress = getDistributerAddress(distributer,"request")
		manufacturerAddress = getManufacturerAddress(manufacturerName)
		batchAddress = getBatchAddress(batchID)
		input_address_list = [DISTRIBUTERS_TABLE, MANUFACTURERS_TABLE, manufacturerAddress, distributerAddress, batchAddress]
		output_address_list = [manufacturerAddress, distributerAddress, batchAddress]
		response = wrap_and_send("giveToDistributer", command_string, input_address_list, output_address_list, wait = 5)
		# print ("give response: {}".format(response))
		return yaml.safe_load(response)['data'][0]['status']

	def listMedicines(self, manufacturerName):
		address = getManufacturerAddress(manufacturerName)
		result = listClients(address)
		if result:
			return result
		else:
			return "No medicines"