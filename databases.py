from pymongo import Connection
import random

conn = Connection()
db = conn['login']

def register(user,pword,pword2,name):
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
    list = [{"user":user,"password":pword,"name":name,"num":i}]
    print list
    db.users.insert(list)
    return (True,"Successfully registered.")
	
	#def troll(user,pword,pword2,name):
		#return (user, pword,pword2,name)
	
def login(user,pword):
    if user == "":
        return (False,"Please enter your username.")
    if pword == "":
        return (False,"Please enter your password.")
    if next(db.users.find({"user":user}),None) == None:
        return (False,"No such username is registered.")
    if next(db.users.find({"user":user,"password":pword}),None) == None:
        return (False,"Incorrect password.")
    return (True,"Successfully logged in.")

def assignTargets():
    n = [i["num"] for i in db.users.find({},{"password":False})]
    random.shuffle(n)
    for a in range(len(n)):
        if a == len(n) - 1:
            db.users.update({"num":n[a]},{"$set":{"target":n[0]}})
        else:
            db.users.update({"num":n[a]},{"$set":{"target":n[a+1]}})
    
def getInfoByUser(user):
    return next(db.users.find({"user":user},{'password':False}),None)

def getInfoByID(n):
    return next(db.users.find({"num":n},{'password':False}),None)

def getTarget(n):
    t = getInfoByID(n)
    if t != None and t["target"] != 0:
        return getInfoByID(t["target"])
    
if __name__ == "__main__":
    print "Clearing the users database"
    db.users.drop()


