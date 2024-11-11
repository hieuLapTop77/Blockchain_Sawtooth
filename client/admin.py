#!/usr/bin/python3

import os

import pandas as pd
from admin_class import admin
from flask import Flask, render_template, request

os.environ['PYTHONIOENCODING'] = 'utf-8'

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['LC_ALL'] = "en_US.UTF-8"
app.config['LANG'] = "en_US.UTF-8"
app.config['JSON_AS_ASCII'] = False


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
        print("Tên nhà sản xuất: ", manufacturer)
        k = a.addManufacturer(manufacturer)
        if (k == "COMMITTED"):
            return render_template('alert.html', command="ADDED MANUFACTURER", port="5000")
        return render_template('alert.html', command="SOMETHING FAILED!", port="5000")
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
        list_ = result.split(",")
        df = pd.DataFrame({"Manufacturers": list_})
        df.insert(0, 'ID', range(1, len(df) + 1))
        columns = df.columns.tolist()
        data_list = df.to_dict(orient="records")
        return render_template('data.html', data=data_list, columns=columns, name="Manufacturers", title='Admin', port="5000")
    except:
        return render_template('alert.html', command="No Manufacturers", port="5000")


@app.route('/listDist', methods=['POST', 'GET'])
def listDist():
    a = admin()
    try:
        result = a.listDistributers()
        list_ = result.split(",")
        df = pd.DataFrame({"Distributers": list_})
        df.insert(0, 'ID', range(1, len(df) + 1))
        columns = df.columns.tolist()
        data_list = df.to_dict(orient="records")
        return render_template('data.html', data=data_list, columns=columns, name="Distributers", title='Admin', port="5000")
    except:
        return render_template('alert.html', command="No Distributers", port="5000")


@app.route('/listPharma', methods=['POST', 'GET'])
def listPharma():
    a = admin()
    try:
        result = a.listPharmacies()
        list_ = result.split(",")
        df = pd.DataFrame({"Pharmacies": list_})
        df.insert(0, 'ID', range(1, len(df) + 1))
        columns = df.columns.tolist()
        data_list = df.to_dict(orient="records")
        return render_template('data.html', data=data_list, columns=columns, name="Pharmacies", title='Admin', port="5000")
    except:
        return render_template('alert.html', command="No Pharmacies", port="5000")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
