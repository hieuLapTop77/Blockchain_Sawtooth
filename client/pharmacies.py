from flask import Flask, render_template, request
from pharmacy_class import pharmacy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['LC_ALL'] = "C.UTF-8"
app.config['LANG'] = "C.UTF-8"

@app.route("/")
def homepage():
	return render_template('pharmacies.html')

@app.route("/getFromDistributer", methods = ['GET', 'POST'])
def getFromDist():
	p = pharmacy()
	dist_name = request.form['distributer']
	pharma_name = request.form['pharmacy']
	date = request.form['date']
	batchid = request.form['batchid']
	action = request.form['choice']
	result = p.getFromDistributor(dist_name, pharma_name, batchid, date, action)
	return render_template('alert.html', command=result, port="5030")

@app.route('/listMed', methods = ['GET', 'POST'])
def listMed():
    p = pharmacy()
    pharma_name = request.form['pharmacy']
    result = p.listMedicines(pharma_name)
    return render_template('alert.html',command=result, port="5030")

@app.route('/listMedReq', methods = ['GET', 'POST'])
def listMedReq():
    p = pharmacy()
    pharma_name = request.form['pharmacy']
    result = p.listMedicines(pharma_name, 'request')
    return render_template('alert.html',command=result, port="5030")

@app.route('/track', methods = ['GET', 'POST'])
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
	return render_template('tracking.html', manufacturer = manu, distributer = dist, pharmacy = pharma, medicine = args[0], batchid = args[1], manu_date = args[2], exp_date = args[3])

if __name__=='__main__':
	app.run(debug=True, host="0.0.0.0", port="5030")
