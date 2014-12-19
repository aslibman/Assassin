from pymongo import Connection

conn = Connection()
db = conn['login']

def register(user,pword,pword2,name):
    if user == "":
        return "Please enter a username."
    if next(db.users.find({"user":user}),None) != None:
        return "The username entered is already registered."
    if pword == "" or pword2 == "":
        return "No password entered in one or more of the fields."
    if pword != pword2:
        return "The passwords entered do not match."
    if name == "":
        return "No name entered."
    db.users.find(sort=[("num",-1)],{"password":False})
    if num == None:
        i = 1
    else:
        i = 
    list = [{"user":user,"password":pword,"name":name,"num":i}]
    db.users.insert(list)
    return "Successfully registered."

def login(user,pword):
    if user == "":
        return "Please enter your username."
    if pword == "":
        return "Please enter your password."
    if next(db.users.find({"user":user}),None) == None:
        return "No such username is registered."
    if next(db.users.find({"user":user,"password":pword}),None) == None:
        return "Incorrect password."
    return "Successfully logged in."

def getInfoByUser(user):
    return next(db.users.find({"user":user},{'password':False}),None);

def getInfoByID(n):
    return next(db.users.find({"num":n},{'password':False}),None);

if __name__ == "__main__":
    print "Clearing the users database"
    db.users.drop()

