#!/usr/bin/python3
import html
import os

from flask import Flask, render_template, request
from manufacturer_class import manufacturer

from client import MANUFACTURERS_TABLE

os.environ['PYTHONIOENCODING'] = 'utf-8'
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('manufacturer.html')


@app.route('/addMed', methods=['GET', 'POST'])
def add_medicines():
    m = manufacturer()
    manu_name = request.form['manufacturer']
    med = request.form['medicine']
    manu_date = request.form['manu_date']
    exp_date = request.form['exp_date']
    batchid = m.get_bat_id(MANUFACTURERS_TABLE)
    owner = manu_name
    result = m.manufacture(manu_name, med, batchid, manu_date, exp_date, owner)
    return render_template('alert.html', command=result, port="5010")


@app.route('/giveToDist', methods=['GET', 'POST'])
def send_to_distributor():
    m = manufacturer()
    manu = request.form['manufacturer']
    dist = request.form['distributor']
    # batchid = m.get_bat_id(MANUFACTURERS_TABLE)
    batchid = request.form['batchid']
    date = request.form['date']
    result = m.giveToDistributor(manu, dist, batchid, date)
    return render_template('alert.html', command=result, port="5010")


@app.route('/listMed', methods=['GET', 'POST'])
def list_medicines():
    m = manufacturer()
    manu_name = request.form['manufacturer']
    result = m.listMedicines(manu_name)
    if result is None:
        return render_template('alert.html', command="No Medicines", port="5010")
    if result.empty:
        return render_template('alert.html', command="No Medicines", port="5010")
    else:
        result.insert(0, 'ID', range(1, len(result) + 1))
        columns = result.columns.tolist()
        data_list = result.to_dict(orient="records")
        return render_template('data.html', data=data_list, columns=columns, name="Medicines", title='Manufacturer', port="5010")


if __name__ == '__main__':
    app.config['FLASK_ENV'] = "development"
    app.config['DEBUG'] = True
    app.config['LC_ALL'] = "en_US.UTF-8"
    app.config['LANG'] = "en_US.UTF-8"
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True, host="0.0.0.0", port="5010")
