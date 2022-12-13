from flask import Flask, render_template, jsonify, request, redirect, url_for
from random import randint
import uuid
from passlib.hash import pbkdf2_sha256
import pymongo

app = Flask(__name__)

# database connection setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["blood_bucket"]
users = db["users"]

authUser={
    "name": "",
}

@app.route('/')
def index():
    if(authUser['name'] == ""):
        login = False
    else:
        login = True
    return render_template('index.html', name=authUser['name'], isLogin=login)

class User:
    def signup(self):
        user={
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "phone": request.form.get('phone'),
            "bloodGroup":request.form.get('bloodGroup'),
            "lastDonation": request.form.get('lastDonation'),
        }
        if(users.find_one({"email": user['email']})):
            return "Email already exists"
        if (user['password'] != request.form.get('repassword')):
            return "Password do not match"
        user['password'] = pbkdf2_sha256.hash(user['password'])
        users.insert_one(user)
        return 200

    def login(self):
        user={
            "email": request.form.get('email'),
            "password": request.form.get('password'),
        }
        if(not users.find_one({"email": user['email']})):
            return "Invalid email or password"
        if(pbkdf2_sha256.verify(user['password'], users.find_one({"email": user['email']})['password'])):
            authUser['name'] = users.find_one({"email": user['email']})['name']
            return 200
        else:
            return "Invalid email or password"

    def logout(self):
        authUser['name'] = ""
        return redirect("/", code=302)

        

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        if(User().login() == 200):
            return redirect("/", code=302)
        else:
            error = User().login()
            return render_template('login.html', error=error)
    return render_template('login.html', error=error)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        if(User().signup() == 200):
            return redirect("/login", code=302)
        else:
            error = User().signup()
            print(error)
            return render_template('signup.html', error=error)
    return render_template('signup.html', error=error)

if __name__ == "__main__":
    app.run(debug=True)
