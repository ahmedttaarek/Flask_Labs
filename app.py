from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
def home_page():
    print("hello")
    return "Hello World"

@app.route("/student")
def student():
    return redirect(url_for("home_page"))

@app.route("/student/<int:id>")
def studentId(id):
    if id == 0:
        return redirect(url_for("home_page"))
    else:
        return "HELLOWORLD"
    
students = [{"id" :1 , "name": "Ahmed"} ,{"id" :2, "name": "Tarek"}]

@app.route("/search/<int:id>")
def search(id):
    return render_template("search.html" , students= students , studentId = id)

if __name__ == "__main__":
    app.run(debug=True)