from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from databases import register, login, getInfoByUser, getInfoByID
from pymongo import MongoClient
from werkzeug import secure_filename
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


@app.route ("/home", methods = ["POST" , "GET"])
def home():
    return render_template("home.html")

@app.route("/",methods = ["POST","GET"])
@app.route ("/login", methods = ["POST" , "GET"])
def loginPage():
    if request.method == "POST":
        user = request.form["username"]
        pword = request.form["password"]
        l = login(user,pword)
        if l[0]:
            return redirect(url_for("home"))
        else:
            return render_template("login.html", message=l[1])
    return render_template("login.html")
	
@app.route ("/register", methods = ["GET"])
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
		render_template("register.html",message=message)

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
