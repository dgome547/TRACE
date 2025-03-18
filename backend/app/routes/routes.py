from flask import Blueprint

routes = Blueprint('routes', __name__)

@routes.route('/test', methods=['GET'])
def test_route():
    return "Test route works!"