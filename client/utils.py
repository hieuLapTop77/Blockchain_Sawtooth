#!/usr/bin/python3
import hashlib

def hash(data):
    return hashlib.sha512(data.encode()).hexdigest()

family_name = "pharma"
FAMILY_NAME = hash(family_name)[:6]

TABLES = hash("tables")[:6]


MANUFACTURER_ENTRIES = hash("manufacturer-entries")[:6]
MANUFACTURERS = hash("manufacturers")
MANUFACTURERS_TABLE = FAMILY_NAME + TABLES + MANUFACTURERS[:58]

DISTRIBUTER_ENTRIES = hash("distributer-entries")[:6]
DISTRIBUTERS = hash("distributers")
DISTRIBUTERS_TABLE = FAMILY_NAME + TABLES + DISTRIBUTERS[:58]

def getManufacturerAddress(manufacturerName):
    return FAMILY_NAME + MANUFACTURER_ENTRIES + hash(manufacturerName)[:58]

def getDistributerAddress(distributerName, qualifier = "has"):
    distributerName = str(distributerName)
    return FAMILY_NAME + DISTRIBUTER_ENTRIES + hash(distributerName)[:57] + hash(qualifier)[0]
