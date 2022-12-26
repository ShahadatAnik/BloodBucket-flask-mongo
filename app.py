from flask import Flask, render_template, request, redirect
import uuid
from passlib.hash import pbkdf2_sha256
import pymongo
import datetime

app = Flask(__name__)

# database connection setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["blood_bucket"]
users = db["users"]
hospital = db["hospital"]

authUser = {
    "name": "",
    "email": "",
    "phone": "",
    "bloodGroup": "",
    "lastDonation": "",
}

authHospital = {
    "name": "",
    "email": "",
    "phone": "",
    "address": "",
    "city": "",
    "district": "",
    "bloodGroupAP": "",
    "bloodGroupAN": "",
    "bloodGroupBP": "",
    "bloodGroupBN": "",
    "bloodGroupABP": "",
    "bloodGroupABN": "",
    "bloodGroupOP": "",
    "bloodGroupON": "",
}


# login and signup For User
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
        error = User().login()
        if error != 200:
            return render_template("user/login.html", error=error)
        else:
            return redirect("/", code=302)
    return render_template("user/login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""
    if request.method == "POST":
        error = User().signup()
        if error != 200:
            return render_template("user/signup.html", error=error)
        else:
            return redirect("user/login", code=302)
    return render_template("user/signup.html", error=error)


@app.route("/logout")
def logout():
    return User().logout()


@app.route("/user-info")
def userInfo():
    nextDonation = datetime.datetime.strptime(
        authUser["lastDonation"], "%Y-%m-%d"
    ) + datetime.timedelta(days=90)
    timeRemaining = nextDonation - datetime.datetime.now()
    if timeRemaining.days < 0:
        timeRemaining = datetime.timedelta(days=0)

    return render_template(
        "user/user-info.html",
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
        if error != 200:
            return render_template(
                "user/update-user-info.html",
                error=error,
                name=authUser["name"],
                email=authUser["email"],
                phone=authUser["phone"],
                bloodGroup=authUser["bloodGroup"],
                lastDonation=authUser["lastDonation"],
            )
        else:
            return redirect("/user-info", code=302)
    return render_template(
        "user/update-user-info.html",
        error=error,
        name=authUser["name"],
        email=authUser["email"],
        phone=authUser["phone"],
        bloodGroup=authUser["bloodGroup"],
        lastDonation=authUser["lastDonation"],
    )


# login and signup For Hospital
class Hospital:
    def signup(self):
        hospital = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "phone": request.form.get("phone"),
            "address": request.form.get("address"),
            "city": request.form.get("city"),
            "district": request.form.get("district"),
            "bloodGroupAP": request.form.get("bloodGroupAP"),
            "bloodGroupAN": request.form.get("bloodGroupAN"),
            "bloodGroupBP": request.form.get("bloodGroupBP"),
            "bloodGroupBN": request.form.get("bloodGroupBN"),
            "bloodGroupABP": request.form.get("bloodGroupABP"),
            "bloodGroupABN": request.form.get("bloodGroupABN"),
            "bloodGroupOP": request.form.get("bloodGroupOP"),
            "bloodGroupON": request.form.get("bloodGroupON"),
        }
        if hospital.find_one({"email": hospital["email"]}):
            return "Email already exists"
        if hospital["password"] != request.form.get("repassword"):
            return "Password do not match"
        hospital["password"] = pbkdf2_sha256.hash(hospital["password"])
        print(hospital)
        hospital.insert_one(hospital)
        return 200

    def login(self):
        hospital = {
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }
        if not hospital.find_one({"email": hospital["email"]}):
            return "Invalid email or password"
        if pbkdf2_sha256.verify(
            hospital["password"],
            hospital.find_one({"email": hospital["email"]})["password"],
        ):
            temp = hospital.find_one(
                {"email": hospital["email"]}, {"_id": 0, "password": 0}
            )
            authHospital["name"] = temp["name"]
            authHospital["email"] = temp["email"]
            authHospital["phone"] = temp["phone"]
            authHospital["address"] = temp["address"]
            authHospital["city"] = temp["city"]
            authHospital["district"] = temp["district"]
            authHospital["bloodGroupAP"] = temp["bloodGroupAP"]
            authHospital["bloodGroupAN"] = temp["bloodGroupAN"]
            authHospital["bloodGroupBP"] = temp["bloodGroupBP"]
            authHospital["bloodGroupBN"] = temp["bloodGroupBN"]
            authHospital["bloodGroupABP"] = temp["bloodGroupABP"]
            authHospital["bloodGroupABN"] = temp["bloodGroupABN"]
            authHospital["bloodGroupOP"] = temp["bloodGroupOP"]
            authHospital["bloodGroupON"] = temp["bloodGroupON"]

            return 200

        else:
            return "Invalid email or password"

    def logout(self):
        authHospital["name"] = ""
        authHospital["email"] = ""
        authHospital["phone"] = ""
        authHospital["address"] = ""
        authHospital["city"] = ""
        authHospital["district"] = ""
        authHospital["bloodGroupAP"] = ""
        authHospital["bloodGroupAN"] = ""
        authHospital["bloodGroupBP"] = ""
        authHospital["bloodGroupBN"] = ""
        authHospital["bloodGroupABP"] = ""
        authHospital["bloodGroupABN"] = ""
        authHospital["bloodGroupOP"] = ""
        authHospital["bloodGroupON"] = ""

        return redirect("/", code=302)

    def update_info(
        self,
        name,
        email,
        phone,
        address,
        city,
        district,
        bloodGroupAP,
        bloodGroupAN,
        bloodGroupBP,
        bloodGroupBN,
        bloodGroupABP,
        bloodGroupABN,
        bloodGroupOP,
        bloodGroupON,
    ):
        if email != authHospital["email"]:
            if hospital.find_one({"email": email}):
                return "Email already exists"
        hospital.update_one(
            {"email": authHospital["email"]},
            {
                "$set": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "city": city,
                    "district": district,
                    "bloodGroupAP": bloodGroupAP,
                    "bloodGroupAN": bloodGroupAN,
                    "bloodGroupBP": bloodGroupBP,
                    "bloodGroupBN": bloodGroupBN,
                    "bloodGroupABP": bloodGroupABP,
                    "bloodGroupABN": bloodGroupABN,
                    "bloodGroupOP": bloodGroupOP,
                    "bloodGroupON": bloodGroupON,
                }
            },
        )
        authHospital["name"] = name
        authHospital["email"] = email
        authHospital["phone"] = phone
        authHospital["address"] = address
        authHospital["city"] = city
        authHospital["district"] = district
        authHospital["bloodGroupAP"] = bloodGroupAP
        authHospital["bloodGroupAM"] = bloodGroupAN
        authHospital["bloodGroupBP"] = bloodGroupBP
        authHospital["bloodGroupBN"] = bloodGroupBN
        authHospital["bloodGroupABP"] = bloodGroupABP
        authHospital["bloodGroupABN"] = bloodGroupABN
        authHospital["bloodGroupOP"] = bloodGroupOP
        authHospital["bloodGroupON"] = bloodGroupON
        return 200


