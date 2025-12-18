from flask import render_template, request, jsonify, url_for, session
from werkzeug.utils import redirect
from courseapp import app, dao, login,db
from flask_login import login_user, logout_user, current_user
import cloudinary.uploader

from courseapp.dao import save_score


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses')
def course_list():
    courses = dao.get_courses()

    return render_template('course_register.html', courses=courses)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    lessons = dao.get_lessons(course_id=course_id)
    course = dao.get_course_by_id(course_id=course_id)
    sections = dao.get_sections(course_id=course_id)
    enrollment_existed = dao.get_enrollment_existed(student_id=current_user.id, course_id=course_id)

    return render_template('course_detail.html', lessons=lessons, course=course, sections=sections, enrollment_existed=enrollment_existed)

@app.route('/api/enroll-section', methods=['POST'])
def enroll_section():
    section_id = request.json.get('section_id')
    unit_price = request.json.get('price')

    try:
        dao.add_to_enrollment(current_user.id, section_id, unit_price)
    except Exception as e:
        return {'status': "fail", 'message': str(e)}

    return {'status': 'success', 'message': 'Đăng ký thành công'}


@app.route('/api/cancel-section', methods=['PATCH'])
def cancel_section():
    enrollment_id = int(request.json.get('id'))

    try:
        dao.cancel_enrollment(enrollment_id=enrollment_id)
    except Exception as e:
        return {'message': str(e)}

    return {'message': 'Hủy đăng ký thành công'}


@app.route('/register-account', methods=['GET', 'POST'])
def register_account():
    err_msg = ''

    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        email = request.form.get('email')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                dao.add_user(name=name, username=username, password=password, email=email, avatar=avatar_path)
                return redirect(url_for('login_account'))
            else:
                err_msg = 'Mật khẩu xác nhận không khớp !!!'
        except Exception as ex:
            err_msg = 'Hệ thống đang gặp lỗi' + str(ex) + '!!!'

    return render_template('account_register.html', err_msg=err_msg)

@app.route('/login-account', methods=['GET', 'POST'])
def login_account():
    err_msg = ''

    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)

        if user:
            login_user(user=user)
            return redirect(url_for('index'))
        else:
            err_msg = 'Tài khoản hoặc mật khẩu không đúng'

    return render_template('account_login.html', err_msg=err_msg)

@app.route('/account-logout')
def logout_account():
    logout_user()
    return redirect(url_for('index'))

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

#hary

@app.route("/student-profile")
def student_profile():
    return render_template("student_profile.html",user=current_user)

@app.route("/student-profile/edit", methods=["GET", "POST"])
def student_profile_edit():
    if not current_user.is_authenticated:
        return redirect(url_for('login_account'))

    student = current_user.student

    if request.method == "POST":
        student.name = request.form.get("name")
        student.email = request.form.get("email")
        db.session.commit()
        return redirect(url_for('student_profile'))

    return render_template("student_profile_edit.html", student=student)



@app.route("/student-courses")
def student_courses():
    if not current_user.is_authenticated:
        return redirect(url_for('login_account'))
    courses = dao.get_course_by_student(current_user.id)
    return render_template("student_courses.html", courses=courses)

