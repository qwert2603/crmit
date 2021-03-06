import re

from wtforms import DateField, ValidationError
from wtforms.widgets import Input

from app.models import vk_link_prefix

prefix_field_required = '<span style="color: orangered;">*</span> '


class DateInput(Input):
    input_type = 'date'


class DateFieldWidget(DateField):
    widget = DateInput()


class VkLink(object):
    def __call__(self, form, field, message=None):
        m1 = field.data[:len(vk_link_prefix)] == vk_link_prefix
        regex = re.compile('^[a-zA-Z0-9_]+$', 0)
        m2 = regex.match(field.data[len(vk_link_prefix):] or '')
        if not m1 or not m2:
            raise ValidationError('ссылка на страницу ВКонтакте вида {}id12345678'.format(vk_link_prefix))
        return True


class Phone(object):
    def __init__(self, allow_empty):
        self.allow_empty = allow_empty

    def __call__(self, form, field, message=None):
        if self.allow_empty and field.data == '':
            return True
        regex = re.compile('^89[0-9]{9}$', 0)
        if not regex.match(field.data):
            raise ValidationError('телефон в формате 89012223344')
        return True
