from flask import request, jsonify, g
from ..utils.auth import generate_token, requires_auth, verify_token
from ..api import api as api_bp
from ..models import Canvas
import nanoid
from random import choice
import time

alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
awesome_text = ["A good Project", "Fantastic Project",
                "An awesome project", "Best Project all over the world"]


# @api_bp.route("/smite_it_down", methods=["DELETE"])
# def purify():
#     Canvas.delete_many({})
#     return(jsonify(response=list(Canvas.find({}))))

@api_bp.route("/new_canvas", methods=["POST"])
@requires_auth
def get_new_cavas():
    incoming = request.get_json()
    canvas_id = nanoid.generate(size=20)
    canvas_type = incoming["canvas_type"]
    canvas = Canvas({
        'canvas_id': canvas_id,
        'canvas_name': "New Canvas",
        'canvas_description': choice(awesome_text),
        'canvas_type': canvas_type,
        'canvas_team': [{"user": g.current_user["email"], "role":"creator"}],
        'canvas_preview': None,
        'canvas_notes': None,
        'canvas_lastUpdate': int(1000*time.time())
    })
    try:
        canvas.save()
    except:
        return "Couldn't save that!", 501
    last_canvas = Canvas.find_one({"canvas_id": canvas_id}, {"_id": 0})
    return jsonify(canvas=last_canvas)


@api_bp.route("/get_canvas_by_canvas_id", methods=["POST"])
@requires_auth
def get_canvas_by_canvas_id():
    try:
        canvas_id = request.get_json()["canvas_id"]
    except:
        return jsonify(canvas={})
    canvas = Canvas.find_one({"canvas_id": canvas_id}, {"_id": 0})
    return jsonify(canvas=canvas)


@api_bp.route("/get_canvas_by_user", methods=["POST"])
@requires_auth
def get_canvas_by_user():
    if request.get_json():
        email = request.get_json()["email"]
    else:
        email = g.current_user["email"]
    canvas_list = list(Canvas.find({"canvas_team.user": email}, {"_id": 0}))

    return jsonify(user_canvas=canvas_list)


@api_bp.route("/update_many_canvas", methods=["GET"])
def many_canvas_update():
    incoming = request.get_json()
    Canvas.update({},
                  {'$set': incoming["canvas"]},
                  multi=True)
    canvas_list = Canvas.find({"canvas_id": incoming["canvas_id"]}, {"_id": 0})
    return jsonify(list(canvas_list))


@api_bp.route("/update_canvas", methods=["POST"])
@requires_auth
def update_canvas():
    try:
        updated_canvas = request.get_json()['canvas']
        Canvas.find_one_and_update({'canvas_id': updated_canvas['canvas_id']}, {
                                   '$set': updated_canvas})
    except:
        return jsonify(error=False)
    return jsonify(user_canvas=Canvas.find_one({'canvas_id': updated_canvas['canvas_id']}, {"_id": 0}))