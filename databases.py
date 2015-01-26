from pymongo import Connection
import random, os, base64, string
from faceapi import kairosapiDETECT, kairosapiENROLL
#from PIL import Image
conn = Connection()
db = conn['game']

upload_folder = "static/uploads/"
allowedExtensions = ['png', 'jpg']
allowedChars = string.letters + string.digits
#maxPicSize = 4 * 1024 * 1024
#defaultImg = "null.jpeg"

### FILE FUNCTIONS
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowedExtensions

def uploadFile(file,name):
    if not file:
        return (False,"No image selected.")
    if not allowed_file(file.filename):
        return (False,"File is of wrong type. (Jpg and Png are supported)")
    fileExtension = file.filename.split(".")[-1]
    fileSave = name + "." + fileExtension
    file.save(os.path.join(upload_folder, fileSave))
    if kairosapiDETECT(upload_folder+fileSave)==False:
        return (False, "Please upload a picture with a face in it.")
    return (True,"File successfully uploaded.",fileSave)

#def processImg(imgPath):
#    img = Image.open(imgPath)
#    exif = img._getexif()
#    if exif:
#        if orientation_key in exif:
#            orientation = exif[orientation_key]
#            rotate_values = {3:180, 6:270, 8:90}
#            if orientation in rotate_values:
#                image = image.rotate(rotate_values[orientation])
#                img.save(imgPath, quality = 100)
        
### PLAYER FUNCTIONS
def register(user,pword,pword2,name,file):
    user = user.lower()
    if user == "":
        return (False,"Please enter a username.")
    if len(user) > 15 or len(user) < 4:
        return (False,"Username must be between 4 and 15 characters long.")
    if False in [c in allowedChars for c in user]:
        return (False,"Username can only contain letters and numbers.")
    if next(db.users.find({"user":user}),None) != None:
        return (False,"The username entered is already registered.")
    if pword == "" or pword2 == "":
        return (False,"No password entered in one or more of the fields.")
    if pword != pword2:
        return (False,"The passwords entered do not match.")
    v = validPassword(pword)
    if not v[0]:
        return v
    pword = base64.b64encode(pword)
    if name == "":
        return (False,"No name entered.")
    num = next(db.users.find({},{"password":False},sort=[("num",-1)]),None)
    if num == None: #Sets an ID for newly created accounts
        i = 1
    else:
        i = num["num"] + 1
    f = uploadFile(file,user)
    if not f[0]:
        return f
    fileExtension = file.filename.split(".")[-1]
    fileSave = user + "." + fileExtension
    list = [{"user":user,"password":pword,"name":name,"num":i,"pic":fileSave,"game":0,"stats":{"kills":0,"deaths":0,"gamesPlayed":0,"gamesWon":0},"loc":{"lat":0,"lng":0},"request":0}]        
    db.users.insert(list)
    kairosapiENROLL(upload_folder+fileSave,user)
    return (True,"Successfully registered.")

def changeProfile(user,path):
    db.users.update({"user":user},{"$set":{"pic":path}})
    
def validPassword(pword):
    if len(pword) == 0:
        return (False,"Password cannot be blank.")
    if len(pword) > 15 or len(pword) < 5:
        return (False,"Password must be between 5 and 15 characters long.")
    return (True,"Password valid.")
    
def changePassword(user,current,pword1,pword2):
    r = authenticate(user,current)
    if not r[0]:
        return r
    if pword1 != pword2:
        return (False,"The new passwords entered do not match.")
    v = validPassword(pword1)
    if not v[0]:
        return v
    pword = base64.b64encode(pword)
    db.users.update({"user":user},{"$set":{"password":pword1}})
    return (True,"Password changed successfully.")
    
def authenticate(user,pword):
    if user == "":
        return (False,"Please enter your username.")
    if pword == "":
        return (False,"Please enter your password.")
    if next(db.users.find({"user":user}),None) == None:
        return (False,"No such username is registered.")
    pword = base64.b64encode(pword)
    if next(db.users.find({"user":user,"password":pword}),None) == None:
        return (False,"Incorrect password.")
    return (True,"Successfully logged in.")

def getInfoByUser(user):
    return next(db.users.find({"user":user},{'password':False}),None)

def getInfoByID(n):
    return next(db.users.find({"num":n},{'password':False}),None)

