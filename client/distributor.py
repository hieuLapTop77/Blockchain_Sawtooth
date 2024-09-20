#!/usr/bin/python3
from flask import Flask, render_template, request
from distributor_class import distributer

app=Flask(__name__)
app.config['DEBUG'] = True
app.config['LC_ALL'] = "C.UTF-8"
app.config['LANG'] = "C.UTF-8"

@app.route("/")
def homepage():
	return render_template('distributor.html')

@app.route('/recieveFromManufacturer', methods = ['POST','GET'])
def recieveFromManufacturer():
    d = distributer()
    manu_name = request.form['manufacturer']
    dist_name = request.form['distributer']
    date = request.form['date']
    batchid = request.form['batchid']
    action = request.form['choice']
    k = d.getFromManufacturer(manu_name, dist_name, batchid, date, action)
    if (k == "COMMITTED"):
        return render_template('alert.html',command="SENT THE REQUIRED BATCH SUCCESSFULLY", port = "5020")
    else:
       return render_template('alert.html',command="SOMETHING FAILED! \nOOPS!", port = "5020")

@app.route('/sendToPharmacy', methods=['POST', 'GET'])
def sendToPharmacy():
    d = distributer()
    dist_name = request.form['distributer']
    pharma_name = request.form['pharmacy']
    date = '12/5/19' #request.form['date']
    batchid = request.form['batchid']
    k = d.giveToPharmacy(dist_name, pharma_name, batchid, date)
    if (k == "COMMITTED"):
        return render_template('alert.html',command="SENT TO PHARMACY", port = "5020")
    else:
       return render_template('alert.html',command="SOMETHING FAILED! \nOOPS!", port = "5020")


@app.route('/listMed', methods = ['GET', 'POST'])
def listMed():
    m = distributer()
    dist_name = request.form['distributer']
    result = m.listMedicines(dist_name)
    return render_template('alert.html',command=result, port="5020")

@app.route('/listMedReq', methods = ['GET', 'POST'])
def listMedReq():
    m = distributer()
    dist_name = request.form['distributer']
    result = m.listMedicines(dist_name, 'request')
    return render_template('alert.html', command = result, port="5020")

if __name__=='__main__':
	app.run(host = "0.0.0.0", port = "5020")
