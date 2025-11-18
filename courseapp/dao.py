from models import Course, Lesson, Class, Schedule

def get_courses():
    return Course.query.all()

def get_course_by_id(course_id):
    return Course.query.get(course_id)

def get_lessons(course_id):
    query = Lesson.query.filter(Lesson.active.__eq__(True))

    if course_id:
        query = query.filter(Lesson.course_id.__eq__(course_id))

    return query.all()

def get_classes(course_id):
    query = Class.query.filter(Class.active.__eq__(True))

    if course_id:
        query = query.filter(Class.course_id.__eq__(course_id))

    return query.all()

def get_schedules(class_id):
    query = Schedule.query.filter(Schedule.active.__eq__(True))

    if class_id:
        query = query.filter(Schedule.class_id.__eq__(class_id))

    return query.all()