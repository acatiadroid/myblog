from flask import Flask, render_template, redirect, request
import psycopg2 as postgres
import json

with open("secrets.json", "r") as f:
    js = json.load(f)

conn = postgres.connect(
    database=js["database"],
    user=js["user"],
    port=js["port"],
    host=js["host"],
    password=js["password"],
)
app = Flask(__name__, static_folder="./static/")

def get_post(name):
    cur = conn.cursor()

    cur.execute("SELECT * FROM posts WHERE postname=%s", (name,))
    
    data = cur.fetchone()
    conn.commit()
    cur.close()
    
    return data

def get_posts():
    cur = conn.cursor()

    cur.execute("""SELECT * FROM posts""")

    data = cur.fetchall()
    conn.commit()
    cur.close()

    return data

def addpost(title, mainbody, displaytitle):
    cur = conn.cursor()
    
    cur.execute("""INSERT INTO posts (postname, postcontent, postdisplaytitle) VALUES (%s, %s, %s)""", (title, mainbody, displaytitle,))

    conn.commit()
    cur.close()

@app.route("/")
def index():
    return redirect("/home")

@app.route("/acatia/adminPanel", methods=['POST', 'GET'])
def createpost():
    if request.method == "POST":
        if request.form.get("title") and request.form.get("mainbody") and request.form.get("disp-title"):
            addpost(request.form.get("title"), request.form.get("mainbody"), request.form.get("disp-title"))

            return redirect(f"/post?name={request.form.get('title')}")

        entry = request.form.get("pass")

        if entry == js["adminPanelKey"]:
            return render_template("addpost.html")
        else:
            return render_template("verify.html", verify=True, wrong=True)
    
    return render_template("verify.html", verify=True)

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/post")
def post():
    args = request.args
    if not args.get("name"):
        return redirect("/feed")
    
    _, body, title = get_post(args["name"])
   
    return render_template("post.html", title=title, body=body)
    
@app.route("/feed")
def feed():
    posts = get_posts()
    final = []
    for url, body, title in posts:
        final.append({"url": url, "body": body, "title": title})
    
    return render_template("feed.html", posts=final)


if __name__ == "__main__":
    app.run(debug=True)