@app.route("/login-hospital", methods=["POST"])
def loginHospital():
    error = ""
    if request.method == "POST":
        error = Hospital.login()
        if error != 200:
            return render_template("hospital/login-hospital.html", error=error)
        else:
            return redirect("/hospital-info", code=302)
    return render_template("hospital/login-hospital.html", error=error)


@app.route("/signup-hospital", methods=["POST"])
def signupHospital():
    error = ""
    if request.method == "POST":
        error = Hospital.signup()
        if error != 200:
            return render_template("hospital/signup-hospital.html", error=error)
        else:
            return redirect("/", code=302)
    return render_template("hospital/signup-hospital.html", error=error)


@app.route("/logout-hospital")
def logoutHospital():
    return Hospital.logout()


@app.route("/hospital-info")
def hospitalInfo():
    return render_template(
        "hospital-info.html",
        name=authHospital["name"],
        email=authHospital["email"],
        phone=authHospital["phone"],
        address=authHospital["address"],
        city=authHospital["city"],
        district=authHospital["district"],
        bloodGroupAP=authHospital["bloodGroupAP"],
        bloodGroupAN=authHospital["bloodGroupAN"],
        bloodGroupBP=authHospital["bloodGroupBP"],
        bloodGroupBN=authHospital["bloodGroupBN"],
        bloodGroupABP=authHospital["bloodGroupABP"],
        bloodGroupABN=authHospital["bloodGroupABN"],
        bloodGroupOP=authHospital["bloodGroupOP"],
        bloodGroupON=authHospital["bloodGroupON"],
    )


