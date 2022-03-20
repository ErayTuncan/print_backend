import os
from flask import Flask, send_from_directory
from flask_restful import Api, Resource, request
from database import *
import uuid

app = Flask(__name__)
api = Api(app)

directory = "./files/"

class saveFile(Resource):
    def post(self):
        response = {}
        if 'file' not in request.files:
            return {'response': 'no file'}, 400

        file_record = {}

        fileuuid = str(uuid.uuid4())
        filename = fileuuid[-8:] + "-" + request.files["file"].filename

        filedir = directory + filename
        file = request.files["file"]

        file.save(filedir)

        file_record['fileuuid'] = fileuuid
        file_record['filename'] = filename

        db_create_file_record(file_record)

        response['response'] = 'file added'
        response['uuid'] = fileuuid

        return response, 200

class retrieveFile(Resource):
    def get(self):
        fileuuid = request.args.get('fileuuid')

        record = db_query_file_record(fileuuid)

        filename = record['filename']

        path = os.path.join(directory)

        return send_from_directory(path, filename)



# Add URL endpoins
api.add_resource(saveFile, '/save-file')
api.add_resource(retrieveFile, '/retrieve-file')



if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
