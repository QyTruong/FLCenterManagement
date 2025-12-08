from sqlalchemy.exc import IntegrityError
from models import Course, Lesson, Classroom, User, Student, Teacher, Staff, Section, Enrollment, Invoice, Score, Result, Status
import hashlib
from courseapp import db
from flask_login import current_user
from sqlalchemy import func, case
from sqlalchemy.sql import extract

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
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Username này đã tồn tại !')

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

#------THÔNG KÊ---------

def course_stats():
    return db.session.query(Course.id, Course.name, func.count(Lesson.id))\
        .join(Lesson, Course.id.__eq__(Lesson.course_id))\
        .group_by(Course.id, Course.name).all()


def number_of_student_stats(kw=None, from_date=None, to_date=None):
    q = db.session.query(Course.id, Course.name, func.count(Enrollment.id))\
        .join(Section, Course.id.__eq__(Section.course_id), isouter=True)\
        .join(Enrollment, Section.id.__eq__(Enrollment.section_id),isouter=True)\
        .group_by(Course.id, Course.name)

    if kw:
        q = q.filter(Course.name.contains(kw))

    if from_date:
        q = q.filter(Enrollment.enroll_date.__ge__(from_date))

    if to_date:
        q = q.filter(Enrollment.enroll_date.__le__(to_date))

    return q.all()


def revenue_by_month_stats(year):

    return db.session.query(extract('month', Invoice.payment_date), func.sum(Invoice.amount))\
        .filter(extract('year', Invoice.payment_date) == year)\
        .group_by(extract('month', Invoice.payment_date))\
        .order_by(extract('month', Invoice.payment_date)).all()


def pass_rate_stats(from_date=None, to_date=None):

    q= db.session.query(Course.name, func.count(Score.id),
                        func.sum(case((Score.result.__eq__(Result.SUCCESS),1), else_=0)),
                        (func.sum(case((Score.result.__eq__(Result.SUCCESS),1), else_=0))*100 / func.count(Score.id)))\
                        .join(Section, Section.course_id.__eq__(Course.id), isouter=True)\
                        .join(Enrollment, Enrollment.section_id.__eq__(Section.id), isouter=True)\
                        .join(Score, Score.enrollment_id.__eq__(Enrollment.id), isouter=True)\
                        .group_by(Course.name)

    if from_date:
        q = q.filter(Enrollment.enroll_date.__ge__(from_date))

    if to_date:
        q = q.filter(Enrollment.enroll_date.__le__(to_date))

    return q.all()
