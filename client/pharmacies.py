from flask import Flask, render_template, request
from pharmacy_class import pharmacy

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['LC_ALL'] = "en_US.UTF-8"
app.config['LANG'] = "en_US.UTF-8"
app.config['JSON_AS_ASCII'] = False


@app.route("/")
def home():
    return render_template('pharmacies.html')


@app.route("/getFromDistributer", methods=['GET', 'POST'])
def get_from_distributor():
    p = pharmacy()
    dist_name = request.form['distributer']
    pharma_name = request.form['pharmacy']
    date = request.form['date']
    batchid = request.form['batchid']
    action = request.form['choice']
    result = p.getFromDistributor(
        dist_name, pharma_name, batchid, date, action)
    return render_template('alert.html', command=result, port="5030")


@app.route('/listMed', methods=['GET', 'POST'])
def list_medicines():
    p = pharmacy()
    pharma_name = request.form['pharmacy']
    result = p.listMedicines(pharma_name)
    if result is None:
        return render_template('alert.html', command="No Medicines", port="5030")
    if result.empty:
        return render_template('alert.html', command="No Medicines", port="5030")
    else:
        result.insert(0, 'ID', range(1, len(result) + 1))
        columns = result.columns.tolist()
        data_list = result.to_dict(orient="records")
        return render_template('data.html', data=data_list, columns=columns, name="Medicines", title='Pharmacies', port="5030")


@app.route('/listMedReq', methods=['GET', 'POST'])
def list_medicines_request():
    p = pharmacy()
    pharma_name = request.form['pharmacy']
    result = p.listMedicines_v1(pharma_name, 'request')
    if result is None:
        return render_template('alert.html', command="No Request", port="5030")
    if result.empty:
        return render_template('alert.html', command="No Request", port="5030")
    else:
        result.insert(0, 'ID', range(1, len(result) + 1))
        columns = result.columns.tolist()
        data_list = result.to_dict(orient="records")
        return render_template('data.html', data=data_list, columns=columns, name="Medicines Request", title='Pharmacies', port="5030")


@app.route('/track', methods=['GET', 'POST'])
def track():
    p = pharmacy()
    batchid = request.form['batchid']
    result = p.readMedicineBatch(batchid)
    i = 0
    args = ['0', '0', '0']
    result = result.split(',')
    while result[i] != " +":
        i = i + 1

    if i == 1:
        manu = result[0]
        dist = 0
        pharma = 0
    elif i == 2:
        manu = result[1]
        dist = result[0]
        pharma = 0
    elif i == 3:
        manu = result[2]
        dist = result[1]
        pharma = result[0]
    args = result[i+1:]
    return render_template('tracking.html', manufacturer=manu, distributer=dist, pharmacy=pharma, medicine=args[0], batchid=args[1], manu_date=args[2], exp_date=args[3])


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5030")
