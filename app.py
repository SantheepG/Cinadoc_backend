# Importing necessary libraries
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import bcrypt
from io import BytesIO
import requests
import numpy as np 
from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model
import keras.utils as image
from pymongo import MongoClient
import dropbox


# Dropbox setup
dbx = dropbox.Dropbox('sl.Bb1pSqO57eJySB0belLvdavZhKfa6d23BC2YeMzV0kK-Rdu5piYv7j3s5bsyKFA06VW9EVzulEfk60YcYEGFiTI92u2m5xc-jDfVBlTFpwojDT1psFADI2jxaiEZGQ5L3vdAfBvdBt6X')

# Setting up mongodb
app = Flask(__name__) 
app.secret_key = "cinadoc"
app.config['MONGO_URI'] = "mongodb+srv://gshantheep:cinadoc@cluster0.cz7xwta.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(app.config['MONGO_URI'])
db = client.get_database('Users')
collection = db.get_collection('user')
mongo = PyMongo(app)

# User registeration
@app.route('/register',methods=['POST'])

def register_user():   
    _json = request.json
    _name = _json['name']
    _email = _json['email']
    _phone = _json['phone']
    _encrypted_pswd = bcrypt.hashpw(_json['pwd'].encode('utf-8'), bcrypt.gensalt()) # Pswd encryption

    existing_user = collection.find_one({'name': _name})

    try:
        if _name and _email and _encrypted_pswd and _phone and request.method == 'POST':
            if existing_user:
                response = jsonify("Username already taken")
                response.status_code = 404
                return response
            else:
                id = collection.insert_one({'name':_name, 'email':_email, 'phone':_phone, 'pwd':_encrypted_pswd })
                response = jsonify("User created successfully!")
                response.status_code = 200
                return response   
        else:
            response = jsonify("Required fields are empty")
            response.status_code = 404
            return response   
    except:
        return jsonify("Something went wrong. Please try again")
    
# User login
@app.route('/login')
def login():

    _json = request.json
    username = _json['name']
    password = _json['pwd']

    if username and password :
        try:
            user = collection.find_one({'name':username})
            if bcrypt.checkpw(password.encode('utf-8'), user['pwd']):
                return jsonify("Login success")
            else:
                return jsonify("Incorrect username or password")
        except:
            return jsonify("Incorrect username or password")  
    else:
        return jsonify("Required fields are empty")

# Prediction
model = load_model('acc73.h5')
model.make_predict_function()

def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(255,255))
    x = image.img_to_array(img)
    x = np.expand_dims(img, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    return preds

# Uploading img to dropbox
def upload_to_dropbox(file_stream, file_name):
    try:
        dbx.files_upload(file_stream.read(), '/' + file_name)
        shared_link_metadata = dbx.sharing_create_shared_link('/' + file_name)
        shared_link_url = shared_link_metadata.url
        return shared_link_url.replace('?dl=0', '?dl=1')
    except:
        return jsonify("Image upload unsuccessful. Please try again")

# Img upload & classification    
@app.route('/predict',methods=['GET','POST'])
def predict():

    if request.method == 'POST':
        try:
            file = request.files['image']
            file_stream = file.stream
            file_name = file.filename
            # URL of the image
            shared_link = upload_to_dropbox(file_stream, file_name)
            # Get the content of the URL using requests
            response = requests.get(shared_link)  
            preds = model_predict(BytesIO(response.content), model)
            predicted_label = np.argmax(preds)
            if predicted_label == 0:
                return jsonify("Rough Bark")
            else:
                return jsonify("Stripe canker") 
        except:
            return jsonify("Image upload unsuccessful. Please try again")
        

if __name__ == "__main__":
    app.run(debug=True)






