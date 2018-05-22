from app.mail import send_email
from app.models import StudentInGroup, Group, vk_link_prefix, shift_vk, shift_email
from app.vk import send_vk_messages


def parents_of_student_in_group(student_in_group_id):
    return StudentInGroup.query.get_or_404(student_in_group_id).student.parents.all()


def parents_of_group(group_id):
    parents = []
    for student in Group.query.get_or_404(group_id).students:
        for parent in student.parents:
            parents.append(parent)
    return parents


def do_send_notification(parents, subject, body):
    emails = []
    vk_domains = set()
    vk_links = set()
    for parent in parents:
        if parent.notification_types & (1 << shift_email) != 0:
            emails.append(parent.email)
        if parent.notification_types & (1 << shift_vk) != 0:
            vk_domains.add(parent.vk_link[len(vk_link_prefix):])
            vk_links.add(parent.vk_link)
    if len(emails) == 0 and len(vk_domains) == 0: return None
    if len(emails) > 0: send_email(subject, body, emails)
    if len(vk_domains) > 0: send_vk_messages(subject, body, vk_domains)
    return '{}\n{}'.format('\n'.join(emails), '\n'.join(vk_links))
