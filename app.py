from flask import Flask, render_template, jsonify, request, redirect, url_for
from random import randint
import uuid
from passlib.hash import pbkdf2_sha256
import pymongo
import datetime

app = Flask(__name__)

# database connection setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["blood_bucket"]
users = db["users"]

authUser = {
    "name": "",
    "email": "",
    "phone": "",
    "bloodGroup": "",
    "lastDonation": "",
}
# login and signup
class User:
    def signup(self):
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "phone": request.form.get("phone"),
            "bloodGroup": request.form.get("bloodGroup"),
            "lastDonation": request.form.get("lastDonation"),
        }
        if users.find_one({"email": user["email"]}):
            return "Email already exists"
        if user["password"] != request.form.get("repassword"):
            return "Password do not match"
        user["password"] = pbkdf2_sha256.hash(user["password"])
        print(user)
        users.insert_one(user)
        return 200

    def login(self):
        user = {
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }
        if not users.find_one({"email": user["email"]}):
            return "Invalid email or password"
        if pbkdf2_sha256.verify(
            user["password"], users.find_one({"email": user["email"]})["password"]
        ):
            temp = users.find_one({"email": user["email"]}, {"_id": 0, "password": 0})
            authUser["name"] = temp["name"]
            authUser["email"] = temp["email"]
            authUser["phone"] = temp["phone"]
            authUser["bloodGroup"] = temp["bloodGroup"]
            authUser["lastDonation"] = temp["lastDonation"]
            return 200
        else:
            return "Invalid email or password"

    def logout(self):
        authUser["name"] = ""
        authUser["email"] = ""
        authUser["phone"] = ""
        authUser["bloodGroup"] = ""
        authUser["lastDonation"] = ""

        return redirect("/", code=302)

    def update_info(self, name, email, phone, bloodGroup, lastDonation):
        if email != authUser["email"]:
            if users.find_one({"email": email}):
                return "Email already exists"
        users.update_one(
            {"email": authUser["email"]},
            {
                "$set": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "bloodGroup": bloodGroup,
                    "lastDonation": lastDonation,
                }
            },
        )
        authUser["name"] = name
        authUser["email"] = email
        authUser["phone"] = phone
        authUser["bloodGroup"] = bloodGroup
        authUser["lastDonation"] = lastDonation

        return 200


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        if User().login() == 200:
            return redirect("/", code=302)
        else:
            error = User().login()
            return render_template("login.html", error=error)
    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""
    if request.method == "POST":
        if User().signup() == 200:
            return redirect("/login", code=302)
        else:
            error = User().signup()
            print(error)
            return render_template("signup.html", error=error)
    return render_template("signup.html", error=error)


@app.route("/logout")
def logout():
    return User().logout()


# others
@app.route("/")
def index():
    return render_template("index.html", name=authUser["name"], email=authUser["email"])


@app.route("/user-info")
def userInfo():
    nextDonation = datetime.datetime.strptime(
        authUser["lastDonation"], "%Y-%m-%d"
    ) + datetime.timedelta(days=90)
    timeRemaining = nextDonation - datetime.datetime.now()
    if timeRemaining.days < 0:
        timeRemaining = datetime.timedelta(days=0)

    return render_template(
        "user-info.html",
        name=authUser["name"],
        email=authUser["email"],
        phone=authUser["phone"],
        bloodGroup=authUser["bloodGroup"],
        lastDonation=authUser["lastDonation"],
        nextDonation=nextDonation.date(),
        timeRemaining=timeRemaining.days,
    )


@app.route("/update-user-info", methods=["GET", "POST"])
def updateUserInfo():
    error = ""
    if request.method == "POST":
        error = User().update_info(
            request.form.get("name"),
            request.form.get("email"),
            request.form.get("phone"),
            request.form.get("bloodGroup"),
            request.form.get("lastDonation"),
        )
        if error == 200:
            return redirect("/user-info", code=302)
        else:
            return render_template(
                "update-user-info.html",
                error=error,
                name=authUser["name"],
                email=authUser["email"],
                phone=authUser["phone"],
                bloodGroup=authUser["bloodGroup"],
                lastDonation=authUser["lastDonation"],
            )
    return render_template(
        "update-user-info.html",
        error=error,
        name=authUser["name"],
        email=authUser["email"],
        phone=authUser["phone"],
        bloodGroup=authUser["bloodGroup"],
        lastDonation=authUser["lastDonation"],
    )


@app.route("/donner")
def donner():
    days = datetime.datetime.now() - datetime.timedelta(days=90)
    d = str(days.strftime("%Y-%m-%d"))
    print(d)
    result = users.find(
        {
            "lastDonation": {
                "$lt": d,
            },
        },
        {"_id": 0, "password": 0, "email": 0, "phone": 0},
    )

    return render_template(
        "donner.html",
        name=authUser["name"],
        email=authUser["email"],
        result=result,
    )


if __name__ == "__main__":
    app.run(debug=True)
