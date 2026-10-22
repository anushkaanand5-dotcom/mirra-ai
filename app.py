from datetime import date, datetime

from flask import Flask, render_template, request, session, redirect
import mysql.connector

from flask_session import Session


from dotenv import load_dotenv
import os
load_dotenv()

from flask import redirect

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
app.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=app.google_client_id,
    client_secret=app.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)


db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ilptkhaha87!23!",
    database="journal_db"
)

cursor=db.cursor()

@app.route("/")
def homepage():

    if "email" in session:
        return redirect("/journal")

    return render_template("home.html")



@app.route("/journal", methods=["GET", "POST"])
def journal():

    if "email" not in session:
        return redirect("/")
    loaded_reflection = ""
    loaded_rating = ""

    is_editable = True  

    if request.method == "POST":

        user_id = session["email"]

        entry_date = request.form["date"]
        rating = request.form.get("rating")
        reflection = request.form.get("reflection")

        action = request.form["action"]
        today = str(date.today())

        if entry_date != today:
            is_editable = False

        if not entry_date:
         return "Please select a date."

        
        print ("Email", user_id)
        print("Date:", entry_date)
        print("Action:", action)
        if action=="save":

            cursor.execute(
                """
                INSERT INTO journal_entries(
                user_id, entry_date,rating,reflection,last_modified)
             VALUES (%s, %s,%s,%s, NOW())

                ON DUPLICATE KEY UPDATE
                rating = VALUES(rating),
                reflection = VALUES(reflection),
             last_modified = NOW()
                """,
                (user_id,entry_date,rating,reflection)
            )
            db.commit()
            print ("Saved successfully!")
        elif action=="load":
            cursor.execute(
                """
                SELECT rating, reflection
                FROM journal_entries
                WHERE user_id = %s
                AND entry_date = %s
                """,
                (user_id, entry_date)
            )

            result = cursor.fetchone()

            if result:
                loaded_rating = result[0]
                loaded_reflection = result[1]
                print("load_reflection", loaded_reflection)
        

    return render_template(
        "index.html",
        loaded_reflection=loaded_reflection,
        loaded_rating=loaded_rating,
        is_editable=is_editable,
        name=session["name"]
    )
    # Basically opens html and gives it these variables



@app.route("/history")
def history():
    if "email" not in session:
        return redirect("/")
    
    cursor.execute(
        """
        SELECT user_id, entry_date, rating
        FROM journal_entries
        ORDER BY entry_date DESC
        """
    )

    entries = cursor.fetchall()
    current_month = datetime.now().month
    current_year = datetime.now().year

    months = [
        "January",
     "February",
     "March",
        "April",
     "May",
      "June",
       "July",
       "August",
      "September",
      "October",
       "November",
      "December"
    ]
    return render_template(
        "history.html",
     entries=entries,
        current_month=current_month,
      current_year=current_year,
      months=months
    )

@app.route("/entry/<user_id>/<entry_date>")
def view_entry(user_id, entry_date):
    if "email" not in session:
        return redirect("/")
    cursor.execute(
        """
        SELECT user_id,
               entry_date,
               rating,
               reflection,
               last_modified
        FROM journal_entries
        WHERE user_id = %s
        AND entry_date = %s
        """,
        (user_id, entry_date)
    )

    entry = cursor.fetchone()

    return render_template(
        "entry.html",
        entry=entry
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            """
            INSERT INTO users(username, password)
            VALUES (%s, %s)
            """,
            (username, password)
        )

        db.commit()

        return "Account created!"

    return render_template("register.html")


@app.route("/google-login")
def google_login():
    return google.authorize_redirect(
        "http://127.0.0.1:5000/login/callback",
        prompt="select_account"
    )



@app.route("/login/callback")
def callback():

    token = google.authorize_access_token()

    user = token["userinfo"]

    session["email"] = user["email"]
    session["name"] = user["name"]

    return redirect("/journal")
         


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")










if __name__ == "__main__":
    app.run(debug=True)


#@app.route("/save_my_day")
#def home():
#   return "Hello World!"
    #return render_template("index.html")

"""if __name__ == "__main__":
    app.run(debug=True)"""


"""
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        journal = request.form["journal"]

        print("User wrote:")
        print(journal)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
"""

