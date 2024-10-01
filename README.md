#### Project Supply chain

- Run:
```
    - docker-compose up -d --build
    - Open 4 terminal to run file into container: docker exec -it pharma-client bash
        - 1. Run Administrator
            source virtualenvironment/venv/bin/activate
            python3 admin.py
        - 2. Run Manufacturer
            source virtualenvironment/venv/bin/activate
            python3 manufacturer.py
        - 3. Run Distributor
            source virtualenvironment/venv/bin/activate
            python3 distributor.py
        - 4. Run Pharmacies
            source virtualenvironment/venv/bin/activate
            python3 pharmacies.py

    - Open localhost
        - Admin: http://localhost:5000/
        - Manufacturer: http://localhost:5010/
        - Distributor: http://localhost:5020/
        - Pharmacies: http://localhost:5030/
```
