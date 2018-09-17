from flask import request, jsonify


def create_json_list(Entity, filter_field, entity_to_json, more_filter=None, order_by=None):
    query_ = Entity.query \
        .filter(filter_field.ilike('%{}%'.format(request.args.get('search', '', type=str))))
    if more_filter is not None: query_ = more_filter(query_)
    if order_by is not None:
        query_ = order_by(query_)
    else:
        query_ = query_.order_by(Entity.id)
    entities_list = query_ \
        .offset(request.args.get('offset', type=int)) \
        .limit(request.args.get('count', type=int)) \
        .all()
    return jsonify([entity_to_json(entity) for entity in entities_list])
