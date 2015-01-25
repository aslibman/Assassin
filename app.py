from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from databases import register, authenticate, getInfoByUser, getInfoByID, inGame, getTarget, createGame, getGame, leaveGame, assignTargets, updateLocation, joinGame, countPlayers, isHost, killTarget
from functools import wraps
from faceapi import kairosapiENROLL, kairosapiRECOGNIZE, kairosapiREMOVESUBJECT, kairosapiDETECT
import json
app = Flask('__name__')
app.config['SECRET_KEY'] = "change this"

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
    canStartGame = isHost(ID) and countPlayers(game["num"]) > 1 and not game["started"]
    target = getTarget(ID)
    
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
        if request.form["b"] == "Start":
			assignTargets(playerInfo["game"])
       ## target = getTarget(ID)
    return render_template("home.html",playerInGame=playerInGame, user=user, game=game, target=target, canStartGame=canStartGame)
	

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
@app.route('/profile/', methods=['GET', 'POST'])
@app.route('/profile/<username>', methods=['GET', 'POST'])
@loginRequired
def profile(username=None):
    if username == None:
        result = getInfoByUser(session['username'])
    else:
        result = getInfoByUser(username)
        if result == None:
            return "No such user found" #needs template
    user = session["username"]
    playerInfo = getInfoByUser(user)
    ID = playerInfo["num"]
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
        if request.form["b"] == "Join Game":
            joinGame(result["game"], ID)
            return redirect(url_for("home"))
			
        
    host = ""
    description = ""
    inGame = False
    if result["game"] != 0:
        inGame = True
        game = getGame(result["game"])
        host = getInfoByID(game["host"])["user"]
        description = game["description"]
    canJoinGame = getInfoByUser(session["username"])["game"] == 0
    return render_template("profile.html",result=result,inGame=inGame,host=host,description=description,canJoinGame=canJoinGame)

@app.route('/target', methods=['GET', 'POST'])
@loginRequired
def target():
    player = getInfoByUser(session["username"])
    ID = player["num"]
    game = player["game"]
    gameStarted = False
            
    lat = json.loads(json.dumps(request.args.get("latitude")))
    lng = json.loads(json.dumps(request.args.get("longitude")))
    if lat != None and lng != None:
        updateLocation(ID,float(lat),float(lng))
        
    if game != 0 and getGame(game)["started"]:
        gameStarted = True
        target = getTarget(ID)
        targetJSON = getTarget(ID);
        targetLat = targetJSON["loc"]["lat"];
        targetLng = targetJSON["loc"]["lng"];
        return render_template("target.html",targetLng=targetLng, targetLat=targetLat, target=target,gameStarted=gameStarted)
        
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
        if request.form["b"] == "Confirm":
            #grab img and compare using API (use uploadFile to upload if needed)
            if True:#victors stuff
                killTarget(ID)
    return render_template("target.html",gameStarted=gameStarted)

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
                return redirect(url_for("profile",username=result["user"]))
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
        if request.form["b"] == "seeifface":
            kairosapiDETECT("photos/ball.jpg")
    return render_template("recognition.html")


if __name__=="__main__":
    app.debug = True
    app.run()
