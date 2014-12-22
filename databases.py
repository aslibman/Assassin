from pymongo import Connection

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
    db.users.insert(list)
    return (True,"Successfully registered.")

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

def getInfoByUser(user):
    return next(db.users.find({"user":user},{'password':False}),None);

def getInfoByID(n):
    return next(db.users.find({"num":n},{'password':False}),None);

if __name__ == "__main__":
    print "Clearing the users database"
    db.users.drop()

