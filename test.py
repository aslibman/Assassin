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

if __name__=="__main__":
    app.debug=True
    app.run()
