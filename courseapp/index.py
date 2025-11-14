from flask import render_template, request
from courseapp import app, dao

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/course')
def course_register():
    courses = dao.load_courses()

    return render_template('course_register.html', courses=courses)

@app.route('/course/<course_id>')
def course_detail(course_id):
    lessons = dao.load_lessons(course_id)
    course = dao.load_course_by_id(course_id)

    return render_template('course_detail.html', lessons=lessons, course=course)


if __name__ == '__main__':
    from courseapp.admin import admin

    app.run(debug=True)