@app.route("/update-hospital-info", methods=["POST"])
def updateHospital():
    error = ""
    if request.method == "POST":
        error = Hospital.update_info(
            request.form.get("name"),
            request.form.get("email"),
            request.form.get("phone"),
            request.form.get("address"),
            request.form.get("city"),
            request.form.get("district"),
            request.form.get("bloodGroupAP"),
            request.form.get("bloodGroupAN"),
            request.form.get("bloodGroupBP"),
            request.form.get("bloodGroupBN"),
            request.form.get("bloodGroupABP"),
            request.form.get("bloodGroupABN"),
            request.form.get("bloodGroupOP"),
            request.form.get("bloodGroupON"),
        )
        if error != 200:
            return render_template(
                "hospital/update-hospital.html",
                error=error,
                name=authHospital["name"],
                email=authHospital["email"],
                phone=authHospital["phone"],
                address=authHospital["address"],
                city=authHospital["city"],
                district=authHospital["district"],
                bloodGroupAP=authHospital["bloodGroupAP"],
                bloodGroupAN=authHospital["bloodGroupAN"],
                bloodGroupBP=authHospital["bloodGroupBP"],
                bloodGroupBN=authHospital["bloodGroupBN"],
                bloodGroupABP=authHospital["bloodGroupABP"],
                bloodGroupABN=authHospital["bloodGroupABN"],
                bloodGroupOP=authHospital["bloodGroupOP"],
                bloodGroupON=authHospital["bloodGroupON"],
            )
        else:
            return redirect("/hospital-info", code=302)

    return render_template(
        "hospital/update-hospital.html",
        error=error,
        name=authHospital["name"],
        email=authHospital["email"],
        phone=authHospital["phone"],
        address=authHospital["address"],
        city=authHospital["city"],
        district=authHospital["district"],
        bloodGroupAP=authHospital["bloodGroupAP"],
        bloodGroupAN=authHospital["bloodGroupAN"],
        bloodGroupBP=authHospital["bloodGroupBP"],
        bloodGroupBN=authHospital["bloodGroupBN"],
        bloodGroupABP=authHospital["bloodGroupABP"],
        bloodGroupABN=authHospital["bloodGroupABN"],
        bloodGroupOP=authHospital["bloodGroupOP"],
        bloodGroupON=authHospital["bloodGroupON"],
    )


# others
@app.route("/")
def index():
    return render_template(
        "index.html",
        name=authUser["name"],
        email=authUser["email"],
        hospitalName=authHospital["name"],
        hospitalEmail=authHospital["email"],
    )


@app.route("/donner", methods=["GET", "POST"])
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
    ).sort([("bloodGroup", pymongo.ASCENDING), ("lastDonation", pymongo.DESCENDING)])

    if request.method == "POST":
        donner_name_or_blood_group = request.form.get("donner_name_or_blood_group")
        result = users.find(
            {
                "$or": [
                    {"name": {"$regex": donner_name_or_blood_group, "$options": "i"}},
                    {
                        "bloodGroup": {
                            "$regex": donner_name_or_blood_group,
                            "$options": "i",
                        }
                    },
                ],
                "lastDonation": {
                    "$lt": d,
                },
            },
            {"_id": 0, "password": 0, "email": 0, "phone": 0},
        ).sort(
            [("bloodGroup", pymongo.ASCENDING), ("lastDonation", pymongo.DESCENDING)]
        )
        # result_count = users.find(
        #     {
        #         "$or": [
        #             {"name": {"$regex": donner_name_or_blood_group, "$options": "i"}},
        #             {
        #                 "bloodGroup": {
        #                     "$regex": donner_name_or_blood_group,
        #                     "$options": "i",
        #                 }
        #             },
        #         ],
        #         "lastDonation": {
        #             "$lt": d,
        #         },
        #     },
        #     {"_id": 0, "password": 0, "email": 0, "phone": 0},
        # ).count()
        # print(result_count)

    return render_template(
        "donner/donner.html",
        name=authUser["name"],
        email=authUser["email"],
        hospitalName=authHospital["name"],
        hospitalEmail=authHospital["email"],
        result=result,
    )


@app.route("/donner/<name>")
def donnerInfo(name):
    result = users.find_one(
        {
            "name": name,
        },
        {"_id": 0, "password": 0},
    )
    return render_template(
        "donner/donner-info.html",
        name=authUser["name"],
        email=authUser["email"],
        hospitalName=authHospital["name"],
        hospitalEmail=authHospital["email"],
        donner=result,
    )


if __name__ == "__main__":
    app.run(debug=True)
