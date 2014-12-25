from flask import Flask, render_template, request, redirect, url_for
from databases import register, login, getInfoByUser, getInfoByID

app = Flask('__name__')

@app.route("/",methods = ["POST","GET"])
@app.route ("/home", methods = ["POST" , "GET"])
def home():
    return render_template("home.html")

@app.route ("/login", methods = ["POST" , "GET"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pword = request.form["password"]
        l = login(user,pword)
        if l[0]:
            return redirect(url_for("home"))
        else:
            return render_template("login.html", message=l[1])
    return render_template("login.html")
	
@app.route ("/register", methods = ["POST" , "GET"])
def register():
	return render_template("register.html")

@app.route("/about", methods = ["POST" , "GET"])
def about():
	return render_template("about.html")

##@app.route ("/facerecog", methods = ["POST" , "GET"])

if __name__=="__main__":
    app.debug = True
    app.secret_key = 'dfjahdjhbdjf,lnhmdfnm'
    app.run()
