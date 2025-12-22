from datetime import datetime

from sqlalchemy.exc import IntegrityError
from models import Course, Lesson, Classroom, User, Student, Teacher, Staff, Section, Enrollment, Invoice, Score, \
    Result, PaymentStatus
import hashlib
from courseapp import db
from flask_login import current_user
from sqlalchemy import func, case
from sqlalchemy.sql import extract

def get_courses():
    return Course.query.all()

def get_students():
    return Student.query.all()

def get_sections():
    return Section.query.order_by(Section.course_id).all()

def get_enrollments_pending(student_id=None):
    query = db.session.query(
                Enrollment,
            ).join(Invoice, Enrollment.invoice_id.__eq__(Invoice.id)) \
            .filter(
                Invoice.payment_status.__eq__(PaymentStatus.PENDING)
            )

    if student_id:
        query = query.filter(Enrollment.student_id.__eq__(student_id))

    return query.all()


def get_enrollments_paid(student_id=None):
    query = db.session.query(
                Enrollment,
            ).join(Invoice, Enrollment.invoice_id.__eq__(Invoice.id)) \
            .filter(
                Invoice.payment_status.__eq__(PaymentStatus.PAID)
            )

    if student_id:
        query = query.filter(Enrollment.student_id.__eq__(student_id))

    return query.all()

def get_enrollments(student_id=None):
    enrollments = Enrollment.query

    if student_id:
        enrollments = enrollments.filter(Enrollment.student_id.__eq__(student_id))

    return enrollments.all()


def get_enrollment_list():
    query = db.session.query(
                            Enrollment.id,
                            Enrollment.unit_price,
                            Enrollment.enroll_date,
                            Student.name,
                            Course.name,
                            Classroom.name
                        ).join(Student, Enrollment.student_id.__eq__(Student.id))\
                        .join(Section, Enrollment.section_id.__eq__(Section.id))\
                        .join(Classroom, Section.classroom_id.__eq__(Classroom.id))\
                        .join(Course, Section.course_id.__eq__(Course.id))\
                        .order_by(Student.name)

    return query.all()


def get_lessons_by_course_id(course_id):
    query = Lesson.query.filter(Lesson.active.__eq__(True))

    if course_id:
        query = query.filter(Lesson.course_id.__eq__(course_id))

    return query.all()

def get_course_by_id(course_id):
    return Course.query.get(course_id)


def get_sections_by_course_id(course_id):
    query = Section.query.filter(Section.active.__eq__(True))

    if course_id:
        query = query.filter(Section.course_id.__eq__(course_id))

    return query.all()

def get_section_by_id(section_id):
    query = db.session.query(
                            Section.schedule,
                            Course.id,
                            Course.price,
                            Course.name,
                            Classroom.name
                        ).join(Course, Section.course_id == Course.id)\
                        .join(Classroom, Section.course_id == Course.id)\
                        .filter(Section.id == section_id)

    return query.first()

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

def check_schedule_existed(schedule, student_id):
    query = db.session.query(Section) \
        .join(Enrollment, Enrollment.section_id == Section.id) \
        .filter(
            Enrollment.student_id.__eq__(student_id),
            Section.schedule.__eq__(schedule)
        )

    schedule_existed = query.first()
    if schedule_existed:
        return schedule_existed.schedule

    return None

def add_to_enrollment(section_id, unit_price, student_id):
    section = Section.query.filter(Section.id.__eq__(section_id)).first()
    classroom = Classroom.query.filter(Classroom.id.__eq__(section.classroom_id)).first()

    if section.current_size < classroom.capacity:
        enrollment = Enrollment(student_id=student_id, section_id=section_id, unit_price=unit_price, invoice_id=None)
        db.session.add(enrollment)

        section.current_size += 1
        db.session.commit()

        return True

    return False


def cancel_enrollment(enrollment_id):
    enrollment = Enrollment.query.filter(Enrollment.id.__eq__(enrollment_id)).first()
    section = Section.query.filter(Section.id.__eq__(enrollment.section_id)).first()

    if section.current_size > 0 and enrollment:
        db.session.delete(enrollment)
        section.current_size -= 1
        db.session.commit()

def get_enrollment_existed(course_id, student_id):
    query = db.session.query(Enrollment)\
        .join(Section, Section.id == Enrollment.section_id)\
        .filter(
            Enrollment.student_id.__eq__(student_id),
            Section.course_id.__eq__(course_id)
        ).first()

    return query

def get_invoices_by_student_id(student_id):
    query = db.session.query(
                Invoice.id
            ).select_from(Enrollment)\
            .join(
                Invoice,
                Enrollment.invoice_id == Invoice.id)\
            .filter(
                Enrollment.student_id == student_id,
                Invoice.payment_status == PaymentStatus.PENDING
            )

    print(query.first())
    if query.first():
        return query.first()[0]

    return None


