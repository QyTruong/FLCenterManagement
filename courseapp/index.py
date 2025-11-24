from flask import render_template, request, jsonify
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

    return render_template('course_detail.html', lessons=lessons, course=course)

@app.route('/api/class-list/<int:course_id>', methods=['GET'])
def class_list(course_id):
    classes = dao.get_classes(course_id)

    data = []

    for c in classes:
        schedule_list = []

        # duyệt từng lịch học
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

if __name__ == '__main__':
    from courseapp.admin import admin

    app.run(debug=True)