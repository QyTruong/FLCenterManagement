from flask import render_template, request, jsonify, url_for, session
from werkzeug.utils import redirect
from courseapp import app, dao, login
from flask_login import login_user, logout_user
import cloudinary.uploader


@app.route('/')
def index():

    return render_template('index.html')

@app.route('/courses')
def course_list():
    courses = dao.get_courses()

    return render_template('course_register.html', courses=courses)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    lessons = dao.get_lessons(course_id)
    course = dao.get_course_by_id(course_id)

    return render_template('course_detail.html', lessons=lessons, course=course)

@app.route('/api/class-list/<int:course_id>', methods=['GET'])
def class_list(course_id):
    classes = dao.get_classes(course_id)

    data = []

    for c in classes:
        schedule_list = []

        for s in c.schedules:
            schedule_list.append({
                'day_of_week' : s.day_of_week,
                'start_time' : s.start_time.strftime('%H:%M') if s.start_time else None,
                'end_time' : s.end_time.strftime('%H:%M') if s.start_time else None
            })

        data.append({
            'id': c.id,
            'name': c.name,
            'max_student' : c.max_student,
            'schedules': schedule_list
        })

    return jsonify(data)

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


if __name__ == '__main__':
    from courseapp.admin import admin

    app.run(debug=True)