def get_invoice_info(student_id=None):
    query = db.session.query(
            Enrollment.unit_price,
            Invoice.payment_date,
            Invoice.payment_status,
            Student.name,
            Course.name,
            Invoice.id,
        ).join(Student, Enrollment.student_id.__eq__(Student.id)) \
            .join(Invoice, Enrollment.invoice_id.__eq__(Invoice.id))\
            .join(Section, Enrollment.section_id.__eq__(Section.id))\
            .join(Course, Section.course_id.__eq__(Course.id))

    if student_id:
        query = query.filter(Enrollment.student_id.__eq__(student_id))

    return query.all()

def create_invoice(enrollments, invoice_id=None):
    flag = False
    for e in enrollments:
        if e.invoice_id and e.invoice.payment_status == PaymentStatus.PENDING:
            flag = True
            break

    if not flag:
        invoice = Invoice(staff=current_user.staff)
        db.session.add(invoice)
        for e in enrollments:
            if not e.invoice_id:
                e.invoice = invoice
                db.session.add(e)
    else:
        for e in enrollments:
            if not e.invoice_id:
                e.invoice_id = invoice_id
                db.session.add(e)

    db.session.commit()

def pay_invoice(invoice_id):
    invoice = Invoice.query.filter(Invoice.id.__eq__(invoice_id)).first()

    invoice.payment_status = PaymentStatus.PAID
    invoice.payment_date = datetime.now()
    db.session.add(invoice)
    db.session.commit()


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



#========================================= Hary
# ============================
# STUDENT
# ============================
def get_student_profile(student_id):
    return Student.query.get(student_id)

def update_student_profile(student_id, name, email):
    student = Student.query.get(student_id)
    if student:
        student.name = name
        student.email = email
        db.session.commit()
    return student


def get_course_by_student(student_id):
    q = (
        db.session.query(Course)
        .join(Section)
        .join(Enrollment)
        .filter(Enrollment.student_id == student_id)
        .distinct()
    )
    return q.all()


def get_schedule_of_student(student_id):
    """
    Lấy lịch học của student (rút gọn), trả về list Section
    """
    q = (
        db.session.query(Section)
        .join(Course)
        .join(Enrollment)
        .filter(Enrollment.student_id == student_id)
        .distinct()
    )
    return q.all()


def get_scores_of_student(student_id):
    """
    Lấy danh sách điểm của student
    """
    return db.session.query(
        Score,
        Course.name.label("course_name"),
        Section.id.label("section_id")
    ).join(
        Enrollment, Score.enrollment_id == Enrollment.id
    ).join(
        Section, Section.id == Enrollment.section_id
    ).join(
        Course, Course.id == Section.course_id
    ).filter(
        Enrollment.student_id == student_id
    ).all()

#=============TEACHER========
# Lấy teacher theo id
def get_teacher_by_id(teacher_id):
    return Teacher.query.get(teacher_id)

# Cập nhật thông tin teacher
def update_teacher_profile(teacher_id, name=None, email=None, avatar=None, specialization=None):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        if name is not None:
            teacher.name = name
        if email is not None:
            teacher.email = email
        if avatar is not None:
            teacher.avatar = avatar
        if specialization is not None:
            teacher.specialization = specialization
        db.session.commit()
    return teacher

#teacher section hary
# --- DAO cho Teacher ---

# Lấy tất cả sections mà teacher đang dạy
# DAO cho teacher
def get_sections_by_teacher(teacher_id):
    q = (
        db.session.query(Section)
        .join(Course, Course.id == Section.course_id)
        .join(Classroom, Classroom.id == Section.classroom_id)
        .filter(Section.teacher_id == teacher_id)
        .all()
    )
    return q


# Lấy danh sách học viên trong Section
def get_students_by_section(section_id):
    q = (
        db.session.query(Student)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .filter(
            Enrollment.section_id == section_id
        )
        .all()
    )
    return q



def get_enrollments_by_section(section_id):
    return (
        db.session.query(Enrollment, Student)
        .join(Student, Student.id == Enrollment.student_id)
        .filter(Enrollment.section_id == section_id)
        .all()
    )

#luu diem
def save_score(enrollment_id, score_value, score_type, attendance=0):
    s = Score.query.filter(
        Score.enrollment_id == enrollment_id,
        Score.type == score_type
    ).first()

    if not s:
        s = Score(
            enrollment_id=enrollment_id,
            type=score_type,
            score=score_value,
            result=Result.FAILURE
        )
        db.session.add(s)

    s.score = score_value
    db.session.commit()