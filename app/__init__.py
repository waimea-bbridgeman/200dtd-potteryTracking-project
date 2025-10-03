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
def handle_new_piece():
    with connect_db() as client:
     sql = "SELECT id, name, colour FROM glazes ORDER BY name ASC"
     params = []
     result = client.execute(sql, params)
     glazes = result.rows
     
    return render_template("pages/addPiece.jinja", glazes=glazes)

#-----------------------------------------------------------
# Route for adding a piece, using data posted from a form
#-----------------------------------------------------------
@app.post("/addPiece")
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
# Add glaze page route
#-----------------------------------------------------------
@app.get("/addGlaze")
def show_add_glaze_form():
    with connect_db() as client:
        # And show them on the page
        return render_template("pages/addGlaze.jinja")

#-----------------------------------------------------------
# Add glaze page route
#-----------------------------------------------------------
@app.post("/addGlaze")
def handle_new_glaze():
    with connect_db() as client:
        # get the new data from the form
        glaze_name = request.form.get("name")
        glaze_colour = request.form.get("colour")

        # Insert into the DB
        sql = "INSERT INTO glazes (name, colour) VALUES (?, ?)"
        params = [glaze_name, glaze_colour]
        client.execute(sql, params)
        
        # Success!
        flash(f"Glaze, {glaze_name}, added")

        # And back to home page
        return redirect("/")
#-----------------------------------------------------------
# Update the piece information 
#-----------------------------------------------------------
@app.post("/updatePiece")
def handle_updates_to_Piece():
    with connect_db() as client:
        #Get the new info from the form
        uses_layers = request.form.get("layers")
        p_id = request.form.get("p_id")
        g_id = request.form.get("g_id")
        
        

        #Insert it into the DB
        sql = "INSERT INTO uses (p_id, layers, g_id) VALUES (?, ?, ?)"
        params = [p_id, uses_layers, g_id]
        client.execute(sql, params)

        #Success!
        flash(f"Piece updated!")

        return redirect("/")


#-----------------------------------------------------------
# Piece page route - Show details of a single piece
#-----------------------------------------------------------
@app.get("/piece/<int:id>/")    
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

            # Get the glaze dips so far
            sql = """
                SELECT 
                    glazes.name, 
                    uses.date, 
                    uses.layers 
                    
                FROM uses 
                JOIN glazes ON uses.g_id = glazes.id

                WHERE uses.p_id=?
            """
            params = [id]
            result = client.execute(sql, params)
            dips = result.rows

            # Get a list of glazes for menu
            sql = "SELECT id, name, colour FROM glazes"
            params = []
            result = client.execute(sql, params)
            glazes = result.rows

            return render_template(
                "pages/piece.jinja", 
                piece=piece,
                dips=dips,
                glazes=glazes
            )

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


