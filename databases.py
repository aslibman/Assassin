from pymongo import Connection
import random

conn = Connection()
db = conn['game']

def register(user,pword,pword2,name,img):
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
    list = [{"user":user,"password":pword,"name":name,"num":i,"pic":img,"game":0,"stats":{"kills":0,"deaths":0}}]
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

def assignTargets(gameID):
    game = getGame(gameID)["players"]
    n = game.keys()
    random.shuffle(n)
    for a in range(len(n) - 1):
        game[n[a]] = int(n[a+1])
    game[n[len(n)-1]] = int(n[0])
    db.games.update({"num":gameID},{"$set":{"players":game,"started":True}})
    
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

def createGame(name,description,private=False):
    nums = [i["num"] for i in db.games.find({})]
    nums.append(0)
    n = max(nums)
    game = [{"num":n+1,"name":name,"description":description,"private":private,"players":{},"started":False}]
    db.games.insert(game)
    return n + 1

def getGame(n):
    return db.games.find_one({"num":n})

def joinGame(gameID,playerID):
    gamePlayers = getGame(gameID)["players"]
    gamePlayers[str(playerID)] = 0
    db.games.update({"num":gameID},{"$set":{"players":gamePlayers}})
    db.users.update({"num":playerID},{"$set":{"game":gameID}})
    
if __name__ == "__main__":
    print "Clearing the users database"
    db.users.drop()
    db.games.drop()
