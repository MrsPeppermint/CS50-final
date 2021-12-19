import os
from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from functions import login_required, weather_info, celsius, fahr


# configure application
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# filters for temperature (convert and format)
app.jinja_env.filters["celsius"] = celsius
app.jinja_env.filters["fahrenheit"] = fahr

# responses not catched
@app.after_request
def after_request_func(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    return response

# filesystem instead of cookies
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# check for API KEY
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

#connect to database
db = sqlite3.connect("wardrobe.db", check_same_thread=False)

# rows returned as dicts
db.row_factory=sqlite3.Row
cur = db.cursor()

# homepage
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# guest visiting site
@app.route("/guest")
def guest():
    return render_template("index.html")

# register function
@app.route("/register", methods=["GET", "POST"])
def register():
   
    if request.method == "GET":
        return render_template("register.html")
    
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # check for available username and matching password   
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall() 
        if not username:
            flash("Please enter username")
            return redirect("/register")
        elif len(rows) != 0:
            flash("Username taken")
            return redirect("/register")
        elif not password or not confirm_password:
            flash("Please enter password")
            return redirect("/register")
        elif password != confirm_password:
            flash("Passwords do not match")
            return redirect("/register")
        
        # insert into users table using hashed password
        else:
            hash = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, hash) VALUES (?,?)", (username,hash))
            db.commit()
            id = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()[0]    
            session["user_id"] = id
            flash("Registered successfully!")
            return redirect("/") 

# log in function 
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    
    if request.method == "GET":
        return render_template("login.html")
    
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        
        # check if user provided username and password
        if not username or not password:
            flash("Please enter usename and password")
            return render_template("login.html")
        
        # check if username is in database
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        if len(rows) != 1:
            flash("Account doesn't exist. Want to register?")
            return redirect("/register")
        
        # check for password 
        else:
            password_check = [hash[2] for hash in rows]
            if not check_password_hash(password_check[0], password):
                flash("Wrong password!")
                return render_template("login.html")
            # log in successful, update session
            else:
                user = [user[0] for user in rows]
                session["user_id"] = user[0]
                flash("Login successful!")
                return redirect("/")

# logout function
@app.route("/logout")
def logout():
    session.clear()
    flash("Logout successful!")
    return redirect("/")


@app.route("/get_weather", methods=["POST"])
def get_weather():
    location = request.form.get("location").capitalize()
    if not location:
        flash("Enter location!")
        return redirect("/")

    info = weather_info(location)
    if not info == None:
        return render_template("selection.html", info=info)
    else:
        flash("Enter valid location!")
        return redirect("/")

# get weather info and clothing selection
@app.route("/get_selection", methods=["POST"])
@login_required
def get_selection():

        location = request.form.get("location").capitalize()
        if not location:
            flash("Enter location!")
            return redirect("/")
        
        # get weather info from api
        info = weather_info(location)
        if not info == None:
            selection = []
            
            # get all clothes from user
            rows = db.execute("SELECT * FROM clothes WHERE user_id = ?",(session["user_id"],)).fetchall()
            
            # create list of dictionaries with cothes that fit current weather report
            for row in rows:
                if (row["weather"] == info["id"] or row["weather"] == 3) and \
                    (row["temperature"] == info["temp_cat"] or row["temperature"] == 3):
                    selection.append({
                        "type": row["type"],
                        "description": row["description"],
                        "link": row["link"],
                        "color": row["color"]
                    })
            if len(selection) == 0:
                flash("No suitable outfit options. Try adding more items")
            return render_template("selection.html", info=info, selection=selection)    
        else:
            flash("Enter valid location!")
            return redirect("/")


# add new clothing item to database
@app.route("/add_item", methods=["GET","POST"])
@login_required
def add_item():
   
    if request.method == "GET":
        return render_template("add_item.html")
    
    else:
        type = request.form.get("clothing_type")
        description = request.form.get("description")
        temperature = request.form.get("temperature")
        weather = request.form.get("weather")
        source_img = request.files["image"]
        color = request.form.get("color")
        
        # clothing type input necessary
        if not type:
            flash("Please select clothing type")
            return render_template("add_item.html")
        
        # color input necessary    
        if not color:
            flash("Please select color")
            return render_template("add_item.html")

        # set deafult image
        if not source_img: 
                image = "static/images/default_image.png"

        else:
            # upload image to filesystem with secure filename (user_id + image filename)
            img_name = secure_filename(str(session["user_id"]) + source_img.filename)
            image = os.path.join("static/images", img_name)
            
            # check for image duplicate
            if not os.path.isfile(image):
                
                # resize image and set correct orientation (PIL)
                img = Image.open(source_img)
                img.thumbnail((200,200))
                img =  ImageOps.exif_transpose(img)
                img.save(image)
            else: 
                flash("Image with such name already exists, try changing the name of the file.")
                return render_template("add_item.html")

        # insert into table "clothes"    
        cur.execute("INSERT INTO clothes (type, description, temperature, weather, link, user_id, color) VALUES (?,?,?,?,?,?,?)", \
                    (type, description, temperature, weather, image, session["user_id"], color))
        db.commit()
        flash("Item successfully added to your closet")
        return render_template("success.html")     

# show user's closet
@app.route("/closet")
@login_required
def closet():
    rows = db.execute("SELECT * FROM clothes WHERE user_id = ?",(session["user_id"],)).fetchall()
    if len(rows) < 1:
        flash("No items found in your closet. Try adding them.")
        return redirect("/add_item")
    else:
        return render_template("closet.html", selection=rows)

# change password
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def password():

    if request.method == "GET":
        return render_template("password.html")
    
    else:
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        repeat_new_password = request.form.get("repeat_new_password")
        user = session["user_id"]

        # check if the entered old password is valid
        old_check = db.execute("SELECT hash FROM users WHERE id = ?", (user,)).fetchone()[0]
        if not check_password_hash(old_check, old_password):
            flash("Wrong password!")
            return render_template("password.html")

        else:
            # if new passwords don't match
            if not new_password == repeat_new_password:
                flash("Passwords don't match")
                return render_template("password.html")

            # update table with new hash
            else:
                db.execute("UPDATE users SET hash = ? WHERE id = ?", (generate_password_hash(new_password), user))
                flash("Password successfully changed!")
                return redirect("/")
    
# delete account and empty user's closet 
@app.route("/delete_account", methods = ["GET", "POST"])
@login_required
def delete_account():
    
    if request.method == "GET":
        return render_template("deletion.html")
    
    else:
        password = request.form.get("password")
        user = session["user_id"]
        check = db.execute("SELECT hash FROM users WHERE id = ?", (user,)).fetchone()[0]
        if not check_password_hash(check, password):
            flash("Wrong password")
            return redirect("/delete_account")
        else:
            cur.execute("DELETE FROM users WHERE id = ?", (user,))
            cur.execute("DELETE FROM clothes WHERE user_id = ?", (user,))
            db.commit()
            session.clear()
            flash("Account successfully deleted")
            return redirect("/")


#remove item from user's closet
@app.route("/remove_item", methods=["POST"])
@login_required
def remove_item():
    item = request.form.get("id")
    link = request.form.get("link")
    
    #remove image from filesys
    if not link == "static/images/default_image.png":
        fh = open(link, "r")
        os.remove(link)
        fh.close()

    #remove entry from closet
    cur.execute("DELETE FROM clothes WHERE id = ?", (item, ))
    db.commit()
    
    return redirect("/closet")