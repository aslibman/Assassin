from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from databases import register, authenticate, getInfoByUser, getInfoByID
from pymongo import MongoClient
from werkzeug import secure_filename
from functools import wraps
import os

c = MongoClient("localhost", 27017)
db = c.userbase
collection = db.usercollection

app = Flask('__name__')

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

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
	result = register(user,password,password2,name)
	if result[0]:
            session["username"] = user
            return redirect(url_for("home"))
	else:
            return render_template("register.html",message=result[1])
    return render_template("register.html")

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
	file = request.files['file']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return redirect(url_for('uploaded_file',
                                filename=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/about", methods = ["POST" , "GET"])
def about():
	return render_template("about.html")

##@app.route ("/facerecog", methods = ["POST" , "GET"])

if __name__=="__main__":
    app.debug = True
    app.secret_key = 'dfjahdjhbdjf,lnhmdfnm'
    app.run()
