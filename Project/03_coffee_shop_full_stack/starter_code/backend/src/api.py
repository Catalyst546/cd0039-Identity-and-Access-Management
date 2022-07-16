import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc, and_
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def getDrinks():
    try:
        data = []
        { data.append(d.short()) for d in Drink.query.all()}

        if len(data) == 0:
            return jsonify({"drinks": "No drink is available", "success": True}), 200
        else: 
            return jsonify({"drinks": data, "success": True}), 200     

    except:
        abort(400)
    finally:
        print("Drinks : ", data)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
def getDrinksDetailed():
    try:
        data = []
        { data.append(d.long()) for d in Drink.query.all()}

        if len(data) == 0:
            return jsonify({"drinks": "No drink is available", "success": True}), 200
        else: 
            return jsonify({"drinks": data, "success": True}), 200     

    except:
        abort(400)
    finally:
        print("Drinks : ", data)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

def getDrinkByBody(drink):
    new_drink = Drink.query.filter_by(and_(Drink.title == drink.title, json.loads(Drink.recipe) == drink.recipe)).one_or_none()
    print("New Drinks : ", new_drink.long())
    if(new_drink is not None): 
        return new_drink.long()
    else:
        return None

@app.route('/drinks', methods=['POST'])
def postDrinks():
    try:
        data = request.get_json()
        if data.get('title'):
            drink = Drink(
                title = data.get('title'), 
                recipe = json.dumps(data.get('recipe'))
            )
            drink.insert()
            print("Data : ", data , "\nRecipe : ", data.get('recipe'))
            # response = drink
            # if response is None:
            #     return jsonify({"message": "Could not fetch drink after saving",
            #     "success" : True}), 200
            # else:
            # print("New Drink : ", getDrinkByBody(drink))

            return jsonify({"drinks": [drink.long()],
            "success" : True}), 200
        else:
            abort(422)
    except:
        return jsonify({"message": "Error occurred while posting drink",
            "success" : False}), 400


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
def patchDrinks(id):
    try:
        data = request.get_json()
        print("\nData : ", data)
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            return jsonify({"message": "Drink not found", "success": False}), 404

        print("Drink : ", drink, "\nData : ")
        if (data.get('title')):
            if(data.get('title') is not None):
                print("inside title")
                drink.title = data.get('title')
            
        if (data.get('recipe') is not None):
            print("inside drink recipe: ", drink.recipe)

            if (data.get('recipe')[0].get('color') is not None):
                json.loads(drink.recipe)[0]['color']= data.get('recipe')[0].get('color')
                print("inside drink recipe color : ", drink.recipe)

            if (data.get('recipe')[0].get('name') is not None):
                print("inside recipe name")
                json.loads(drink.recipe)[0]['name'] = data.get('recipe')[0].get('name')
                print("inside drink recipe color : ", drink.recipe)

            if (data.get('recipe')[0].get('parts') is not None):
                print("inside recipe parts")
                drink.recipe[0].parts = data.get('recipe')[0].get('parts')
                print("inside drink recipe color : ", drink.recipe)
        
        drink.update()
        print("done with update")
        return jsonify({"drinks": [drink.long()],
            "success" : True}), 200
        
    except:
        return jsonify({"message": "Error occurred while posting drink",
            "success" : False}), 400

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
def deleteDrinks(id):
    try:
        drink = Drink.query.get_or_404(id)
        if drink:
            drink.delete()
            return jsonify({"success": True, "delete": id}), 200
    except:
        return jsonify({"success": False, "message": "Error occurred performing request"}), 400

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def resourceNotFound(error):
    return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authError(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized request"
    }), 422