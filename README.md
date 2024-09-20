# Pharmaceutical supply chain using Hyperledger sawtooth

## Description

The supply chain involves:

 1. Manufacturer  
         The manufacturer manufactures the medicine in units, or *batches*, identified by a *batchID*. The manufacture now owns the batch. The manufacturer can send this batch to a distributor.
 2. Distributor  
         The distributor now has the option to either *accept* or *reject* the batch. If rejected, ownership doesn't change; the batch remains under the manufacture. If the batch is accepted, ownership is transferred to the distributor. The distributor can send this batch to a pharmacy.
 3. Pharmacy  
         The pharmacy has the option to *accept* or *reject* the batch; this is similar to the distributor.
 4. Admin  
         The admin can add manufacturers, distributors and pharmacies.

## Details
1. Navigate into the folder in the terminal.  
Bring up the docker containers using the command:  
    `$ [sudo] docker-compose up`  
This starts the client, processor, network,  validator, dev-mode consensus engine.  
2. Open a new terminal to enter into the pharma-client docker container.  
    `$ [sudo] docker exec -it pharma-client bash`  
3. Install flask.  
    `# pip3 install Flask`  
4. The four players - admin, manufacturers, distributors and pharmacies - each have their own webpages, hosted on different ports.  
     Open 4 new terminals, one for each:  
     * `# python3 admin.py`  
     * `# python3 manufacturer.py`  
     * `# python3 distributor.py`  
     * `# python3 pharmacies.py` 
  5. Open the webpages in a browser:  
	  * `0.0.0.0/5000` - for the admin  
	  * `0.0.0.0/5010` - for the manufacturer  
	  * `0.0.0.0/5020`- for the distributor  
	  * `0.0.0.0/5030` - for the pharmacy  
