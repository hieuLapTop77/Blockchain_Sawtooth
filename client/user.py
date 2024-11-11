import io

import qrcode
from flask import Flask, make_response, render_template, request, send_file
from user_class import User

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['LC_ALL'] = "C.UTF-8"
app.config['LANG'] = "C.UTF-8"


@app.route("/")
def home():
    return render_template('client.html')


@app.route('/qr')
def generate_qr():
    batch_id = request.args.get('batch_id')
    # URL chứa thông tin sản phẩm, bạn cần thay 'example.com' thành tên miền của bạn
    if not batch_id:
        return "<h1>Vui lòng cung cấp batch_id</h1>"
    url = f"http://localhost:5040/track/{batch_id}"
    # Tạo QR code từ URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Tạo hình ảnh QR code và lưu vào bộ nhớ tạm
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)

    # Trả về ảnh QR code dưới dạng file ảnh PNG
    return send_file(buf, mimetype='image/png')


@app.route('/track/<batch_id>', methods=['GET', 'POST'])
def track(batch_id):
    u = User()
    result = u.readMedicineBatch(batch_id)
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
    app.run(debug=True, host="0.0.0.0", port="5040")