@app.route("/student-course/<int:course_id>")
def student_course_detail(course_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login_account'))

    # Lấy danh sách course student đang học
    courses = dao.get_course_by_student(current_user.id)

    # Lọc ra course muốn xem
    course = next((c for c in courses if c.id == course_id), None)
    if not course:
        return "Bạn chưa đăng ký khóa học này hoặc khóa học không tồn tại", 404

    # Lấy lessons
    lessons = dao.get_lessons(course_id)

    # Lấy sections mà student đã đăng ký
    enrollment = dao.get_enrollment_existed(current_user.id, course_id)

    return render_template(
        "student_courses_detail.html",
        course=course,
        lessons=lessons,
        enrollment=enrollment
    )


#hary
@app.route("/student-schedule")
def student_schedule():
    if not current_user.is_authenticated:
        return redirect(url_for("login_account"))

    schedules = dao.get_schedule_of_student(current_user.role.id)
    return render_template("student_schedule.html", schedules=schedules)



#hary
# @app.route("/student-score")
# def student_scores():
#     if not current_user.is_authenticated:
#         return redirect(url_for('login_account'))
#
#     scores = dao.get_scores_by_student(current_user.id)
#     return render_template("student_score.html", scores=scores)


# --- ROUTE CHO HỌC SINH XEM ĐIỂM ---
@app.route("/student-score")
def student_scores():
    if not current_user.is_authenticated:
        return redirect(url_for('login_account'))

    raw_scores = dao.get_scores_by_student(current_user.id)

    courses_data = {}
    all_extra_types = set()  # Để lấy danh sách tất cả các loại điểm (Miệng, Tay...)

    for course, score, enrollment in raw_scores:
        if course.id not in courses_data:
            courses_data[course.id] = {
                'name': course.name,
                'scores': {}
            }

        # Lưu điểm: {'mid': 9, 'Tay': 10...}
        courses_data[course.id]['scores'][score.type] = score.score

        # Nếu không phải GK, CK thì cho vào danh sách cột chung
        if score.type not in ['mid', 'final', 'att']:
            all_extra_types.add(score.type)

    # Chuyển set thành list để ổn định thứ tự cột
    extra_cols = sorted(list(all_extra_types))

    return render_template("student_score.html",
                           courses=courses_data.values(),
                           extra_cols=extra_cols)

@app.route("/teacher-profile")
def teacher_profile():
    return render_template("teacher_profile.html", teacher=current_user.teacher)


@app.route("/teacher-attendance")
def teacher_attendance():
    if not current_user.is_authenticated or not current_user.teacher:
        return redirect(url_for("login_account"))

    sections = dao.get_sections_by_teacher(current_user.id)
    return render_template("teacher_attendance.html", sections=sections)


# @app.route("/teacher-attendance/<int:section_id>", methods=["GET", "POST"])
# def teacher_attendance_section(section_id):
#     if not current_user.is_authenticated or not current_user.teacher:
#         return redirect(url_for("login_account"))
#
#     students = dao.get_students_by_section(section_id)  # [(Enrollment, Student), ...]
#
#     if request.method == "POST":
#         for enrollment, student in students:
#             checked = request.form.get(f"att_{student.id}") is not None
#             enrollment.attendance = checked
#         db.session.commit()
#         # Sau khi lưu xong, redirect sang trang kết quả
#         return redirect(url_for("teacher_attendance_result", section_id=section_id))
#
#     return render_template(
#         "teacher_attendance_section.html",
#         students=students,
#         section_id=section_id
#     )
#
#
# @app.route("/teacher-attendance/<int:section_id>/result")
# def teacher_attendance_result(section_id):
#     if not current_user.is_authenticated or not current_user.teacher:
#         return redirect(url_for("login_account"))
#
#     # Lấy danh sách học viên cùng enrollment
#     students = dao.get_students_by_section(section_id)  # [(Enrollment, Student), ...]
#
#     return render_template(
#         "teacher_attendance_result.html",
#         students=students,
#         section_id=section_id
#     )

@app.route("/teacher-section/<int:section_id>/attendance", methods=["GET", "POST"])
def teacher_attendance_section(section_id):
    if not current_user.is_authenticated or not current_user.teacher:
        return redirect(url_for("login_account"))

    # Lấy danh sách học viên cùng Enrollment
    students = dao.get_students_by_section(section_id)  # [(Enrollment, Student), ...]

    if request.method == "POST":
        # Lưu trạng thái điểm danh
        for enrollment, student in students:
            enrollment.attendance = bool(request.form.get(f"att_{student.id}"))
        db.session.commit()
        return redirect(url_for("teacher_attendance_result", section_id=section_id))

    return render_template(
        "teacher_attendance_section.html",
        students=students,
        section_id=section_id
    )

# Trang kết quả điểm danh
@app.route("/teacher-section/<int:section_id>/attendance-result")
def teacher_attendance_result(section_id):
    if not current_user.is_authenticated or not current_user.teacher:
        return redirect(url_for("login_account"))

    students = dao.get_students_by_section(section_id)
    return render_template(
        "teacher_attendance_result.html",
        students=students,
        section_id=section_id
    )


#hary xem hoc vien lop
@app.route("/teacher-sections")
def teacher_sections():
    if not current_user.is_authenticated or not current_user.teacher:
        return redirect(url_for("login_account"))

    sections = dao.get_sections_by_teacher(current_user.id)
    return render_template("teacher_sections.html", sections=sections)


@app.route("/teacher-section/<int:section_id>/students")
def teacher_view_students(section_id):
    if not current_user.is_authenticated or not current_user.teacher:
        return redirect(url_for("login_account"))

    students_attendance = dao.get_attendance_by_section(section_id)  # [(Enrollment, Student), ...]
    return render_template(
        "teacher_view_students.html",
        students_attendance=students_attendance,
        section_id=section_id
    )


@app.route("/teacher-input-score")
def teacher_input_score_default():
    if not current_user.is_authenticated or not current_user.teacher:
        return redirect(url_for("login_account"))

    # Tìm danh sách lớp của ông thầy này
    sections = dao.get_sections_by_teacher(current_user.id)
    if not sections:
        return "Bạn chưa được phân công dạy lớp nào!", 404

    # Lấy ID của lớp đầu tiên để chuyển hướng
    section_id = sections[0].id

    # SỬA Ở ĐÂY: Phải dùng tên hàm xử lý và truyền tham số section_id
    return redirect(url_for('teacher_input_scores', section_id=section_id))


# --- ROUTE CHO GIÁO VIÊN NHẬP ĐIỂM ---
@app.route("/teacher-section/<int:section_id>/score", methods=["GET", "POST"])
def teacher_input_scores(section_id):
    if not current_user.is_authenticated or not current_user.teacher:
        return redirect(url_for("login_account"))

    students = dao.get_students_by_section(section_id)

    if request.method == "POST":
        for enrollment, student in students:
            # Lưu điểm mặc định
            mid = request.form.get(f"mid_{student.id}", 0)
            final = request.form.get(f"final_{student.id}", 0)
            dao.save_score(enrollment.id, mid, "mid")
            dao.save_score(enrollment.id, final, "final")

            # Quét Form lưu các cột Extra
            for key, value in request.form.items():
                if key.startswith("extra_score_") and f"_{student.id}" in key:
                    col_name = key.split('_')[2]
                    if col_name:
                        dao.save_score(enrollment.id, value, col_name)
        return redirect(url_for("teacher_input_scores", section_id=section_id))

    extra_cols = dao.get_extra_column_names(section_id)
    raw_scores = dao.get_scores_by_section(section_id)
    scores_map = {}
    for s in raw_scores:
        if s.enrollment_id not in scores_map: scores_map[s.enrollment_id] = {}
        scores_map[s.enrollment_id][s.type] = s.score

    return render_template("teacher_input_score.html", section_id=section_id,
                           students=students, scores_map=scores_map, extra_cols=extra_cols)

# --- API XÓA CỘT (FIX LỖI JOIN) ---
@app.route("/api/delete-column", methods=["POST"])
def api_delete_column():
    data = request.json
    try:
        from courseapp import db
        from models import Score, Enrollment
        # 1. Tìm ID các bản ghi cần xóa
        score_ids = db.session.query(Score.id).join(Enrollment)\
            .filter(Enrollment.section_id == data['section_id'], Score.type == data['col_name']).all()
        ids = [s[0] for s in score_ids]
        # 2. Xóa theo ID (Không bao giờ lỗi Join)
        if ids:
            db.session.query(Score).filter(Score.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}


if __name__ == '__main__':
    from courseapp.admin import admin

    app.run(debug=True)