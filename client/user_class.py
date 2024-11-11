#!/bin/python3
from client import getBatchAddress, listClients


class User():
    def __init__(self):
        pass

    def readMedicineBatch(self, batchid):
        address = getBatchAddress(batchid)
        result = listClients(address)
        if result:
            return result
        else:
            return "No such medicine batch"
