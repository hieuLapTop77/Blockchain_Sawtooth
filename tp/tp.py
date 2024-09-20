#!/usr/bin/python3
import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

DEFAULT_URL = 'tcp://validator:4004'

def hash(data):
    return hashlib.sha512(data.encode()).hexdigest()

logging.basicConfig(filename='tp.log',level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# namespaces
family_name = "pharma"
FAMILY_NAME = hash(family_name)[:6]

TABLES = hash("tables")[:6]

TRACKING = hash("tracking")[:6]
TRACKING_TABLE = FAMILY_NAME + TRACKING

MANUFACTURER_ENTRIES = hash("manufacturer-entries")[:6]
MANUFACTURERS = hash("manufacturers")
MANUFACTURERS_TABLE = FAMILY_NAME + TABLES + MANUFACTURERS[:58]

DISTRIBUTER_ENTRIES = hash("distributer-entries")[:6]
DISTRIBUTERS = hash("distributers")
DISTRIBUTERS_TABLE = FAMILY_NAME + TABLES + DISTRIBUTERS[:58]


PHARMACY_ENTRIES = hash("pharmacy-entries")[:6]
PHARMACY = hash("pharmacys")
PHARMACY_TABLE = FAMILY_NAME + TABLES + PHARMACY[:58]

def getBatchAddress(batchID):
    return TRACKING_TABLE + hash(batchID)[:58]

def getManufacturerAddress(manufacturerName):
    return FAMILY_NAME + MANUFACTURER_ENTRIES + hash(manufacturerName)[:58]

def getDistributerAddress(distributerName, qualifier = "has"):
    distributerName = str(distributerName)
    return FAMILY_NAME + DISTRIBUTER_ENTRIES + hash(distributerName)[:57] + hash(qualifier)[0]

def getPharmacyAddress(pharmacyname, qualifier = "has"):
    return FAMILY_NAME + PHARMACY_ENTRIES + hash(pharmacyname)[:57] + hash(qualifier)[0]

class PharmaTransactionHandler(TransactionHandler):
    '''
    Transaction Processor class for the pharma family
    '''
    def __init__(self, namespace_prefix):
        '''Initialize the transaction handler class.
        '''
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        '''Return Transaction Family name string.'''
        return family_name

    @property
    def family_versions(self):
        '''Return Transaction Family version string.'''
        return ['1.0']

    @property
    def namespaces(self):
        '''Return Transaction Family namespace 6-character prefix.'''
        return [self._namespace_prefix]

    # Get the payload and extract the pharma-specific information.
    # It has already been converted from Base64, but needs deserializing.
    # It was serialized with CSV: action, value
    def _unpack_transaction(self, transaction):
        header = transaction.header
        payload_list = self._decode_data(transaction.payload)
        return payload_list

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.
        '''
        LOGGER.info ('starting apply function')
        try:
            payload_list = self._unpack_transaction(transaction)
            LOGGER.info ('payload: {}'.format(payload_list))
            action = payload_list[0]
            try:
                if action == "addManufacturer":
                    manufacturerName = payload_list[1]
                    self._addManufacturer(context, manufacturerName)
                elif action == "addDistributor":
                    distributerName = payload_list[1]
                    self._addDistributer(context, distributerName)
                elif action == "addPharmacy":
                    pharmacyName = payload_list[1]
                    self._addPharmacy(context, pharmacyName)
            	#l = [manufacturerName, medicineName, batchID, manufactureDate, expiryDate]
                elif action == "manufacture":
                    [manufacturerName, medicineName, batchID, manufactureDate, expiryDate] = payload_list[1:]
                    # manufacturerName = payload_list[1]
                    # medicineName = payload_list[2]
                    # batchid = pa
                    # medicineDetails = payload_list[3:7]
                    self._manufacture(context, manufacturerName, medicineName, batchID, manufactureDate, expiryDate)
                
                elif action == "giveTo":
                    manufacturerName = payload_list[1]
                    distributerName = payload_list[2]
                    self._giveTo(context, manufacturerName, distributerName, medicineName)
                    action = payload_list[0]
                
                elif action == "giveToDistributer":
                    manufacturerName = payload_list[1]
                    distributerName = payload_list[2]
                    batchid = payload_list[3]
                    date = payload_list[4]
                    # medicineDetails = payload_list[3:7]
                    self._giveToDistributer(context, manufacturerName, distributerName, batchid, date)

        		# l = [distributer, pharmacy, batchID, date]
                elif action == "giveToPharmacy":
                    distributerName = payload_list[1]
                    pharmacyName = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    self._giveToPharmacy(context, distributerName, pharmacyName, batchID, date)
                    action = payload_list[0]

                # l = [manufacturerName, distributer, batchID, date, action]
                elif action == "getFromManufacturer":
                    manufacturerName = payload_list[1]
                    distributerName = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    action = payload_list[5]
                    self._getFromManufacturer(context, manufacturerName, distributerName, batchID, date, action)

        		# l = [distributer, pharmacy, batchID, date, action]
                elif action == "getFromDistributer":
                    ditributerName = payload_list[1]
                    pharmacyName = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    action = payload_list[5]
                    self._getFromDistributer(context, ditributerName, pharmacyName, batchID, date, action)
                else:
                    LOGGER.debug("Unhandled action: " + action)
            except IndexError as i:
                LOGGER.debug ('IndexError: {}'.format(i))
                raise Exception()
        except Exception as e:
            raise InvalidTransaction("Error: {}".format(e))
            
    @classmethod
    def _addDistributer(self, context, distributerName):
        try:
            LOGGER.info("entering addDist")
            distributers = self._readData(context, DISTRIBUTERS_TABLE)  
            LOGGER.info ('Distributers: {}'.format(distributers))
            if distributers:
                if distributerName not in distributers:
                    distributers.append(distributerName)
                    medicines = []
                    addresses  = context.set_state({
                                    getDistributerAddress(distributerName): self._encode_data(medicines),
                                    getDistributerAddress(distributerName, 'request'): self._encode_data(medicines)
                                })
                else:
                    raise Exception('no manufacturer: ' + distributerName)
            else:
                distributers = [distributerName]
            
            addresses  = context.set_state({
                            DISTRIBUTERS_TABLE: self._encode_data(distributers)
                        })
        except Exception as e:
            logging.debug ('exception: {}'.format(e))
            raise InvalidTransaction("State Error")

    @classmethod
    def _addManufacturer(self, context, manufacturerName):
        try:
            LOGGER.info("entering add manufacture")
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)  
            LOGGER.info ('Manufacturers: {}'.format(manufacturers))
            if manufacturers:
                if manufacturerName not in manufacturers:
                    manufacturers.append(manufacturerName)
                    medicines = []
                    addresses  = context.set_state({
                                    getManufacturerAddress(manufacturerName): self._encode_data(medicines)
                                })
                else:
                    raise Exception('no manufacturer: ' + manufacturerName)
            else:
                manufacturers = [manufacturerName]
            
            addresses  = context.set_state({
                            MANUFACTURERS_TABLE: self._encode_data(manufacturers)
                        })
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")

    @classmethod
    def _addPharmacy(self, context, pharmacyName):
        try:
            #LOGGER.info("entering add pharmacy")
            pharmacy = self._readData(context, PHARMACY_TABLE)  
            #LOGGER.info ('Manufacturers: {}'.format(pharmacy))
            if pharmacy:
                if pharmacyName not in pharmacy:
                    pharmacy.append(pharmacyName)
                    medicines = []
                    addresses  = context.set_state({
                                    getPharmacyAddress(pharmacyName): self._encode_data(medicines),
                                    getPharmacyAddress(pharmacyName, 'request'): self._encode_data(medicines)
                                })
                else:
                    raise Exception('no pharmacy: ' + pharmacyName)
            else:
                pharmacy = [pharmacyName]
            
            addresses  = context.set_state({
                            PHARMACY_TABLE: self._encode_data(pharmacy)
                        })
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")


	#l = [manufacturerName, medicineName, batchID, manufactureDate, expiryDate, owner]
    @classmethod
    def _manufacture(self, context, manufacturerName, medicineName, batchID, manufactureDate, expiryDate):
        manufacturerAddress = getManufacturerAddress(manufacturerName)
        medicine_string = ', '.join([manufacturerName, '+' ,medicineName, batchID, manufactureDate, expiryDate])
        batchAddress = getBatchAddress(batchID)
        try:
            LOGGER.info("entering manufacture")
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)  
            LOGGER.info ('Manufacturers: {}'.format(manufacturers))
            if manufacturers:
                if manufacturerName in manufacturers:
                    medicines = self._readData(context, manufacturerAddress)
                    medicines.append(batchID)
                    tracking = [medicine_string]
                    
                    addresses = context.set_state({
                        manufacturerAddress: self._encode_data(medicines),
                        batchAddress: self._encode_data(tracking)
                    })
                else:
                    raise Exception('no manufacturer: ' + manufacturerName)
            else:
                raise Exception('no manufacturers')
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")
        
    #l = [manufacturerName, distributer, batchID, date]
    @classmethod
    def _giveToDistributer(self, context, manufacturerName, distributerName, batchid, date):
        LOGGER.info("entering giveToDistributers")
        manufacturerAddress = getManufacturerAddress(manufacturerName)
        distributerAddress = getDistributerAddress(distributerName, "request")
        try:
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)  
            distributers = self._readData(context, DISTRIBUTERS_TABLE)  
            LOGGER.info ('manufacturers: {}'.format(manufacturers))
            LOGGER.info ('distributers: {}'.format(distributers))
            if manufacturerName in manufacturers and distributerName in distributers:
                manufacturedMedicines = self._readData(context, manufacturerAddress)
                if batchid in manufacturedMedicines:
                    manufacturedMedicines.remove(batchid)
                    LOGGER.info (batchid + 'removed')
                    distributerMedicine = self._readData(context, distributerAddress)
                    distributerMedicine.append(batchid)
                    addresses = context.set_state({
                        manufacturerAddress: self._encode_data(manufacturedMedicines),
                        distributerAddress: self._encode_data(distributerMedicine)
                    })
                    LOGGER.info('address written')
                else:
                    raise Exception("batchid not in medicineList")
            else:
                raise Exception("manu or pharma not in lists")
            LOGGER.info('{} gave {} to {}.request'.format(manufacturerName, batchid, distributerName))
        except TypeError as t:
            logging.debug('TypeError in _giveTo: {}'.format(t))
            raise InvalidTransaction('Type error')
        except InvalidTransaction as e:
            logging.debug ('excecption: {}'.format(e))
            raise e
        except Exception as e:
            logging.debug('exception: {}'.format(e))
            raise InvalidTransaction('excecption: {}'.format(e))

    # l = [manufacturerName, distributer, batchID, date, owner, action]
    @classmethod
    def _getFromManufacturer(self, context, manufacturerName, distributerName, batchID, date, action):
        LOGGER.info("entering getFromManufacturer")
        action = str(action)
        manufacturerAddress = getManufacturerAddress(manufacturerName)
        distributerRequestAddress = getDistributerAddress(distributerName,"request")
        distributerHasAddress = getDistributerAddress(distributerName,"has")
        batchAddress = getBatchAddress(batchID)
        try:
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)  
            distributers = self._readData(context, DISTRIBUTERS_TABLE)  
            LOGGER.info ('manufacturers: {}'.format(manufacturers))
            LOGGER.info ('distributers: {}'.format(distributers))
            if manufacturerName in manufacturers and distributerName in distributers:
                distributerRequestMedicine = self._readData(context,distributerRequestAddress)
                if batchID in distributerRequestMedicine:
                    distributerRequestMedicine.remove(batchID)
                    LOGGER.info (batchID + 'removed from request list of distributer')
                    if action == "Accept":
                        distributerHasMedicine = self._readData(context, distributerHasAddress)
                        distributerHasMedicine.append(batchID)
                        
                        tracking = self._readData(context, batchAddress)
                        tracking = [distributerName] + tracking
                        
                        addresses = context.set_state({
                            distributerHasAddress: self._encode_data(distributerHasMedicine),
                            distributerRequestAddress: self._encode_data(distributerRequestMedicine),
                            batchAddress: self._encode_data(tracking)
                        })
                        LOGGER.info (batchID + 'added to has list of distributer and tracking updated')
                    elif action == "Reject":
                        manufacturerMedicine = self._readData(context, manufacturerAddress)
                        manufacturerMedicine.append(batchID)
                        
                        addresses = context.set_state({
                            manufacturerAddress: self._encode_data(manufacturerMedicine),
                            distributerRequestAddress: self._encode_data(distributerRequestMedicine)
                        })
                        
                        LOGGER.info (batchID + 'added back to manufacturer')
                else:
                    raise Exception("batchid not in medicine list")
            else:
                raise Exception("manu or dist not in lists")
            #LOGGER.info('{} gave {} to {}'.format(manufacturerName, medicineDetails, distributerName))
        except TypeError as t:
            logging.debug('TypeError in _giveTo: {}'.format(t))
            raise InvalidTransaction('Type error')
        except InvalidTransaction as e:
            logging.debug ('excecption: {}'.format(e))
            raise e
        except Exception as e:
            logging.debug('exception: {}'.format(e))
            raise InvalidTransaction('excecption: {}'.format(e))

    @classmethod
    def _giveToPharmacy(self, context, distributerName, pharmacyName, batchid, date):
        LOGGER.info("entering giveToPharmacy")
        distributerAddress = getDistributerAddress(distributerName)
        pharmacyAddress = getPharmacyAddress(pharmacyName, "request")
        try:
            distributers = self._readData(context, DISTRIBUTERS_TABLE)  
            pharmacies = self._readData(context, PHARMACY_TABLE)  
            LOGGER.info ('distributers: {}'.format(distributers))
            LOGGER.info ('pharmacies: {}'.format(pharmacies))
            if distributerName in distributers and pharmacyName in pharmacies:
                distributerMedicines = self._readData(context, distributerAddress)
                if batchid in distributerMedicines:
                    distributerMedicines.remove(batchid)
                    LOGGER.info (batchid + 'removed from distributers')
                    pharmacyMedicine = self._readData(context, pharmacyAddress)
                    pharmacyMedicine.append(batchid)
                    addresses = context.set_state({
                        distributerAddress: self._encode_data(distributerMedicines),
                        pharmacyAddress: self._encode_data(pharmacyMedicine)
                    })
                else:
                    raise Exception("batchId not in medicineList")
            else:
                raise Exception("distributer or pharmacy not existent")
            LOGGER.info('{} gave {} to {}.request'.format(distributerName, batchid, pharmacyName))
        except TypeError as t:
            logging.debug('TypeError in _giveTo: {}'.format(t))
            raise InvalidTransaction('Type error')
        except InvalidTransaction as e:
            logging.debug ('excecption: {}'.format(e))
            raise e
        except Exception as e:
            logging.debug('exception: {}'.format(e))
            raise InvalidTransaction('excecption: {}'.format(e))

    @classmethod
    def _getFromDistributer(self, context, distributerName, pharmacyName, batchID, date, action):
        LOGGER.info("entering getFromDistributer")
        action = str(action)
        distributerAddress = getDistributerAddress(distributerName)
        pharmacyRequestAddress = getPharmacyAddress(pharmacyName,"request")
        pharmacyHasAddress = getPharmacyAddress(pharmacyName,"has")
        batchAddress = getBatchAddress(batchID)
        try:
            pharmacy = self._readData(context, PHARMACY_TABLE)  
            distributers = self._readData(context, DISTRIBUTERS_TABLE)  
            LOGGER.info ('pharmacy: {}'.format(pharmacy))
            LOGGER.info ('distributers: {}'.format(distributers))
            if pharmacyName in pharmacy and distributerName in distributers:
                pharmacyRequestMedicine = self._readData(context,pharmacyRequestAddress)
                if batchID in pharmacyRequestMedicine:
                    pharmacyRequestMedicine.remove(batchID)
                    LOGGER.info (batchID + 'removed from request list of pharmacy')
                    if action == "Accept":
                        pharmacyHasMedicine = self._readData(context, pharmacyHasAddress)
                        pharmacyHasMedicine.append(batchID)
                        
                        tracking = self._readData(context, batchAddress)
                        tracking = [pharmacyName] + tracking
                        
                        addresses = context.set_state({
                            pharmacyHasAddress: self._encode_data(pharmacyHasMedicine),
                            pharmacyRequestAddress: self._encode_data(pharmacyRequestMedicine),
                            batchAddress: self._encode_data(tracking)
                        })
                        LOGGER.info (batchID + 'added to has list of distributer and tracking updated')
                    elif action == "Reject":
                        distributerMedicine = self._readData(context, distributerAddress)
                        distributerMedicine.append(batchID)
                        
                        addresses = context.set_state({
                            distributerAddress: self._encode_data(distributerMedicine),
                            pharmacyRequestAddress: self._encode_data(pharmacyRequestMedicine)
                        })
                        
                        LOGGER.info (batchID + 'added back to distributer')
                else:
                    raise Exception("batchid not in list")
            else:
                raise Exception("dist or pharma not in lists")
            #LOGGER.info('{} gave {} to {}'.format(manufacturerName, medicineDetails, distributerName))
        except TypeError as t:
            logging.debug('TypeError in _giveTo: {}'.format(t))
            raise InvalidTransaction('Type error')
        except InvalidTransaction as e:
            logging.debug ('excecption: {}'.format(e))
            raise e
        except Exception as e:
            logging.debug('exception: {}'.format(e))
            raise InvalidTransaction('excecption: {}'.format(e))

    # returns a list
    @classmethod
    def _readData(self, context, address):
        state_entries = context.get_state([address])
        if state_entries == []:
            return []
        data = self._decode_data(state_entries[0].data)
        return data

    # returns a list
    @classmethod
    def _decode_data(self, data):
        return data.decode().split(',')

    # returns a csv string
    @classmethod
    def _encode_data(self, data):
        return ','.join(data).encode()


def main():
    try:
        # Setup logging for this class.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

        # Register the Transaction Handler and start it.
        processor = TransactionProcessor(url=DEFAULT_URL)
        sw_namespace = FAMILY_NAME
        handler = PharmaTransactionHandler(sw_namespace)
        processor.add_handler(handler)
        processor.start()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()