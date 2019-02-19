from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, SelectField
from wtforms.validators import Length

from app.form import prefix_field_required
from app.models import Student, StudentInGroup


class SendNotificationForm(FlaskForm):
    receiver = SelectField(prefix_field_required + 'получатель', coerce=int)
    subject = StringField(prefix_field_required + 'тема', validators=[Length(1, 255)])
    body = TextAreaField(prefix_field_required + 'сообщение', validators=[Length(1, 65535)])
    submit = SubmitField('отправить')

    def __init__(self, group, *args, **kwargs):
        super(SendNotificationForm, self).__init__(*args, *kwargs)
        sigs = group.students_in_group \
            .join(Student, Student.id == StudentInGroup.student_id) \
            .order_by(Student.fio) \
            .all()
        self.receiver.choices = [(0, '{} (учеников: {})'.format(group.name, group.students_in_group.count()))] + \
                                [(s.id, s.student.fio) for s in sigs]
