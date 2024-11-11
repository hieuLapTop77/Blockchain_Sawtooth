#!/usr/bin/python3
from distributor_class import distributer
from flask import Flask, render_template, request

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['LC_ALL'] = "C.UTF-8"
app.config['LANG'] = "C.UTF-8"


@app.route("/")
def home():
    return render_template('distributor.html')


@app.route('/recieveFromManufacturer', methods=['POST', 'GET'])
def recieve_from_manufacturer():
    d = distributer()
    manu_name = request.form['manufacturer']
    dist_name = request.form['distributer']
    date = request.form['date']
    batchid = request.form['batchid']
    action = request.form['choice']
    k = d.getFromManufacturer(manu_name, dist_name, batchid, date, action)
    if (k == "COMMITTED"):
        return render_template('alert.html', command=f"{action} successfully", port="5020")
    else:
        return render_template('alert.html', command="SOMETHING FAILED! \nOOPS!", port="5020")


@app.route('/sendToPharmacy', methods=['POST', 'GET'])
def send_to_pharmacy():
    d = distributer()
    dist_name = request.form['distributer']
    pharma_name = request.form['pharmacy']
    date = request.form['date']
    batchid = request.form['batchid']
    k = d.giveToPharmacy(dist_name, pharma_name, batchid, date)
    if (k == "COMMITTED"):
        return render_template('alert.html', command="SENT TO PHARMACY SUCCESSFULLY", port="5020")
    else:
        return render_template('alert.html', command="SOMETHING FAILED! \nOOPS!", port="5020")


@app.route('/listMed', methods=['GET', 'POST'])
def list_medicines():
    m = distributer()
    dist_name = request.form['distributer']
    result = m.listMedicines(dist_name)
    if result is None:
        return render_template('alert.html', command="No Medicines", port="5020")
    if result.empty:
        return render_template('alert.html', command="No Medicines", port="5020")
    else:
        result.insert(0, 'ID', range(1, len(result) + 1))
        columns = result.columns.tolist()
        data_list = result.to_dict(orient="records")
        return render_template('data.html', data=data_list, columns=columns, name="Medicines", title='Distributer', port="5020")


@app.route('/listMedReq', methods=['GET', 'POST'])
def list_medicines_request():
    m = distributer()
    dist_name = request.form['distributer']
    result = m.listMedicines_v1(dist_name, 'request')
    if result is None:
        return render_template('alert.html', command="No Medicines", port="5020")
    if result.empty:
        return render_template('alert.html', command="No Medicines", port="5020")
    else:
        result.insert(0, 'ID', range(1, len(result) + 1))
        columns = result.columns.tolist()
        data_list = result.to_dict(orient="records")
        return render_template('data.html', data=data_list, columns=columns, name="Requests", title='Distributer', port="5020")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5020")
