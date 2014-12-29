from flask import Flask, render_template, request, redirect, url_for
from databases import register, login, getInfoByUser, getInfoByID
from pymongo import MongoClient

c = MongoClient("localhost", 27017)
db = c.userbase
collection = db.usercollection

app = Flask('__name__')

@app.route("/",methods = ["POST","GET"])
@app.route ("/home", methods = ["POST" , "GET"])
def home():
    return render_template("home.html")

@app.route ("/login", methods = ["POST" , "GET"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pword = request.form["password"]
        l = login(user,pword)
        if l[0]:
            return redirect(url_for("home"))
        else:
            return render_template("login.html", message=l[1])
    return render_template("login.html")
	
@app.route ("/register", methods = [ "GET"])
def display_register():
	return render_template("register.html")
	
@app.route ("/register", methods = ["POST"])
def registration():
	x = {}
	
	first_name = request.form["first_name"]
	last_name = request.form["last_name"]
	name = first_name + " " + last_name
	username = request.form["username"]
	password = request.form["password"]
	password2 = request.form["password_confirm"]
	result, message=register(username,password,password2,name)
	if result == True:
		return render_template("home.html")
	else:
		render_template("register.html")

	

@app.route("/about", methods = ["POST" , "GET"])
def about():
	return render_template("about.html")

##@app.route ("/facerecog", methods = ["POST" , "GET"])

if __name__=="__main__":
    app.debug = True
    app.secret_key = 'dfjahdjhbdjf,lnhmdfnm'
    app.run()
