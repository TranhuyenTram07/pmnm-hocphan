
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    tong = None

    if request.method == "POST":
        a = int(request.form["a"])
        b = int(request.form["b"])
        tong = a + b

    return render_template("index.html", tong=tong)

if __name__ == "__main__":
    app.run(debug=True)

