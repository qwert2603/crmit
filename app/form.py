import re

from wtforms import DateField, ValidationError
from wtforms.widgets import Input

from app.models import vk_link_prefix


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


# todo:
class Phone(object):
    def __call__(self, form, field, message=None):
        regex = re.compile('^89[0-9]{9}$', 0)
        if regex.match(field.data[len(vk_link_prefix):] or ''):
            raise ValidationError('телефон в формате 89012223344')
        return True
