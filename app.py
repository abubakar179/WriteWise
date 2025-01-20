from crypt import methods

from flask import Flask, redirect, url_for, render_template, request, session

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        passwd = request.form["pass"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        return render_template("login.html")

@app.route("/<usr>")
def user(usr):
    return f"<p>{usr}</p>"

if __name__ == "__main__":
    app.run(debug=True)