from flask import Flask, render_template, flash, request, redirect, session
from pymongo import MongoClient
from config import Config
from bson.objectid import ObjectId

app=Flask(__name__)
app.secret_key=Config.SECRET_KEY

client=MongoClient(Config.MONGO_URI)
db=client["interntrack"]
users=db["users"]
products=db["products"]
skills=db["skills"]

#---------Login--------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        login_id=request.form.get("login_id")
        password=request.form.get("password")
        role=request.form.get("role")

        user=users.find_one({
            "loginId": login_id,
            "password": password,
            "role": role
        })

        if user:
            session["user"]=user.get("name")
            session["role"]=user.get("role")

            if role=="admin":
                return redirect("/admin")
            else:
                return redirect("/employee")

        flash("Invalid Login ID or Password", "danger")    
        return redirect("/")
    return render_template("login.html")

#------------Employee---------
@app.route("/employee")
def employee_dashboard():
    if session.get("role")!="employee":
        return redirect("/")
    return render_template("employee_dashboard.html", name=session.get("user"))

#-----------Add Product----------------
@app.route("/add-product")
def add_product():
    if session.get("role")!="employee":
        return redirect("/")
    
    apms=users.find({"position": "apm"})
    devs=users.find({"position": "developer"})

    return render_template("add_product.html", apms=apms, devs=devs)

#-----------Save Product--------------
@app.route("/save-product", methods=["POST"])
def save_product():
    product_name=request.form.get("product_name")
    apm=request.form.get("apm")
    developer=request.form.get("developer")

    db.products.insert_one({
        "product_name":product_name,
        "apm": apm,
        "developer": developer,
        "created_by":session.get("user"),
        "status": "pending"       
    })
    return redirect("/employee")

#--------Skill Page-------------------
@app.route("/add-skill")
def add_skill():
    if session.get("role")!="employee":
        return redirect("/")
    return render_template("add_skill.html")

#--------Save skill----------------
@app.route("/save-skill", methods=["POST"])
def save_skill():
    skill=request.form.get("skill")

    db.skills.insert_one({
        "skill": skill,
        "user":session.get("user")
    })

    return redirect("/employee")

# -------- ALL DATA PAGE --------
@app.route("/all-data")
def all_data():
    if session.get("role") != "employee":
        return redirect("/")

    user = session.get("user")

    # Fetch only logged-in user data
    products = db.products.find({"created_by": user})
    skills = db.skills.find({"user": user})

    return render_template("all_data.html", products=products, skills=skills)

#-----Admin Dashboard-----------------
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/")

    all_users = users.find({"role": "employee"})

    return render_template("admin_dashboard.html", users=all_users)

#----Approve------------------
@app.route("/approve-product/<id>")
def approve_product(id):
    if session.get("role") != "admin":
        return redirect("/")

    products.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "approved"}}
    )
    return redirect(request.referrer or "/admin")

#----Reject---------------------------
@app.route("/reject-product/<id>")
def reject_product(id):
    if session.get("role") != "admin":
        return redirect("/")

    products.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "rejected"}}
    )
    return redirect(request.referrer or "/admin")

#-----Employee Detail (NEW PAGE)------
@app.route("/admin/user/<name>")
def admin_user_detail(name):
    if session.get("role") != "admin":
        return redirect("/")

    user_products = products.find({"created_by": name})
    user_skills = skills.find({"user": name})

    return render_template("admin_user_detail.html",
                           name=name,
                           products=user_products,
                           skills=user_skills)

#---------Logout------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)