from flask import render_template
from courseapp import app, dao

@app.route('/')
def index():
    levels = dao.load_levels()

    return render_template('index.html', levels=levels)

@app.route('/course')
def load_courses():
    courses = dao.load_courses()

    return render_template('course_register.html', courses=courses)

if __name__ == '__main__':
    from courseapp.admin import admin

    app.run(debug=True)