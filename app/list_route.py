from flask import render_template, request


def create_list_route(query, template):
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    pagination = query(search).paginate(page, per_page=20, error_out=False)
    return render_template(template, pagination=pagination, items=pagination.items, search=search)
