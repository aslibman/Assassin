from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from databases import *
from functools import wraps
from faceapi import kairosapiENROLL, kairosapiRECOGNIZE, kairosapiREMOVESUBJECT, kairosapiDETECT, kairosapiVIEW
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
    manualRequest = playerInfo["request"] != 0
    
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        elif request.form["b"] == "Settings":
            return redirect(url_for("settings"))
        elif request.form["b"] == "Create":
            description = request.form["entry"]
            match = createGame(ID, description)
            return redirect(url_for("home"))
        elif request.form["b"] == "Leave Game":
            leaveGame(ID)
            return redirect(url_for("home"))
        elif request.form["b"] == "Start":
            assignTargets(playerInfo["game"])
            return redirect(url_for("home"))
        elif request.form["b"] == "Yes":
            answerRequest(ID,True)
            return redirect(url_for("home"))
        elif request.form["b"] == "No":
            answerRequest(ID,False)
            return redirect(url_for("home"))
        else:
            leaveGame(int(request.form["b"]))
            return redirect(url_for("home"))
       ## target = getTarget(ID)
    gameSize = 0
    playerList = []
    if canStartGame:
        gameSize = countPlayers(game["num"])
        playerList = getPlayers(game["num"])
    return render_template("home.html",playerInGame=playerInGame, user=user, game=game, target=target, canStartGame=canStartGame,gameSize=gameSize,playerList=playerList, manualRequest=manualRequest)
	

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
    message=""
    player = getInfoByUser(session["username"])
    ID = player["num"]
    game = player["game"]
    gameStarted = False
    manualConfirm = False
            
    lat = json.loads(json.dumps(request.args.get("latitude")))
    lng = json.loads(json.dumps(request.args.get("longitude")))
    if lat != None and lng != None:
        updateLocation(ID,float(lat),float(lng))
        
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
        if request.form["b"] == "Confirm":
            #victor's stuff
            targetUser = getTarget(ID)["user"]
            f = request.files["f"]
            f = uploadFile(f,targetUser+"TARGET")
            if f[0]:
                path = "static/uploads/" + f[2]
                processImg(path)
                if kairosapiDETECT(path):
                    if targetUser in kairosapiRECOGNIZE(path):
                        killTarget(ID)
                        return redirect(url_for("home"))
                    else:
                        message="Face recognition did not match."
                        manualConfirm=True
                else:
                    message= "No face in the photo detected."
                    manualConfirm=True
        if request.form["b"] == "Manual Confirm":
            sendManualRequest(ID)
            message="A request for manual confirmation has been sent to your target."
                
    if game != 0 and getGame(game)["started"]:
        gameStarted = True
        target = getTarget(ID)
        targetJSON = getTarget(ID);
        targetLat = targetJSON["loc"]["lat"];
        targetLng = targetJSON["loc"]["lng"];
        return render_template("target.html",targetLng=targetLng, targetLat=targetLat, target=target,gameStarted=gameStarted,message=message,manualConfirm=manualConfirm)
    
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
                return render_template("search.html", alert=True)
            else:
                return redirect(url_for("profile",username=result["user"]))
    return render_template("search.html")
        

@app.route('/settings', methods=['GET', 'POST'])
@loginRequired
def settings():
    user = session["username"]
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            logout()
            return redirect(url_for("login"))
        if request.form["b"] == "Settings":
            return redirect(url_for("settings"))
        if request.form["b"] == "Cancel":
            return render_template("settings.html")
        if request.form["b"] == "Change Profile":
            f = request.files["f"]
            upload = uploadFile(f,user)
            if upload[0]:
                changeProfile(user,upload[2])
            return render_template("settings.html",message=upload[1])
        if request.form["b"] == "Change":
            current = request.form["current"]
            pword1 = request.form["new"]
            pword2 = request.form["newConfirm"]
            change = changePassword(user,current,pword1,pword2)
            return render_template("settings.html",message=change[1])
            
                
    return render_template("settings.html")

@app.route('/recognition',methods=["GET","POST"])
def recognition():
    if request.method == "POST":
        if request.form["b"] == "Enroll":
            kairosapiENROLL("photos/Bleh.JPG","victorgaitour")
        if request.form["b"] == "Check":
            #kairosapiCHECK()
            kairosapiRECOGNIZE("photos/Bleh2.JPG")
        if request.form["b"] == "seeifface":
            kairosapiDETECT("photos/ball.jpg")
        if request.form["b"] == "remove":
            kairosapiREMOVESUBJECT("victorgaitour")
        if request.form["b"] == "listall":
            kairosapiVIEW("Assassin")
    return render_template("recognition.html")


if __name__=="__main__":
    app.debug = True
    app.run()
