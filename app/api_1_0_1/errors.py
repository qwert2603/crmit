from app.api_1_0_1 import api_1_0_1


@api_1_0_1.errorhandler(400)
def error400(e):
    return 'bad request', 400


@api_1_0_1.errorhandler(401)
def error401(e):
    return 'auth required', 401


@api_1_0_1.errorhandler(403)
def error403(e):
    return 'access denied', 403


@api_1_0_1.errorhandler(404)
def error404(e):
    return 'not found', 404


@api_1_0_1.errorhandler(500)
def error500(e):
    return 'internal server error', 500
