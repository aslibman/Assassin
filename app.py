from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from databases import register, authenticate, getInfoByUser, getInfoByID
from werkzeug import secure_filename
from functools import wraps
import json
import os
from urllib2 import Request, urlopen
import base64

app = Flask('__name__')

def loginRequired(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if "username" in session:
            return func(*args,**kwargs)
        else:
            return redirect(url_for("login",next=request.url))
    return inner

def logout():
    session.pop("username",None)

@app.route ("/home", methods = ["POST" , "GET"])
@loginRequired
def home():
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
    return render_template("home.html")

@app.route("/",methods = ["POST","GET"])
@app.route ("/login", methods = ["POST" , "GET"])
def login():
    if request.method == "POST":
        if request.form["b"] == "Sign Up":
            return redirect(url_for("registration"))
        
        user = request.form["username"]
        pword = request.form["password"]
        l = authenticate(user,pword)
        if l[0]:
            session["username"] = user
            next = request.args.get("next",None)
            if (next != None):
                return redirect(next)
            else:
                return redirect(url_for("home"))
        else:
            return render_template("login.html", message=l[1])
    return render_template("login.html")	
	
@app.route ("/register", methods = ["GET", "POST"])
def registration():
    if request.method == "POST":
        if request.form["b"] == "Log In":
            return redirect(url_for("login"))
        
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        name = first_name + " " + last_name
        user = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password_confirm"]
        file = request.files["f"]
        result = register(user,password,password2,name,file)
        if result[0]:
            session["username"] = user
            return redirect(url_for("home"))
        else:
            return render_template("register.html",message=result[1])
    return render_template("register.html")

@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/about", methods = ["POST" , "GET"])
def about():
	return render_template("about.html")

@app.route('/profile', methods=['GET', 'POST'])
@loginRequired
def profile():
    return render_template("profile.html")

@app.route('/target', methods=['GET', 'POST'])
@loginRequired
def target():
    return render_template("target.html")

@app.route('/search', methods=['GET', 'POST'])
@loginRequired
def search():
    return render_template("search.html")

@app.route('/settings', methods=['GET', 'POST'])
@loginRequired
def settings():
    return render_template("settings.html")


@app.route('/recognition',methods=["GET","POST"])
def recognition():
    if request.method == "POST":
        if request.form["b"] == "Enroll":
            kairosapiENROLL("me.jpg")
        if request.form["b"] == "Check":
            #kairosapiCHECK()
            kairosapiRECOGNIZE("me.jpg")
    return render_template("recognition.html")

def kairosapiENROLL(facepath):
    with open(facepath,'rb') as img:
        encoded_img = base64.b64encode(img.read())
    values = """{
    "image": "%s",
    "subject_id": "METEST1",
    "gallery_name": "METEST1",
    "selector": "SETPOSE",
    "symmetricFill": "true"
    }"""% (encoded_img)
    print values
    

    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/enroll', data=values, headers=headers)

    response_body = urlopen(request).read()
    print response_body

def kairosapiRECOGNIZE(facepath):
    with open(facepath,'rb') as img:
        encoded_img = base64.b64encode(img.read())
    values = """
    {
    "image": "%s",
    "gallery_name": "METEST1"
    }
    """%(encoded_img)

    headers = {
    'Content-Type': 'application/json',
    'app_id': '8daad7aa',
    'app_key': '25bc262122ca09efa504f747c7c8cf8b'
    }
    request = Request('https://api.kairos.com/recognize', data=values, headers=headers)

    response_body = urlopen(request).read()
    print response_body

if __name__=="__main__":
    app.debug = True
    app.secret_key = 'dfjahdjhbdjf,lnhmdfnm'
    app.run()
