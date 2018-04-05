from flask_login import current_user


def is_section_removable(section): return section.groups.count() == 0 and section.section_preferences.count() == 0


def is_school_removable(school): return school.students.count() == 0


def is_citizenship_removable(citizenship): return citizenship.students.count() == 0


def is_parent_removable(parent): return parent.parent_of_students.count() == 0


def is_group_removable(group): return group.students_in_group.count() == 0 and group.lessons.count() == 0


def is_student_removable(student): pass


def is_teacher_removable(teacher): pass


def is_master_removable(master): return master.system_user_id != current_user.id