def getTarget(playerID):
    t = getInfoByID(playerID)["game"]
    if t != 0 and getGame(t)["started"]:
        return getInfoByID(getGame(t)["players"][str(playerID)])
    else:
        return None

def killTarget(playerID): #kills the target of player with given ID
    playerStats = getInfoByID(playerID)["stats"]
    playerStats["kills"] += 1
    target = getTarget(playerID)
    targetID = target["num"]
    targetStats = target["stats"]
    targetStats["deaths"] += 1
    targetStats["gamesPlayed"] += 1
    newTargetID = getTarget(targetID)["num"]
    game = getInfoByID(playerID)["game"]
    if newTargetID == playerID:
        playerStats["gamesPlayed"] += 1
        playerStats["gamesWon"] += 1
        deleteGame(game)
    else:
        gamePlayers = getGame(game)["players"]
        gamePlayers[str(playerID)] = newTargetID
        gamePlayers.pop(str(targetID))
        db.games.update({"num":game},{"$set":{"players":gamePlayers}})
    db.users.update({"num":playerID},{"$set":{"stats":playerStats}})
    db.users.update({"num":targetID},{"$set":{"stats":targetStats,"game":0}})

def inGame(playerID):
    return not getInfoByID(playerID)["game"] == 0

def leaveGame(playerID):
    player = getInfoByID(playerID)
    game = getGame(player["game"])
    if game["host"] != playerID:
        playerList = game["players"]
        if game["started"]:
            leaverTarget = playerList.pop(str(playerID))
            for p in playerList.keys():
                if playerList[p] == playerID:
                    playerList[p] = leaverTarget
        else:
            playerList.pop(str(playerID))
        db.games.update({"num":game["num"]},{"$set":{"players":playerList}})
        db.users.update({"num":playerID},{"$set":{"game":0}})
    else:
        deleteGame(game["num"])

def isHost(playerID):
    player = getInfoByID(playerID)
    game = player["game"]
    return game != 0 and getGame(game)["host"] == playerID

def updateLocation(playerID,lat,lng):
    db.users.update({"num":playerID},{"$set":{"loc":{"lat":lat,"lng":lng}}})

def sendManualRequest(playerID):
    target = getTarget(playerID)
    db.users.update({"num":target["num"]},{"$set":{"request":playerID}})

def answerRequest(playerID,answer):
    player = getInfoByID(playerID)
    if answer:
        killTarget(player["request"])
    db.users.update({"num":playerID},{"$set":{"request":0}})
    
### GAME FUNCTIONS
def createGame(hostID,description,private=False):
    nums = [i["num"] for i in db.games.find({})]
    nums.append(0)
    n = max(nums)
    host = getInfoByID(hostID)
    gameName = host["user"] + "'s game"
    game = [{"num":n+1,"host":hostID,"name":gameName,"description":description,"private":private,"players":{},"started":False}]
    db.games.insert(game)
    joinGame(n+1,hostID)
    return n + 1
	
def getGame(gameID):
    return db.games.find_one({"num":gameID})

def joinGame(gameID,playerID):
    gamePlayers = getGame(gameID)["players"]
    gamePlayers[str(playerID)] = 0
    db.games.update({"num":gameID},{"$set":{"players":gamePlayers}})
    db.users.update({"num":playerID},{"$set":{"game":gameID}})

def deleteGame(gameID):
    game = getGame(gameID)
    for player in game["players"].keys():
        db.users.update({"num":int(player)},{"$set":{"game":0}})
    db.games.remove({"num":gameID})
        
def assignTargets(gameID):
    game = getGame(gameID)["players"]
    n = game.keys()
    random.shuffle(n)
    for a in range(len(n) - 1):
        game[n[a]] = int(n[a+1])
    game[n[len(n)-1]] = int(n[0])
    db.games.update({"num":gameID},{"$set":{"players":game,"started":True}})
    
def countPlayers(gameID):
    game = getGame(gameID)
    return len(game["players"])

#used to get list of players other than host in a game
def getPlayers(gameID):
    game = getGame(gameID)
    players = game["players"]
    players.pop(str(game["host"]))
    return [getInfoByID(int(i)) for i in players.keys()]
    
if __name__ == "__main__":
    print "Clearing the databases"
    db.users.drop()
    db.games.drop()
