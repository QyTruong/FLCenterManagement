from flask import render_template, request, jsonify, url_for, session
from werkzeug.utils import redirect
from courseapp import app, dao, login, utils
from flask_login import login_user, logout_user, current_user
import cloudinary.uploader


@app.route('/')
def index():

    return render_template('index.html')

@app.route('/courses')
def course_list():
    courses = dao.get_courses()

    return render_template('course_list.html', courses=courses)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    lessons = dao.get_lessons_by_course_id(course_id=course_id)
    course = dao.get_course_by_id(course_id=course_id)
    sections = dao.get_sections_by_course_id(course_id=course_id)
    enrollment_existed = None
    if current_user.is_authenticated:
        enrollment_existed = dao.get_enrollment_existed(course_id=course_id, student_id=current_user.id)

    return render_template('course_detail.html',
                           lessons=lessons,
                           course=course,
                           sections=sections,
                           enrollment_existed=enrollment_existed)


@app.route('/api/enroll-section', methods=['POST'])
def enroll_section():
    section_id = int(request.json.get('section_id'))
    section = dao.get_section_by_id(section_id=section_id)
    schedule = section[0]
    unit_price = section[2]
    course_name = section[3]
    classroom_name = section[4]

    try:
        schedule_existed = dao.check_schedule_existed(schedule=schedule, student_id=current_user.id)
        if not schedule_existed:
            enroll = dao.add_to_enrollment(section_id=section_id, unit_price=unit_price, student_id=current_user.id)
            if not enroll:
                return {'message': 'Lớp học đã đủ số lượng học viên, vui lòng đăng ký lớp khác'}
            else:
                utils.send_email_enrollment(course_name=course_name, classroom_name=classroom_name, schedule=schedule, unit_price=unit_price, student=current_user.student)
                return {'message': 'Đăng ký thành công !!'}
        else:
            return {'message': f'Phiên học {schedule_existed} đã được đăng ký, vui lòng đăng phiên học khác !!'}

    except Exception as e:
        return {'message': str(e)}


@app.route('/api/cancel-section', methods=['PATCH'])
def cancel_section():
    enrollment_id = int(request.json.get('id'))

    try:
        dao.cancel_enrollment(enrollment_id=enrollment_id)
    except Exception as e:
        return {'message': str(e)}

    return {'message': 'Hủy đăng ký thành công !!'}


@app.route('/staff-enroll-section')
def staff_enroll_section_view():
    students = dao.get_students()
    sections = dao.get_sections()
    enrollments = dao.get_enrollment_list()

    return render_template('staff_enroll.html',
                           students=students,
                           sections=sections,
                           enrollments=enrollments)

@app.route('/api/staff-enroll-section', methods=["POST"])
def staff_enroll_section():
    student_id = request.json.get('student_id')
    section_id = request.json.get('section_id')
    section = dao.get_section_by_id(section_id=section_id)
    schedule = section[0]
    course_id = section[1]
    unit_price = section[2]
    enrollment_existed = dao.get_enrollment_existed(course_id=course_id, student_id=student_id)

    try:
        if enrollment_existed:
            return {'message': 'Học viên đã đăng ký khóa học này, vui lòng đăng ký khóa học khác !!'}

        schedule_existed = dao.check_schedule_existed(schedule=schedule, student_id=student_id)
        if not schedule_existed:
            enroll = dao.add_to_enrollment(section_id=section_id, unit_price=unit_price, student_id=student_id)
            if not enroll:
                return {'message': 'Lớp học đã đủ số lượng học viên, vui lòng đăng ký lớp khác !!'}
            else:
                return {'message': 'Đăng ký thành công'}
        else:
            return {'message': f'Phiên học {schedule_existed} đã được đăng ký, vui lòng đăng phiên học khác !!'}

    except Exception as e:
        return {'message': str(e)}


@app.route('/invoice-creating')
def invoice_creating():
    student_id = request.args.get('student_id')
    students = dao.get_students()
    enrollments = None
    total = None

    if student_id:
        enrollments = dao.get_invoices_by_student_id(student_id=student_id)
        total = utils.cal_amount(enrollments)

    return render_template('invoice_creating.html', students=students, enrollments=enrollments, total=total)

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
                err_msg = 'Mật khẩu xác nhận không khớp !!'
        except Exception as ex:
            err_msg = 'Hệ thống đang gặp lỗi: ' + str(ex)

    return render_template('account_register.html', err_msg=err_msg)

@app.route('/login-account')
def login_view():
    return render_template('account_login.html')

@app.route('/login-account', methods=['POST'])
def login_account():
    err_msg = ''

    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)

    if user:
        login_user(user=user)
        next = request.args.get('next')

        if user.staff and user.staff.is_admin:
           return redirect('/admin')

        return redirect(next if next else '/')

    else:
        err_msg = 'Tài khoản hoặc mật khẩu không đúng !!'

    return render_template('account_login.html', err_msg=err_msg)

@app.route('/account-logout')
def logout_account():
    logout_user()
    return redirect(url_for('index'))

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    from courseapp.admin import admin

    app.run(debug=True)
    # with app.app_context():
    #     from flask_login import login_user
    #
    #     with app.test_request_context('/'):
    #         user = dao.auth_user('student1', '1')
    #         login_user(user)
    #         print(user.admin.name)
    #
    #     # load_user(user_id=user.id)
    #     # print(current_user.student.name)

    # result1 = cloudinary.uploader.upload("static/images/beginner.png")
    # result2 = cloudinary.uploader.upload("static/images/intermediate.jpg")
    # result3 = cloudinary.uploader.upload("static/images/advanced.jpg")
    # print(result1['secure_url'])
    # print(result2['secure_url'])
    # print(result3['secure_url'])
