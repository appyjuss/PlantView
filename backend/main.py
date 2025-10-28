from flask import Flask

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', "jpeg"}

class UploadFile(Resource):

    def post(self):
        upload = request.files['file']

        if not upload.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            return{"errors": ["Image format must be .png, .jpg, or .jpeg"]}, 422

        if upload.filename != "":
            try:
                upload.save(f'./static/{upload.filename}')
                return {"filename": upload.filename}, 201
            except Exception as err:
                return {"errors": [str(err)]}, 422
        return {"errors": ["missing filename"]}, 422

api.add_resource(UploadFile, '/api/upload')py