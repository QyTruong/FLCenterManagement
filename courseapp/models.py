import json
from sqlalchemy import Integer, ForeignKey, DateTime, String, Column, Enum, Float, Boolean, Time, Date
from sqlalchemy.orm import relationship
from courseapp import app, db
from datetime import datetime
from enum import Enum as Type

class UserRole(Type):
    ADMIN = 1
    STUDENT = 2
    TEACHER = 3

class Status(Type):
    REGISTERED = 1
    PAID = 2

class Result(Type):
    SUCCESS = 1
    FAILURE = 2

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)

class User(BaseModel):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    avatar = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.STUDENT)

    student = relationship("Student", backref="user", lazy=True, uselist=False)
    teacher = relationship("Teacher", backref="user", lazy=True, uselist=False)

    def __str__(self):
        return self.name

class Course(BaseModel):
    __tablename__ = 'course'

    name = Column(String(50), nullable=False)
    image = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)

    lessons = relationship('Lesson', backref='course', lazy=True)

    def __str__(self):
        return self.name

class Lesson(BaseModel):
    __tablename__ = 'lesson'

    title = Column(String(50), nullable=False)
    content = Column(String(255), nullable=True)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)

    def __str__(self):
        return self.title

class Student(db.Model):
    __tablename__ = 'student'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True, unique=True, nullable=False)
    registers = relationship('Register', backref='student', lazy=True)

class Teacher(db.Model):
    __tablename__ = 'teacher'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True, unique=True, nullable=False)
    specialization = Column(String(50), nullable=False)

    classes = relationship('Class', backref='teacher', lazy=True)


class Class(BaseModel):
    __tablename__ = 'class'

    name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    max_student = Column(Integer, default=50, nullable=False)
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=True)
    course_id = Column(Integer, ForeignKey(Course.id), nullable=True)

    registers = relationship('Register', backref='class', lazy=True)
    schedules = relationship('Schedule', backref='class', lazy=True)

    def __str__(self):
        return self.name

class Schedule(BaseModel):
    __tablename__ = 'schedule'

    day_of_week = Column(String(15), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)

    def __str__(self):
        return f"{self.day_of_week}   {self.start_time} - {self.end_time}"


class Register(BaseModel):
    __tablename__ = 'register'

    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    register_date = Column(DateTime, default=datetime.now())
    status = Column(Enum(Status), nullable=False)

    scores = relationship('Score', backref='register', lazy=True)
    invoice = relationship("Invoice", backref="register", lazy=True, uselist=False)

class Invoice(BaseModel):
    __tablename__ = 'invoice'

    id = Column(Integer, ForeignKey('register.id'), primary_key=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.now())


class Score(BaseModel):
    __tablename__ = 'score'

    score = Column(Float, nullable=False)
    type = Column(String(50), nullable=False)
    result = Column(Enum(Result), nullable=False)
    register_id = Column(Integer, ForeignKey(Register.id), unique=True)

if __name__ == '__main__':
    with app.app_context():
        #db.drop_all()
        #db.create_all()

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

        # Class
        with open('data/classes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for cls in data:
                c = Class(**cls)
                db.session.add(c)
            db.session.commit()

        # Schedule
        with open('data/schedules.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for sc in data:
                s = Schedule(**sc)
                db.session.add(s)
            db.session.commit()

