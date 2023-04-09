from app import app
import pytest
import io
from PIL import Image
import json
        
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_register(client):
    # Make a POST request to the Flask server
    data={"name":"name", "email":"email", "phone":"phone", "pwd" : "pwd"}
    json_data = json.dumps(data)
    response = client.post('/register', data=json_data, headers={'content-type': 'application/json'})
    # Check the response & status code
    assert b"User created successfully!" 
    assert response.status_code == 200

def test_false_register(client):
    # Make a POST request to the Flask server
    data={"name":None, "email":"email", "phone":None, "pwd" : "pwd"}
    json_data = json.dumps(data)
    response = client.post('/register', data=json_data, headers={'content-type': 'application/json'})
    # Check the response & status code
    assert b"Required fields are empty" 
    assert response.status_code == 400    

def test_login(client):
    # Make a POST request to the Flask server
    data={"name":"kevin", "pwd" : "1@!45"}
    json_data = json.dumps(data)
    response = client.post('/login', data=json_data, headers={'content-type': 'application/json'})
    # Check the response & status code
    assert b"Login success"
    assert response.status_code == 200

def test_false_login_pswd(client):
    data={"name":"kevin", "pwd" : "1234"}
    json_data = json.dumps(data)
    response = client.post('/login', data=json_data, headers={'content-type': 'application/json'})
    assert b"Incorrect username or password"
    assert response.status_code == 400
