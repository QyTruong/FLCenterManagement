from models import Course, Lesson, Classroom, User, Student, Teacher, Staff, Section, Enrollment, Status
import hashlib
from courseapp import db

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

def add_to_enrollment(student_id, section_id, unit_price):
    enrollment = Enrollment(student_id=student_id, section_id=section_id, unit_price=unit_price)
    db.session.add(enrollment)
    db.session.commit()

def cancel_enrollment(enrollment_id):
    e = Enrollment.query.filter(Enrollment.id.__eq__(enrollment_id)).first()

    if e:
        e.status = Status.CANCELLED
        print(e.status)
        db.session.commit()


def get_enrollment_existed(student_id, course_id):
    query = Enrollment.query.filter(Enrollment.status.__eq__(Status.REGISTERED))\
                    .filter(Enrollment.student_id.__eq__(student_id)).all()

    for q in query:
        if q.section.course_id == course_id:
            return q

    return None

