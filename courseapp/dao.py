from models import Course, Lesson, Class, Schedule, User, Student, Teacher, Staff
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

def get_classes(course_id):
    query = Class.query.filter(Class.active.__eq__(True))

    if course_id:
        query = query.filter(Class.course_id.__eq__(course_id))

    return query.all()

def get_schedules(class_id):
    query = Schedule.query.filter(Schedule.active.__eq__(True))

    if class_id:
        query = query.filter(Schedule.class_id.__eq__(class_id))

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
