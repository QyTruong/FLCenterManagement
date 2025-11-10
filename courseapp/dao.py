from models import Level, Course

def load_levels():
    return Level.query.all()

def load_courses():
    return Course.query.all()