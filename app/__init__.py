#===========================================================
# Pottery Tracking project
# Billy Bridgeman 
#-----------------------------------------------------------
# Tracks the amount of glazes done on a certain piece
#it does this by allowing the end user to add pottery pieces
#to the DB and giving them the ability to update the amount of 
#layers each piece has had. 

#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now

# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM pieces ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        pieces = result.rows

        sql = "SELECT id, name, colour FROM glazes ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        glazes = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", pieces=pieces, glazes=glazes)



#-----------------------------------------------------------
# Add piece page route
#-----------------------------------------------------------
@app.get("/addPiece")
def addPiece():
    with connect_db() as client:
     sql = "SELECT id, name, colour FROM glazes ORDER BY name ASC"
     params = []
     result = client.execute(sql, params)
     glazes = result.rows
     
    return render_template("pages/addPiece.jinja", glazes=glazes)


#-----------------------------------------------------------
# Add glaze page route
#-----------------------------------------------------------
@app.get("/addGlaze")
def addGlaze():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name, colour FROM glazes ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        glazes = result.rows

        # And show them on the page
        return render_template("pages/addGlaze.jinja", glazes=glazes)


#-----------------------------------------------------------
# Piece page route - Show details of a single piece
#-----------------------------------------------------------
@app.get("/piece/<int:id>")
def show_one_piece(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT id, name, description FROM pieces WHERE id=?"
        params = [id]
        result = client.execute(sql, params)


        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            piece = result.rows[0]
            return render_template("pages/piece.jinja", piece=piece)

        else:
            # No, so show error
            return not_found_error()
        


#-----------------------------------------------------------
# Glaze page route - Show details of a single glaze
#-----------------------------------------------------------
@app.get("/glaze/<int:id>")
def show_one_glaze(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT id, name, colour FROM glazes WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            glaze = result.rows[0]
            return render_template("pages/glaze.jinja", glaze=glaze)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a glaze, using data posted from a form
#-----------------------------------------------------------
@app.post("/add/glaze")
def add_a_glaze():
    # Get the data from the form
    name  = request.form.get("name")
    colour = request.form.get("colour")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO glazes (name, colour) VALUES (?, ?)"
        params = [name, colour]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"'{name}' added", "success")
        return redirect("/")

#-----------------------------------------------------------
# Route for adding a piece, using data posted from a form
#-----------------------------------------------------------
@app.post("/add/piece")
def add_a_piece():
    # Get the data from the form
    name  = request.form.get("name")
    description = request.form.get("description")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO pieces (name, description) VALUES (?, ?)"
        params = [name, description]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"'{name}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for deleting a Glaze, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/glaze<int:id>")
def delete_a_glaze(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM glazes WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("The glaze has been deleted", "success")
        return redirect("/")

#-----------------------------------------------------------
# Route for deleting a Piece, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/piece<int:id>")
def delete_a_piece(id):
    name  = request.form.get("name")
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM pieces WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("The piece has been deleted", "success")
        return redirect("/")


