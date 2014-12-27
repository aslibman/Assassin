from flask import Flask, render_template

app=Flask('__name__')

@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template("register.html")

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template("about.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template("profile.html")

@app.route('/target', methods=['GET', 'POST'])
def target():
    return render_template("target.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template("search.html")

if __name__=="__main__":
    app.debug=True
    app.run()
