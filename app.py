from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from databases import register, authenticate, getInfoByUser, getInfoByID, inGame, getTarget, createGame, getGame, leaveGame, assignTargets
from werkzeug import secure_filename
from functools import wraps
import os
import faceapi
app = Flask('__name__')


def loginRequired(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if "username" in session:
            return func(*args,**kwargs)
        else:
            return redirect(url_for("login",next=request.url))
    return inner

def redirectIfLoggedIn(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if "username" in session:
            return redirect(url_for("home"))
        else:
            return func(*args,**kwargs)
    return inner

def logout():
    session.pop("username",None)

@app.route ("/home", methods = ["POST" , "GET"])
@loginRequired
def home():
    user = session["username"]
    playerInfo = getInfoByUser(user)
    ID = playerInfo["num"]
    playerInGame = inGame(ID)
    game = getGame(playerInfo["game"])
    
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
        if request.form["b"] == "Create":
            description = request.form["entry"]
            match = createGame(ID, description)
            return redirect(url_for("home"))
        if request.form["b"] == "Leave Game":
            leaveGame(ID)
            return redirect(url_for("home"))
       ## target = getTarget(ID)
    return render_template("home.html",playerInGame=playerInGame, user=user, game=game)
	

@app.route("/",methods = ["POST","GET"])
@app.route ("/login", methods = ["POST" , "GET"])
@redirectIfLoggedIn
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
@redirectIfLoggedIn
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
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
    return render_template("profile.html", name="jesus")

@app.route('/target', methods=['GET', 'POST'])
@loginRequired
def target():
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
    return render_template("target.html")

@app.route('/search', methods=['GET', 'POST'])
@loginRequired
def search():
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
        if request.form["b"] == "Search":
            result = getInfoByUser(request.form["entry"])
            if result == None:
                return render_template("search.html", message="Username does not exist")
            else:
                return render_template("profile.html", name=result["user"], kills=result['stats']['kills'], deaths=result['stats']['deaths'], games=result['game'])
    return render_template("search.html")
        

@app.route('/settings', methods=['GET', 'POST'])
@loginRequired
def settings():
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
        if request.form["b"] == "Cancel":
            return render_template("settings.html")
    return render_template("settings.html")

@app.route('/recognition',methods=["GET","POST"])
def recognition():
    if request.method == "POST":
        if request.form["b"] == "Enroll":
            kairosapiENROLL("photos/me.jpg","name")
        if request.form["b"] == "Check":
            #kairosapiCHECK()
            kairosapiRECOGNIZE("photos/Firefox_wallpaper.png")
    return render_template("recognition.html")


if __name__=="__main__":
    app.debug = True
    app.secret_key = 'dfjahdjhbdjf,lnhmdfnm'
    app.run()
