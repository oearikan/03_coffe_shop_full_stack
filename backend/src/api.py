import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from mylog import mylog

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
@app.route('/drinks')
def get_drinks():
    try:
        drink_list = Drink.query.all()
        formatted_list = [drink.short() for drink in drink_list]
        if len(formatted_list) == 0:
            abort(404)

        return jsonify({
            "success": "True",
            "drinks": formatted_list
        })
    except Exception:
        abort(500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drink_list = Drink.query.all()
        formatted_list = [drink.long() for drink in drink_list]
        if len(formatted_list) == 0:
            abort(404)

        return jsonify({
            "success": "True",
            "drinks": formatted_list
        })
    except Exception:
        abort(500)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(payload):
    try:
        body = request.get_json()
        new_title = body.get("title", None)
        new_recipe = body.get("recipe", None)
        check = [bool(new_title), bool(new_recipe)]
        if not all(check):
            abort(422)

        drink = Drink(title = new_title, recipe = json.dumps(new_recipe))
        drink.insert()

        return jsonify({
            "success": True,
            "drink": drink.long()
        })
    except Exception:
        abort(500)



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
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).first_or_404()
        body = request.get_json()
        updated_title = body.get('title', None)
        updated_recipe = body.get('recipe', None)

        if updated_title:
            drink.title = updated_title
            drink.update()

        if updated_recipe:
            drink.recipe = json.dumps(updated_recipe)
            drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(422)



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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).first_or_404()
        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except Exception:
        abort(500)


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

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Something went wrong."
    }), 500


@app.errorhandler(405)
def method_not_allowerd(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed for the requested URL"
    })

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        "success": False,
        "error": str(e.status_code) + ": " + e.error['code'],
        "message": e.error['description']
    }), e.status_code
