from models import Course, Lesson, Classroom, User, Student, Teacher, Staff, Section, Enrollment, Status
import hashlib
from courseapp import db
from flask_login import current_user

def get_courses():
    return Course.query.all()

def get_course_by_id(course_id):
    return Course.query.get(course_id)

def get_lessons(course_id):
    query = Lesson.query.filter(Lesson.active.__eq__(True))

    if course_id:
        query = query.filter(Lesson.course_id.__eq__(course_id))

    return query.all()

def get_sections(course_id):
    query = Section.query.filter(Section.active.__eq__(True))

    if course_id:
        query = query.filter(Section.course_id.__eq__(course_id))

    return query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def auth_user(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(
            User.username.__eq__(username.strip()),
            User.password.__eq__(password)).first()

    return None

def add_user(name, username, password, email, avatar=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    student = Student(name=name, email=email, avatar=avatar)
    user = User(username=username, password=password, student=student)

    db.session.add(user)
    db.session.add(student)
    db.session.commit()

def check_schedule_existed(schedule):
    query = db.session.query(Section) \
        .join(Enrollment, Enrollment.section_id.__eq__(Section.id)) \
        .filter(
        Enrollment.status == Status.REGISTERED,
        Enrollment.student_id == current_user.id,
        Section.schedule == schedule
    )

    schedule_existed = query.first()
    if schedule_existed:
        return schedule_existed.schedule

    return None

def add_to_enrollment(section_id, unit_price):
    section = Section.query.filter(Section.id.__eq__(section_id)).first()
    classroom = Classroom.query.filter(Classroom.id.__eq__(section.classroom_id)).first()

    if section.current_size < classroom.capacity:
        enrollment = Enrollment(student_id=current_user.id, section_id=section_id, unit_price=unit_price)
        db.session.add(enrollment)
        section.current_size += 1
        db.session.commit()

        return True

    return False


def cancel_enrollment(enrollment_id):
    enrollment = Enrollment.query.filter(Enrollment.id.__eq__(enrollment_id)).first()
    section = Section.query.filter(Section.id.__eq__(enrollment.section_id)).first()

    if section.current_size > 0 and enrollment:
        enrollment.status = Status.CANCELLED
        section.current_size -= 1
        db.session.commit()



def get_enrollment_existed(course_id):
    if current_user.is_authenticated:
        query = db.session.query(Enrollment) \
            .join(Section, Section.id == Enrollment.section_id) \
            .filter(
            Enrollment.student_id.__eq__(current_user.id),
            Section.course_id.__eq__(course_id),
            Enrollment.status.__eq__(Status.REGISTERED)
        ).first()

        return query

    return None


