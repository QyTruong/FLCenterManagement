from flask import render_template, request
from courseapp import app, dao

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
    classes = dao.get_classes(course_id)

    return render_template('course_detail.html', lessons=lessons, course=course, classes=classes)


if __name__ == '__main__':
    from courseapp.admin import admin

    app.run(debug=True)