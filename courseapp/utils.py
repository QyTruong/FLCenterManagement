from flask_login import current_user
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from courseapp import app


def send_email_enrollment(course_name, classroom_name, schedule, unit_price, student):
    if current_user.is_authenticated:
        formatted_price = f"{float(unit_price):,.0f} VNĐ"

        message = Mail(from_email=app.config['SENDGRID_FROM_EMAIL'],
                       to_emails=student.email,
                       subject='Thư xác nhận đăng ký khóa học thành công tại English Center !!!',
                       plain_text_content=f'Xin chào {student.name},\n'
                                          f'Chúc mừng bạn đã đăng ký thành công khóa học {course_name}\n'
                                          f'Tên lớp: {classroom_name}\n' f'Phiên học: {schedule}\n'
                                          f'Giá tiền: {formatted_price}\n'
                                          f'Vui lòng đến trung tâm đóng học trước ngày 1/1/2026\n'
                                          f'Địa chỉ trung tâm: 12/233D/9/23/45D đường ABC, phường XYZ\n'
                                          f'Xin cảm ơn.')

        sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
        sg.send(message)
