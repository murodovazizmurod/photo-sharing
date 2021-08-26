from datetime import datetime
import os
import imghdr
import cloudinary
import cloudinary.uploader as uploader


from flask import Flask, render_template, request, abort, redirect, jsonify
from ormx import Database
from ormx.models import Column, Table
from werkzeug.utils import secure_filename

app = Flask(__name__)
db = Database('files.db')

# Models

class Image(Table):
    __tablename__ = 'images'
    public = Column(str)
    size = Column(int)
    width = Column(int)
    height = Column(int)
    url = Column(str)
    created = Column(datetime)

db.create(Image)

cloudinary.config( 
  cloud_name = "duhmrouek", 
  api_key = "743114969696173", 
  api_secret = "irG5H-xkyaowaaPUuPLaWU1C7ZU" 
)

app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                    file_ext != validate_image(uploaded_file.stream):
                abort(400)
        u = uploader.upload(uploaded_file)
        image = Image(public=u['public_id'],
                      size=u['bytes'],
                      width=u['width'],
                      height=u['height'],
                      url=u['url'],
                      created=datetime.now())
        db.save(image)
        return redirect('/'+image.public)
    return render_template('index.html', images=db['images'])


@app.route('/<id>')
def upload(id):
    image = db.get(Image, public=id)
    if not image:
        abort(404)
    return render_template('download.html', image=image)

@app.route('/all')
def all():
    images = db['images']
    return jsonify(images)

@app.errorhandler(404)
def error404(e):
    return render_template('404.html')