import json
from sqlalchemy import Integer, ForeignKey, DateTime, String, Column, Enum, Float, Boolean, Time, Date
from sqlalchemy.orm import relationship
from courseapp import app, db
from datetime import datetime
from enum import Enum as Type
from flask_login import UserMixin

class EnrollStatus(Type):
    REGISTERED = 1
    CANCELLED = 2

class PaymentStatus(Type):
    PENDING = 1
    PAID = 2

class Result(Type):
    SUCCESS = 1
    FAILURE = 2

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)

class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    def __init__(self, username, password, staff=None, student=None, teacher=None):
        self.username = username
        self.password = password
        self.staff = staff
        self.student = student
        self.teacher = teacher

    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)

    staff = relationship("Staff", backref="user", lazy=True, uselist=False)
    student = relationship("Student", backref="user", lazy=True, uselist=False)
    teacher = relationship("Teacher", backref="user", lazy=True, uselist=False)

    @property
    def role(self):
        if self.staff:
            return self.staff
        elif self.student:
            return self.student
        elif self.teacher:
            return self.teacher
        return None

class Staff(db.Model):
    __tablename__ = 'staff'

    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    avatar = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)

    invoices = relationship("Invoice", backref="staff", lazy=True)


    def __str__(self):
        return self.name

class Student(db.Model):
    __tablename__ = 'student'

    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    avatar = Column(String(255), nullable=True)

    enrollments = relationship('Enrollment', backref='student', lazy=True)

    def __str__(self):
        return self.name


class Teacher(db.Model):
    __tablename__ = 'teacher'

    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    avatar = Column(String(255), nullable=False)
    specialization = Column(String(50), nullable=True)

    classrooms = relationship('Classroom', backref='teacher', lazy=True)

    def __str__(self):
        return self.name

class Classroom(BaseModel):
    __tablename__ = 'classroom'

    name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=True)

    sections = relationship('Section', backref='classroom', lazy=True)

    def __str__(self):
        return self.name


class Enrollment(BaseModel):
    __tablename__ = 'enrollment'

    enroll_date = Column(DateTime, default=datetime.now())
    status = Column(Enum(EnrollStatus), nullable=False, default=EnrollStatus.REGISTERED)
    unit_price = Column(Float, nullable=False)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)

    invoice = relationship('Invoice', backref='enrollment', lazy=True, uselist=False)
    scores = relationship('Score', backref='enrollment', lazy=True)

class Score(BaseModel):
    __tablename__ = 'score'

    score = Column(Float, nullable=False)
    type = Column(String(50), nullable=False)
    result = Column(Enum(Result), nullable=False)
    enrollment_id = Column(Integer, ForeignKey(Enrollment.id), nullable=True)

class Invoice(BaseModel):
    __tablename__ = 'invoice'

    id = Column(Integer, ForeignKey(Enrollment.id), primary_key=True, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    staff_id = Column(Integer, ForeignKey(Staff.id), nullable=True)

class Section(BaseModel):
    __tablename__ = 'section'

    schedule = Column(String(50), nullable=False)
    classroom_id = Column(Integer, ForeignKey('classroom.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    current_size = Column(Integer, default=0)

    enrollments = relationship('Enrollment', backref='section', lazy=True)

class Lesson(BaseModel):
    __tablename__ = 'lesson'

    title = Column(String(50), nullable=False)
    content = Column(String(255), nullable=True)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)

    def __str__(self):
        return self.title

class Course(BaseModel):
    __tablename__ = 'course'

    name = Column(String(50), nullable=False)
    image = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)

    lessons = relationship('Lesson', backref='course', lazy=True)
    sections = relationship('Section', backref='course', lazy=True)

    def __str__(self):
        return self.name


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

        import hashlib

        s1 = Staff(name='Staff1', email='staff1@gmail.com',
                  avatar='https://res.cloudinary.com/dl0b32hii/image/upload/v1763480359/ksw7wx53ma3edyfrqh8q.jpg', is_admin=True)

        s2 = Staff(name='Staff2', email='staff1@gmail.com',
                  avatar='https://res.cloudinary.com/dl0b32hii/image/upload/v1763480359/ksw7wx53ma3edyfrqh8q.jpg')

        student1 = Student(name='student1', email='truong.4725212@gmail.com',
                  avatar='https://res.cloudinary.com/dl0b32hii/image/upload/v1763480359/ksw7wx53ma3edyfrqh8q.jpg')
        student2 = Student(name='student2', email='truong.4725212@gmail.com',
                           avatar='https://res.cloudinary.com/dl0b32hii/image/upload/v1763480359/ksw7wx53ma3edyfrqh8q.jpg')
        student3 = Student(name='student3', email='truong.4725212@gmail.com',
                           avatar='https://res.cloudinary.com/dl0b32hii/image/upload/v1763480359/ksw7wx53ma3edyfrqh8q.jpg')

        u1 = User(username='admin', password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()), staff=s1)
        u2 = User(username='staff1', password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()), staff=s2)
        u3 = User(username='student1', password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()), student=student1)
        u4 = User(username='student2', password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()), student=student2)
        u5 = User(username='student3', password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()), student=student3)

        db.session.add_all([u1, u2, u3, u4, u5])

        db.session.add_all([s1,s2])
        db.session.add_all([student1,student2,student3])

        db.session.commit()


        # Course
        with open('data/courses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for course in data:
                c = Course(**course)
                db.session.add(c)
            db.session.commit()

        # Lesson
        with open('data/lessons.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for course in data:
                l = Lesson(**course)
                db.session.add(l)
            db.session.commit()

        # Classroom
        with open('data/classrooms.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for cls in data:
                c = Classroom(**cls)
                db.session.add(c)
            db.session.commit()

        # section
        with open('data/sections.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for se in data:
                s = Section(**se)
                db.session.add(s)
            db.session.commit()

        # Enrollment
        with open('data/enrollments.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for en in data:
                c = Enrollment(**en)
                db.session.add(c)
            db.session.commit()

        # Invoice
        with open('data/invoices.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for inv in data:
                c = Invoice(**inv)
                db.session.add(c)
            db.session.commit()

        # #User
        # with open('data/users.json', 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        #     for us in data:
        #         u = User(**us)
        #         db.session.add(u)
        #     db.session.commit()
        #
        # # Admin
        # with open('data/staff.json', 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        #     for ad in data:
        #         a = Staff(**ad)
        #         db.session.add(a)
        #     db.session.commit()
        #
        # #Student
        # with open('data/students.json', 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        #     for st in data:
        #         s = Student(**st)
        #         db.session.add(s)
        #     db.session.commit()
        #
        # # Teacher
        # with open('data/teachers.json', 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        #     for te in data:
        #         t = Teacher(**te)
        #         db.session.add(t)
        #     db.session.commit()
