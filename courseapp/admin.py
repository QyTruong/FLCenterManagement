from flask_admin import Admin, BaseView, expose, AdminIndexView
from courseapp import app, db,dao
from flask_admin.contrib.sqla import ModelView

from models import Classroom, Course, Section
from flask_login import  current_user, logout_user
from flask import redirect, request
from datetime import  datetime

class View(ModelView):
    column_sortable_list = ['id']
    edit_modal = True
    can_export = True
    can_view_details = True
    page_size = 5

class AdminView(View):
    def is_accessible(self) -> bool:
        return  current_user.is_authenticated

class CourseView(AdminView):
    column_list = ['id', 'name', 'price', 'active']
    column_filters = ['id', 'price']

class ClassroomView(AdminView):
    column_list = ['id', 'name','capacity', 'active']
    column_searchable_list = ['name']
    column_filters = ['id', 'name']

class SectionView(AdminView):
    column_list = ['id', 'schedule', 'active', 'course_id', 'classroom_id']
    column_filters = ['id', 'schedule']
    column_searchable_list = ['course_id']

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login-account')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated


class RevenueStatsView(BaseView):
    @expose('/')
    def index(self):

        year = request.args.get('year', datetime.now().year)

        return  self.render('admin/revenue_stats.html', revenue_stats=dao.revenue_by_month_stats(year=year))

    def is_accessible(self) -> bool:
        return  current_user.is_authenticated and current_user.staff

class StudentStatsView(BaseView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        return  self.render('admin/student_stats.html',
                            stats=dao.number_of_student_stats(kw=kw, from_date=from_date, to_date=to_date))

    def is_accessible(self) -> bool:
        return  current_user.is_authenticated and current_user.staff


class PassRateStatsView(BaseView):
    @expose('/')
    def index(self):
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        return self.render('admin/rate_stats.html', pass_rate_stats=dao.pass_rate_stats(from_date=from_date, to_date=to_date))

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.staff



class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=dao.course_stats())


# admin = Admin(app=app, index_view=MyAdminIndex())
admin = Admin(app=app, name='Administration', index_view=MyAdminIndex())

admin.add_view(CourseView(Course, db.session))
admin.add_view(ClassroomView(Classroom, db.session))
admin.add_view(SectionView(Section, db.session))
admin.add_view(RevenueStatsView(name='Thống kê doanh thu', endpoint='revenue_stats'))
admin.add_view(StudentStatsView(name='Thống kê học viên', endpoint='student_stats'))
admin.add_view(PassRateStatsView(name='Tỷ lệ đạt', endpoint='rate_stats'))
admin.add_view(LogoutView(name='Đăng xuất', endpoint='logout'))