#!/usr/bin/python3
import hashlib
import logging
import sys
import traceback

from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.exceptions import InternalError, InvalidTransaction
from sawtooth_sdk.processor.handler import TransactionHandler

DEFAULT_URL = 'tcp://validator:4004'


def hash(data):
    return hashlib.sha512(data.encode()).hexdigest()


logging.basicConfig(filename='tp.log', level=logging.DEBUG)
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


def getManufacturerAddress(manufacturer_name):
    return FAMILY_NAME + MANUFACTURER_ENTRIES + hash(manufacturer_name)[:58]


def getDistributerAddress(distributer_name, qualifier="has"):
    distributer_name = str(distributer_name)
    return FAMILY_NAME + DISTRIBUTER_ENTRIES + hash(distributer_name)[:57] + hash(qualifier)[0]


def getPharmacyAddress(pharmacy_name, qualifier="has"):
    return FAMILY_NAME + PHARMACY_ENTRIES + hash(pharmacy_name)[:57] + hash(qualifier)[0]


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
        _header = transaction.header
        payload_list = self._decode_data(transaction.payload)
        return payload_list

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.
        '''
        LOGGER.info('starting apply function')
        try:
            payload_list = self._unpack_transaction(transaction)
            LOGGER.info('payload: %s', payload_list)
            action = payload_list[0]
            try:
                if action == "addManufacturer":
                    manufacturer_name = payload_list[1]
                    self._addManufacturer(context, manufacturer_name)
                elif action == "addDistributor":
                    distributer_name = payload_list[1]
                    self._addDistributer(context, distributer_name)
                elif action == "addPharmacy":
                    pharmacy_name = payload_list[1]
                    self._addPharmacy(context, pharmacy_name)
                # l = [manufacturer_name, medicine_name, batchID, manufacture_date, expiry_date]
                elif action == "manufacture":
                    [manufacturer_name, medicine_name, batchID,
                        manufacture_date, expiry_date] = payload_list[1:]
                    # manufacturer_name = payload_list[1]
                    # medicine_name = payload_list[2]
                    # batchid = pa
                    # medicineDetails = payload_list[3:7]
                    self._manufacture(
                        context, manufacturer_name, medicine_name, batchID, manufacture_date, expiry_date)

                elif action == "giveTo":
                    manufacturer_name = payload_list[1]
                    distributer_name = payload_list[2]
                    self._giveTo(context, manufacturer_name,
                                 distributer_name, medicine_name)
                    action = payload_list[0]

                elif action == "giveToDistributer":
                    manufacturer_name = payload_list[1]
                    distributer_name = payload_list[2]
                    batchid = payload_list[3]
                    date = payload_list[4]
                    # medicineDetails = payload_list[3:7]
                    self._giveToDistributer(
                        context, manufacturer_name, distributer_name, batchid, date)

                    # l = [distributer, pharmacy, batchID, date]
                elif action == "giveToPharmacy":
                    distributer_name = payload_list[1]
                    pharmacy_name = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    self._giveToPharmacy(
                        context, distributer_name, pharmacy_name, batchID, date)
                    action = payload_list[0]

                # l = [manufacturer_name, distributer, batchID, date, action]
                elif action == "getFromManufacturer":
                    manufacturer_name = payload_list[1]
                    distributer_name = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    action = payload_list[5]
                    self._getFromManufacturer(
                        context, manufacturer_name, distributer_name, batchID, date, action)

                    # l = [distributer, pharmacy, batchID, date, action]
                elif action == "getFromDistributer":
                    ditributer_name = payload_list[1]
                    pharmacy_name = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    action = payload_list[5]
                    self._getFromDistributer(
                        context, ditributer_name, pharmacy_name, batchID, date, action)
                else:
                    LOGGER.debug("Unhandled action: %s", action)
            except IndexError as i:
                LOGGER.debug('IndexError: %s', i)
                raise i
        except Exception as e:
            raise e

    @classmethod
    def _addDistributer(self, context, distributer_name):
        try:
            LOGGER.info("entering addDist")
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            LOGGER.info('Distributers: %s', distributers)
            if distributers:
                if distributer_name not in distributers:
                    distributers.append(distributer_name)
                    medicines = []
                    _addresses = context.set_state({
                        getDistributerAddress(distributer_name): self._encode_data(medicines),
                        getDistributerAddress(distributer_name, 'request'): self._encode_data(medicines)
                    })
                else:
                    raise Exception('no manufacturer: ', distributer_name)
            else:
                distributers = [distributer_name]

            _addresses = context.set_state({
                DISTRIBUTERS_TABLE: self._encode_data(distributers)
            })
        except Exception as e:
            logging.debug('exception: %s', e)
            raise e

    @classmethod
    def _addManufacturer(self, context, manufacturer_name):
        try:
            LOGGER.info("entering add manufacture")
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)
            LOGGER.info('Manufacturers: %s', manufacturers)
            if manufacturers:
                if manufacturer_name not in manufacturers:
                    manufacturers.append(manufacturer_name)
                    medicines = []
                    _addresses = context.set_state({
                        getManufacturerAddress(manufacturer_name): self._encode_data(medicines)
                    })
                else:
                    raise Exception('no manufacturer: ' + manufacturer_name)
            else:
                manufacturers = [manufacturer_name]

            _addresses = context.set_state({
                MANUFACTURERS_TABLE: self._encode_data(manufacturers)
            })
        except Exception as e:
            logging.debug('excecption: %s', e)
            raise e

    @classmethod
    def _addPharmacy(self, context, pharmacy_name):
        try:
            # LOGGER.info("entering add pharmacy")
            pharmacy = self._readData(context, PHARMACY_TABLE)
            # LOGGER.info ('Manufacturers: %s',pharmacy)
            if pharmacy:
                if pharmacy_name not in pharmacy:
                    pharmacy.append(pharmacy_name)
                    medicines = []
                    _addresses = context.set_state({
                        getPharmacyAddress(pharmacy_name): self._encode_data(medicines),
                        getPharmacyAddress(pharmacy_name, 'request'): self._encode_data(medicines)
                    })
                else:
                    raise Exception('no pharmacy: ' + pharmacy_name)
            else:
                pharmacy = [pharmacy_name]

            _addresses = context.set_state({
                PHARMACY_TABLE: self._encode_data(pharmacy)
            })
        except Exception as e:
            logging.debug('excecption: %s', e)
            raise e
        # l = [manufacturer_name, medicine_name, batchID, manufacture_date, expiry_date, owner]

    @classmethod
    def _manufacture(self, context, manufacturer_name, medicine_name, batchID, manufacture_date, expiry_date):
        manufacturer_address = getManufacturerAddress(manufacturer_name)
        medicine_string = ', '.join(
            [manufacturer_name, '+', medicine_name, batchID, manufacture_date, expiry_date])
        batch_address = getBatchAddress(batchID)
        try:
            LOGGER.info("entering manufacture")
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)
            LOGGER.info('Manufacturers: %s', manufacturers)
            if manufacturers:
                if manufacturer_name in manufacturers:
                    medicines = self._readData(context, manufacturer_address)
                    medicines.append(batchID)
                    tracking = [medicine_string]

                    _addresses = context.set_state({
                        manufacturer_address: self._encode_data(medicines),
                        batch_address: self._encode_data(tracking)
                    })
                else:
                    raise Exception('no manufacturer: ' + manufacturer_name)
            else:
                raise Exception('no manufacturers')
        except Exception as e:
            logging.debug('excecption: %s', e)
            raise e

    # l = [manufacturer_name, distributer, batchID, date]
    @classmethod
    def _giveToDistributer(self, context, manufacturer_name, distributer_name, batchid, date):
        LOGGER.info("entering giveToDistributers")
        manufacturer_address = getManufacturerAddress(manufacturer_name)
        distributer_address = getDistributerAddress(
            distributer_name, "request")
        try:
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            LOGGER.info('manufacturers: %s', manufacturers)
            LOGGER.info('distributers: %s', distributers)
            if manufacturer_name in manufacturers and distributer_name in distributers:
                manufactured_medicines = self._readData(
                    context, manufacturer_address)
                if batchid in manufactured_medicines:
                    manufactured_medicines.remove(batchid)
                    LOGGER.info(batchid, '%s removed')
                    distributer_medicine = self._readData(
                        context, distributer_address)
                    distributer_medicine.append(batchid)
                    _addresses = context.set_state({
                        manufacturer_address: self._encode_data(manufactured_medicines),
                        distributer_address: self._encode_data(
                            distributer_medicine)
                    })
                    LOGGER.info('address written')
                else:
                    raise Exception("batchid not in medicineList")
            else:
                raise Exception("manu or pharma not in lists")
            LOGGER.info('%s gave %s to %s.request',
                        manufacturer_name, batchid, distributer_name)
        except TypeError as t:
            logging.debug('TypeError in _giveTo: %s', t)
            raise t
        except InvalidTransaction as e:
            logging.debug('excecption: %s', e)
            raise e
        except Exception as e:
            logging.debug('exception: %s', e)
            raise e

    # l = [manufacturer_name, distributer, batchID, date, owner, action]
    @classmethod
    def _getFromManufacturer(self, context, manufacturer_name, distributer_name, batchID, date, action):
        LOGGER.info("entering getFromManufacturer")
        action = str(action)
        manufacturer_address = getManufacturerAddress(manufacturer_name)
        distributer_request_address = getDistributerAddress(
            distributer_name, "request")
        distributer_has_address = getDistributerAddress(
            distributer_name, "has")
        batch_address = getBatchAddress(batchID)
        try:
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            LOGGER.info('manufacturers: %s', manufacturers)
            LOGGER.info('distributers: %s', distributers)
            if manufacturer_name in manufacturers and distributer_name in distributers:
                distributer_request_medicine = self._readData(
                    context, distributer_request_address)
                if batchID in distributer_request_medicine:
                    distributer_request_medicine.remove(batchID)
                    LOGGER.info(
                        batchID, '%s removed from request list of distributer')
                    if action == "Accept":
                        distributer_has_medicine = self._readData(
                            context, distributer_has_address)
                        distributer_has_medicine.append(batchID)

                        tracking = self._readData(context, batch_address)
                        tracking = [distributer_name] + tracking

                        _addresses = context.set_state({
                            distributer_has_address: self._encode_data(distributer_has_medicine),
                            distributer_request_address: self._encode_data(distributer_request_medicine),
                            batch_address: self._encode_data(tracking)
                        })
                        LOGGER.info(
                            batchID, '%s added to has list of distributer and tracking updated')
                    elif action == "Reject":
                        manufacturerMedicine = self._readData(
                            context, manufacturer_address)
                        manufacturerMedicine.append(batchID)

                        _addresses = context.set_state({
                            manufacturer_address: self._encode_data(manufacturerMedicine),
                            distributer_request_address: self._encode_data(
                                distributer_request_medicine)
                        })

                        LOGGER.info(batchID, '%s added back to manufacturer')
                else:
                    raise Exception("batchid not in medicine list")
            else:
                raise Exception("manu or dist not in lists")
            # LOGGER.info('{} gave {} to %s',manufacturer_name, medicineDetails, distributer_name)
        except TypeError as t:
            logging.debug('TypeError in _giveTo: %s', t)
            raise t
        except InvalidTransaction as e:
            logging.debug('excecption: %s', e)
            raise e
        except Exception as e:
            logging.debug('exception: %s', e)
            raise e

    @classmethod
    def _giveToPharmacy(self, context, distributer_name, pharmacy_name, batchid, date):
        LOGGER.info("entering giveToPharmacy")
        distributer_address = getDistributerAddress(distributer_name)
        pharmacy_address = getPharmacyAddress(pharmacy_name, "request")
        try:
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            pharmacies = self._readData(context, PHARMACY_TABLE)
            LOGGER.info('distributers: %s', distributers)
            LOGGER.info('pharmacies: %s', pharmacies)
            if distributer_name in distributers and pharmacy_name in pharmacies:
                distributer_medicines = self._readData(
                    context, distributer_address)
                if batchid in distributer_medicines:
                    distributer_medicines.remove(batchid)
                    LOGGER.info(batchid, '%s removed from distributers')
                    pharmacy_medicine = self._readData(
                        context, pharmacy_address)
                    pharmacy_medicine.append(batchid)
                    _addresses = context.set_state({
                        distributer_address: self._encode_data(distributer_medicines),
                        pharmacy_address: self._encode_data(pharmacy_medicine)
                    })
                else:
                    raise Exception("batchId not in medicineList")
            else:
                raise Exception("distributer or pharmacy not existent")
            LOGGER.info('%s gave %s to %s .request',
                        distributer_name, batchid, pharmacy_name)
        except TypeError as t:
            logging.debug('TypeError in _giveTo: %s', t)
            raise t
        except InvalidTransaction as e:
            logging.debug('excecption: %s', e)
            raise e
        except Exception as e:
            logging.debug('exception: %s', e)
            raise e

    @classmethod
    def _getFromDistributer(self, context, distributer_name, pharmacy_name, batchID, date, action):
        LOGGER.info("entering getFromDistributer")
        action = str(action)
        distributer_address = getDistributerAddress(distributer_name)
        pharmacy_request_address = getPharmacyAddress(pharmacy_name, "request")
        pharmacy_has_address = getPharmacyAddress(pharmacy_name, "has")
        batch_address = getBatchAddress(batchID)
        try:
            pharmacy = self._readData(context, PHARMACY_TABLE)
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            LOGGER.info('pharmacy: %s', pharmacy)
            LOGGER.info('distributers: %s', distributers)
            if pharmacy_name in pharmacy and distributer_name in distributers:
                pharmacy_request_medicine = self._readData(
                    context, pharmacy_request_address)
                if batchID in pharmacy_request_medicine:
                    pharmacy_request_medicine.remove(batchID)
                    LOGGER.info(
                        batchID, '%s removed from request list of pharmacy')
                    if action == "Accept":
                        pharmacy_has_medicine = self._readData(
                            context, pharmacy_has_address)
                        pharmacy_has_medicine.append(batchID)

                        tracking = self._readData(context, batch_address)
                        tracking = [pharmacy_name] + tracking

                        _addresses = context.set_state({
                            pharmacy_has_address: self._encode_data(pharmacy_has_medicine),
                            pharmacy_request_address: self._encode_data(pharmacy_request_medicine),
                            batch_address: self._encode_data(tracking)
                        })
                        LOGGER.info(
                            batchID, '%s added to has list of distributer and tracking updated')
                    elif action == "Reject":
                        distributer_medicine = self._readData(
                            context, distributer_address)
                        distributer_medicine.append(batchID)

                        _addresses = context.set_state({
                            distributer_address: self._encode_data(distributer_medicine),
                            pharmacy_request_address: self._encode_data(
                                pharmacy_request_medicine)
                        })

                        LOGGER.info(batchID, '%s added back to distributer')
                else:
                    raise Exception("batchid not in list")
            else:
                raise Exception("dist or pharma not in lists")
            # LOGGER.info('{} gave {} to %s',manufacturer_name, medicineDetails, distributer_name)
        except TypeError as t:
            logging.debug('TypeError in _giveTo: %s', t)
            raise t
        except InvalidTransaction as e:
            logging.debug('excecption: %s', e)
            raise e
        except Exception as e:
            logging.debug('exception: %s', e)
            raise e

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
