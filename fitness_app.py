#--------------------------------------------------Task 1---------------------------------------------------------------------------#

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
# local import for db connection
from connect_db import connect_db, Error

app = Flask(__name__)
app.json.sort_keys = False #maintain order of your stuff
ma = Marshmallow(app)
#------------------------------------------------------End-------------------------------------------------------------------------#

#-----------------------------------------------------Member SCHEMA------------------------------------------------------------------------#

# define the member schema
# makes sure the member data adheres to a specific format
class memberSchema(ma.Schema):
    member_id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    bench_amount = fields.Int(required=True)
    membership_type = fields.String(required=True)

    class Meta:  
        
        fields = ("member_id", "name", "email", "phone", "bench_amount", "membership_type")
# instantiating memberSchema class
# based on how many members we're dealing with
member_schema = memberSchema()
members_schema = memberSchema(many=True)

#------------------------------------------------------End-----------------------------------------------------------------------#

#------------------------------------------------------Task 2-----------------------------------------------------------------------#

@app.route('/')
def home():
    return "Welcome to our super cool Fitness Tracker, time to get up, get out, and touch grass!!"


@app.route('/members', methods=['GET'])
def get_members():   
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True) #dictionary=TRUE only for GET
        # SQL query to fetch all members
        query = "SELECT * FROM Members"

        # executing query with cursor
        cursor.execute(query)

        # accessing stored query
        members = cursor.fetchall()

         # use Marshmallow to format the json response
        return members_schema.jsonify(members)
    
    except Error as e:
        # error handling for connection/route issues
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/members', methods = ['POST']) 
def add_members():
    try:
        # Validate the data follows our structure from the schema
        # deserialize the data using Marshmallow
        # this gives us a python dictionary
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        # new member details, to be sent to our db
        # comes from member_data which we turn into a python dictionary
        # with .load(request.json)
        new_member = (member_data['name'], member_data['email'], member_data['phone'], member_data['bench_amount'], member_data['membership_type'])

        # SQL Query to insert member data into our database
        query = "INSERT INTO Members (name, email, phone, bench_amount, membership_type) VALUES (%s, %s, %s, %s, %s)"

        # execute the query 
        cursor.execute(query, new_member)
        conn.commit()

        # Succesfiul addition of our member
        return jsonify({"message":"New member added succesfully"}), 201
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


@app.route('/members/<int:id>', methods= ["PUT"])
def update_member(id):
    try:
        # Validate the data follows our structure from the schema
        # deserialize the data using Marshmallow
        # this gives us a python dictionary
        member_data = member_schema.load(request.json)
        print(member_data)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # Updating member info
        updated_member = (member_data['name'], member_data['email'], member_data['phone'], member_data['bench_amount'], member_data['membership_type'], id)

        # SQL Query to find and update a member based on the id
        query = "UPDATE Members SET name = %s, email = %s, phone = %s, bench_amount = %s, membership_type = %s WHERE member_id = %s"

        # Executing Query
        cursor.execute(query, updated_member)
        conn.commit()

        # Message for succesful update
        return jsonify({"message":"Member details were succesfully updated!"}), 200
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    

@app.route('/members/<int:id>', methods=["DELETE"])
def delete_member(id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        # set variable for the id passed in through the right to a tuple, with that
        member_to_remove = (id,)
        
        # query to find member based on their id
        query = "SELECT * FROM Members WHERE member_id = %s"
        # check if member exists in db
        cursor.execute(query, member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "User does not exist"}), 404
        
        # If member exists, we shall delete them :( 
        del_query = "DELETE FROM Members where member_id = %s"
        cursor.execute(del_query, member_to_remove)
        conn.commit()

        # nice message about the execution of our beloved member
        return jsonify({"message":"Member Removed succesfully"}), 200   

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 

#----------------------------------------------------------------End----------------------------------------------------------------------------#

#---------------------------------------------------------Workout SCHEMA--------------------------------------------------------------------#

class WorkoutSchema(ma.Schema):
    sesh_id = fields.Int(dump_only=True)
    date = fields.String(required=True)
    member_id = fields.Int(required=True)
    workout_type = fields.String(required=True)

    class Meta:

        fields = ("sesh_id", "date", "member_id", "workout_type")
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

#----------------------------------------------------------End---------------------------------------------------------------------#

#---------------------------------------------------------Task 3--------------------------------------------------------------------#

@app.route('/workouts', methods=['GET'])
def get_workouts():   
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True) #dictionary=TRUE only for GET
        # SQL query to fetch all workouts
        query = "SELECT * FROM Dank_sesh"

        # executing query with cursor
        cursor.execute(query)

        # accessing stored query
        workouts = cursor.fetchall()

         # use Marshmallow to format the json response
        return workouts_schema.jsonify(workouts)
    
    except Error as e:
        # error handling for connection/route issues
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/workouts', methods = ['POST']) 
def add_workouts():
    try:
        # Validate the data follows our structure from the schema
        # deserialize the data using Marshmallow
        # this gives us a python dictionary
        workout_data = workout_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        # new workout details, to be sent to our db
        # comes from workout_data which we turn into a python dictionary
        # with .load(request.json)
        new_workout = (workout_data['date'], workout_data['member_id'], workout_data['workout_type'])

        # SQL Query to insert member data into our database
        query = "INSERT INTO Dank_sesh (date, member_id, workout_type) VALUES (%s, %s, %s)"

        # execute the query 
        cursor.execute(query, new_workout)
        conn.commit()

        # Succesfiul addition of our member
        return jsonify({"message":"New workout added succesfully"}), 201
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


@app.route('/workouts/<int:id>', methods= ["PUT"])
def update_workout(id):
    try:
        # Validate the data follows our structure from the schema
        # deserialize the data using Marshmallow
        # this gives us a python dictionary
        workout_data = workout_schema.load(request.json)
        print(workout_data)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # Updating workout info
        updated_workout = (workout_data['date'], workout_data['member_id'], workout_data['workout_type'], id)

        # SQL Query to find and update a workout based on the id
        query = "UPDATE Dank_sesh SET date = %s, member_id = %s, workout_type = %s WHERE sesh_id = %s"

        # Executing Query
        cursor.execute(query, updated_workout)
        conn.commit()

        # Message for succesful update
        return jsonify({"message":"Workout details were succesfully updated!"}), 200
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#----------------------------------------------------------End----------------------------------------------------------------------#

if __name__ == "__main__":
    app.run(debug=True)