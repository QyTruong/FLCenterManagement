from models import Course, Lesson

def load_courses():
    return Course.query.all()

def load_course_by_id(course_id):
    return Course.query.filter(Course.id == course_id).first()

def load_lessons(course_id):
    query = Lesson.query.filter(Lesson.active.__eq__(True))

    if course_id:
        query = query.filter(Lesson.course_id.__eq__(course_id))

    return query.all()