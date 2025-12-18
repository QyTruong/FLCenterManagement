from flask_login import current_user
from models import Course, Lesson, Classroom, User, Student, Teacher, Staff, Section, Enrollment, Status, Score,Result
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
    if not student_id: #hary
        return  None

    query = Enrollment.query.filter(Enrollment.status.__eq__(Status.REGISTERED))\
                    .filter(Enrollment.student_id.__eq__(student_id)).all()

    for q in query:
        if q.section.course_id == course_id:
            return q

    return None

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
        Enrollment.status == Status.REGISTERED
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
            Enrollment.status == Status.REGISTERED
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










