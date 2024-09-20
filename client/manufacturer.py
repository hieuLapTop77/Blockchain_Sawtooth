#!/usr/bin/python3
from flask import Flask, render_template, request
from manufacturer_class import manufacturer

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('manufacturer.html')

@app.route('/addMed', methods = ['GET', 'POST'])
def hello():
    m = manufacturer()
    manu_name = request.form['manufacturer']
    med = request.form['medicine']
    manu_date = request.form['manu_date']
    exp_date = request.form['exp_date']
    batchid = request.form['batchid']
    owner = manu_name
    result = m.manufacture(manu_name, med, batchid, manu_date, exp_date, owner)
    return render_template('alert.html',command=result,port="5010")

@app.route('/giveToDist', methods = ['GET', 'POST'])
def sendtoDist():
    m = manufacturer()
    manu = request.form['manufacturer']
    dist = request.form['distributor']
    batchid = request.form['batchid']
    date = request.form['date']
    result = m.giveToDistributor(manu, dist, batchid, date)
    return render_template('alert.html',command=result,port="5010")

@app.route('/listMed', methods = ['GET', 'POST'])
def listMed():
    m = manufacturer()
    manu_name = request.form['manufacturer']
    result = m.listMedicines(manu_name)
    if result:
        return render_template('alert.html',command=result,port="5010")
    else:
        return render_template('alert.html',command="No Medicines",port="5010")

if __name__=='__main__':
    app.config['FLASK_ENV'] = "development"
    app.config['DEBUG'] = True
    app.config['LC_ALL'] = "C.UTF-8"
    app.config['LANG'] = "C.UTF-8"
    app.run(debug=True, host="0.0.0.0", port="5010")
