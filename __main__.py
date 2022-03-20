import os
from flask import Flask, flash, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
from database import *
import uuid
import qrcode

DOC_UPLOAD_FOLDER = './files/'
QR_CODE_FOLDER = './qrcodes/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['DOC_UPLOAD_FOLDER'] = DOC_UPLOAD_FOLDER
app.config['QR_CODE_FOLDER'] = QR_CODE_FOLDER

def upload_new_file(file):
    return_val = {"response":"success", "fileuuid":""}
    if file.filename == '':
        return_val["response"] = "empty_filename"
        return return_val

    if file and allowed_file(file.filename):
        file_record = {}

        fileuuid = str(uuid.uuid4())
        filename = fileuuid[-8:] + "-" + file.filename
        filename = secure_filename(filename)

        file_record['fileuuid'] = fileuuid
        file_record['filename'] = filename

        db_create_file_record(file_record)

        file.save(os.path.join(app.config['DOC_UPLOAD_FOLDER'], filename))
        
        return_val["fileuuid"] = fileuuid
        return return_val
    else:
        return_val["response"] = "file_not_allowed"
        return return_val


def show_result(id):
    img = qrcode.make(id)
    qr_path = os.path.join(app.config['QR_CODE_FOLDER'], id + ".png")
    img.save(qr_path)
    print(qr_path)
    return render_template("code.html", uuid_output=id, qr_code=qr_path)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        upload_resp = upload_new_file(file)

        if upload_resp["response"] == "success":
            show_result(upload_resp["fileuuid"])
        else:
            flash(upload_resp["response"])
            return redirect(request.url)


@app.route('/save-file', methods=['POST'])
def save_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return {"response": "No file part", "fileuuid":""}, 400

        file = request.files['file']

        upload_resp = upload_new_file(file)

        return upload_resp


@app.route('/retrieve-file', methods=['GET'])
def retrieve_file():
    if request.method == 'GET':
        fileuuid = request.args.get('fileuuid')

        record = db_query_file_record(fileuuid)

        filename = record['filename']

        path = os.path.join(app.config['DOC_UPLOAD_FOLDER'])

        return send_from_directory(path, filename)


if __name__ == "__main__":
    app.run(debug=True)