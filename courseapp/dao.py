from models import Course, Lesson, Classroom, User, Student, Teacher, Staff, Section, Enrollment, EnrollStatus, Score, Invoice, Result
from sqlalchemy.exc import IntegrityError
import hashlib
from courseapp import db
from flask_login import current_user
from sqlalchemy import func, case
from sqlalchemy.sql import extract
from datetime import datetime

def get_courses():
    return Course.query.all()

def get_students():
    return Student.query.all()

def get_sections():
    return Section.query.order_by(Section.course_id).all()

def get_enrollment_list():
    query = db.session.query(
                            Enrollment.id,
                            Enrollment.unit_price,
                            Enrollment.status,
                            Enrollment.invoice_id,
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

def get_invoices_by_student_id(student_id=None):
    query = db.session.query(
            Enrollment.unit_price,
            Invoice.payment_date,
            Invoice.payment_status,
            Student.name,
            Course.name,
            Enrollment.id
        ).join(Student, Enrollment.student_id.__eq__(Student.id)) \
            .join(Invoice, Enrollment.invoice_id.__eq__(Invoice.id))\
            .join(Section, Enrollment.section_id.__eq__(Section.id))\
            .join(Course, Section.course_id.__eq__(Course.id)) \
            .filter(
                Enrollment.status.__eq__(EnrollStatus.REGISTERED)
            )

    if student_id:
        query = query.filter(Enrollment.student_id.__eq__(student_id))

    print(query.all())

    return query.all()

def get_lessons_by_course_id(course_id):
    query = Lesson.query.filter(Lesson.active.__eq__(True))

    if course_id:
        query = query.filter(Lesson.course_id.__eq__(course_id))

    return query.all()

def get_course_by_id(course_id):
    return Course.query.get(course_id)

def get_student_by_id(student_id):
    return Student.query.filter(Student.id.__eq__(student_id)).first()

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
        .join(Enrollment, Enrollment.section_id.__eq__(Section.id)) \
        .filter(
        Enrollment.status.__eq__(EnrollStatus.REGISTERED),
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
    enrollment_cancelled_existing = Enrollment.query.filter(
        Enrollment.status.__eq__(EnrollStatus.CANCELLED),
        Enrollment.student_id.__eq__(student_id),
        Enrollment.section_id.__eq__(section_id)
    ).first()

    if section.current_size < classroom.capacity:
        if enrollment_cancelled_existing:
            enrollment_cancelled_existing.status = EnrollStatus.REGISTERED
            enrollment_cancelled_existing.enroll_date = datetime.now()
        else:
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
        enrollment.status = EnrollStatus.CANCELLED
        enrollment.enroll_date = datetime.now()
        section.current_size -= 1
        db.session.commit()

def get_enrollment_existed(course_id, student_id):
    query = db.session.query(Enrollment)\
        .join(Section, Section.id == Enrollment.section_id)\
        .filter(
        Enrollment.student_id.__eq__(student_id),
        Section.course_id.__eq__(course_id),
        Enrollment.status.__eq__(EnrollStatus.REGISTERED)
    ).first()

    return query



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
#hary # lay ds student register
def get_scores_by_section(section_id):
    # Dùng join y chang style của mày
    q = db.session.query(Score) \
        .join(Enrollment, Enrollment.id == Score.enrollment_id) \
        .filter(Enrollment.section_id == section_id)

    return q.all()


#haru schedule
def get_schedule_of_student(student_id):
    q = (
        db.session.query(
            Section.schedule,
            Classroom.name,
            Course.name,
            Teacher.name

        )
        .join(Enrollment, Enrollment.section_id == Section.id)
        .join(Classroom, Classroom.id == Section.classroom_id)
        .join(Course, Course.id == Section.course_id)
        .join(Teacher, Teacher.id == Section.teacher_id)
        .filter(Enrollment.student_id == student_id)

    )
    return q.all()


#hary, teacher_page lay ds hoc sinh cai'
def get_students_by_section(section_id):
    q = db.session.query(
        Enrollment,
        Student
    )\
    .join(Student, Student.id == Enrollment.student_id)\
    .filter(
        Enrollment.section_id == section_id,
        Enrollment.status == EnrollStatus.REGISTERED
    )
    return q.all()

def get_attendance_by_section(section_id):
    q = db.session.query(Enrollment, Student)\
        .join(Student, Student.id == Enrollment.student_id)\
        .filter(Enrollment.section_id == section_id)
    return q.all()




def save_attendance(enrollment_id, status: bool):
    enrollment = db.session.get(Enrollment, enrollment_id)
    if enrollment:
        enrollment.attendance = status
        db.session.commit()


def get_extra_column_names(section_id):
    # Lấy tất cả các loại điểm (type) duy nhất của lớp này trừ các cột mặc định
    query = db.session.query(Score.type).distinct() \
        .join(Enrollment, Score.enrollment_id == Enrollment.id) \
        .filter(Enrollment.section_id == section_id) \
        .filter(~Score.type.in_(['mid', 'final', 'att']))

    return [r[0] for r in query.all()]

# Hàm save_score giữ nguyên logic, chỉ đảm bảo check update/insert chuẩn
def save_score(enrollment_id, score_value, score_type, attendance=False):
    s = Score.query.filter(
        Score.enrollment_id == enrollment_id,
        Score.type == score_type
    ).first()

    if s is None:
        s = Score(
            enrollment_id=enrollment_id,
            type=score_type,
            result=Result.FAILURE,  # Mặc định
            attendance=attendance
        )
        db.session.add(s)

    # Ép kiểu float nếu có giá trị, nếu rỗng thì là 0
    try:
        val = float(score_value)
    except:
        val = 0

    s.score = val
    s.attendance = attendance

    # Logic tự động xét Đạt/Không đạt (nếu thích)
    if s.type == 'final' or s.type == 'mid':  # Ví dụ thôi
        if val >= 5:
            s.result = Result.SUCCESS
        else:
            s.result = Result.FAILURE

    db.session.commit()



def get_scores_by_student(student_id):
    # Trả về đúng tuple (Course, Score, Enrollment) như mày muốn
    q = db.session.query(Course, Score, Enrollment)\
        .join(Section, Course.id == Section.course_id)\
        .join(Enrollment, Section.id == Enrollment.section_id)\
        .join(Score, Enrollment.id == Score.enrollment_id)\
        .filter(
            Enrollment.student_id == student_id,
            Enrollment.status == EnrollStatus.REGISTERED
        )
    return q.all()




#lay ds gv day
def get_sections_by_teacher(teacher_id):
    return Section.query.filter(
        Section.teacher_id == teacher_id
    ).all()


#lay diem
def get_score(enrollment_id, score_type):
    return Score.query.filter(
        Score.enrollment_id == enrollment_id,
        Score.type == score_type
    ).first()










