from pymongo import Connection
import random
import os

conn = Connection()
db = conn['game']

upload_folder = "uploads/"
allowedExtensions = ['png', 'jpg']
maxPicSize = 4 * 1024 * 1024
defaultImg = "null.jpeg"

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowedExtensions

### PLAYER FUNCTIONS
def register(user,pword,pword2,name,file):
    if user == "":
        return (False,"Please enter a username.")
    if next(db.users.find({"user":user}),None) != None:
        return (False,"The username entered is already registered.")
    if pword == "" or pword2 == "":
        return (False,"No password entered in one or more of the fields.")
    if pword != pword2:
        return (False,"The passwords entered do not match.")
    if name == "":
        return (False,"No name entered.")
    num = next(db.users.find({},{"password":False},sort=[("num",-1)]),None)
    if num == None: #Sets an ID for newly created accounts
        i = 1
    else:
        i = num["num"] + 1
    if not file:
        return (False,"No profile image selected.")
    if not allowed_file(file.filename):
        return (False,"File is of wrong type. (Jpg and Png are supported)")
    fileExtension = file.filename.split(".")[-1]
    fileSave = user + "." + fileExtension
    file.save(os.path.join(upload_folder, fileSave))
    list = [{"user":user,"password":pword,"name":name,"num":i,"pic":fileSave,"game":0,"stats":{"kills":0,"deaths":0,"gamesPlayed":0}}]        
    db.users.insert(list)
    return (True,"Successfully registered.")
	
def authenticate(user,pword):
    if user == "":
        return (False,"Please enter your username.")
    if pword == "":
        return (False,"Please enter your password.")
    if next(db.users.find({"user":user}),None) == None:
        return (False,"No such username is registered.")
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
    db.users.update({"num":playerID},{"$set":{"stats":playerStats}})
    db.users.update({"num":targetID},{"$set":{"stats":targetStats}})
    newTargetID = getTarget(targetID)["num"]
    game = getInfoByID(playerID)["game"]
    gamePlayers = getGame(game)["players"]
    gamePlayers[str(playerID)] = newTargetID
    gamePlayers[str(targetID)] = -1
    db.games.update({"num":game},{"$set":{"players":gamePlayers}})

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
    return db.games.find_one({"num":n})

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
    
if __name__ == "__main__":
    print "Clearing the users database"
    db.users.drop()
    db.games.drop()
    #register("A",".",".","a")
    #register("B",".",".","a")
    #register("C",".",".","a")
    #register("D",".",".","a")
    #createGame("Test","desc")
    #joinGame(1,1)
    #joinGame(1,2)
    #joinGame(1,3)
    #joinGame(1,4)
