from wtforms import DateField
from wtforms.widgets import Input


class DateInput(Input):
    input_type = 'date'


class DateFieldWidget(DateField):
    widget = DateInput()
