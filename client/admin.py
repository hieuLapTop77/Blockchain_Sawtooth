#!/usr/bin/python3
from admin_class import admin
from flask import Flask, render_template, request

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['LC_ALL'] = "C.UTF-8"
app.config['LANG'] = "C.UTF-8"


@app.route("/")
def fun1():
    return render_template('admin.html')


@app.route('/addDist', methods=['POST', 'GET'])
def addDist():
    a = admin()
    distributer = request.form['distributer']
    k = a.addDistributer(distributer)
    if (k == "COMMITTED"):
        return render_template('alert.html', command="ADDED DISTRIBUTORS", port="5000")
    else:
        return render_template('alert.html', command="SOMETHING FAILED! \nOOPS!", port="5000")


@app.route('/addManu', methods=['POST', 'GET'])
def addManu():
    if request.method == 'POST':
        a = admin()
        manufacturer = request.form['manufacturer']
        print("Manufacturer: ", manufacturer)
        k = a.addManufacturer_v1(manufacturer)
        if (k == "COMMITTED"):
            return render_template('alert.html', command="ADDED MANUFACTURER", port="5000")
        return render_template('alert.html', command="SOMETHING FAILED! \nOOPS!", port="5000")
    return render_template('admin.html')


@app.route('/addPharma', methods=['POST', 'GET'])
def addPharma():
    a = admin()
    pharmacy = request.form['pharmacy']
    k = a.addPharmacy(pharmacy)
    if (k == "COMMITTED"):
        return render_template('alert.html', command="ADDED PHARMACY", port="5000")
    else:
        return render_template('alert.html', command="SOMETHING FAILED! \nOOPS!", port="5000")


@app.route('/listManu', methods=['POST', 'GET'])
def listManu():
    a = admin()
    try:
        result = a.listManufacturers()
        return render_template('alert.html', command=result, port="5000")
    except:
        return render_template('alert.html', command="No Manufacturers", port="5000")


@app.route('/listDist', methods=['POST', 'GET'])
def listDist():
    a = admin()
    try:
        result = a.listDistributers()
        return render_template('alert.html', command=result, port="5000")
    except:
        return render_template('alert.html', command="No Distributers", port="5000")


@app.route('/listPharma', methods=['POST', 'GET'])
def listPharma():
    a = admin()
    try:
        result = a.listPharmacies()
        return render_template('alert.html', command=result, port="5000")
    except:
        return render_template('alert.html', command="No Pharmacies", port="5000")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
