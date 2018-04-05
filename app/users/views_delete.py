from flask import flash, redirect, url_for, abort
from flask_login import login_required
from app import db
from app.is_removable_check import is_master_removable
from app.models import Master
from app.users import users
from app.decorators import check_master


@users.route('/delete_master/<int:id>')
@login_required
@check_master
def delete_master(id):
    master = Master.query.get_or_404(id)
    if not is_master_removable(master): abort(409)
    db.session.delete(master)
    db.session.delete(master.system_user)
    flash('руководитель удалён')
    return redirect(url_for('.masters_list'))
