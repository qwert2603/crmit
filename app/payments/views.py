from flask import render_template
from flask_login import login_required
from app.decorators import check_master
from app.models import Group
from app.payments import payments


@payments.route('/group/<int:group_id>')
@login_required
@check_master
def payments_in_group(group_id):
    # todo
    return render_template('payments/payments_in_group.html', group=Group.query.get_or_404(group_id))
