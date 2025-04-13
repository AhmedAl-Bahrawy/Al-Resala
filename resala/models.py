from . import db, bcrypt
from flask_login import UserMixin
from . import login_manager
from datetime import datetime

from datetime import datetime
from . import db, bcrypt
from flask_login import UserMixin

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # مثل: طالب، مدرس، ولي أمر، أدمن
    users = db.relationship('User', back_populates='role', lazy=True)  # استخدام back_populates

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(200))  # رابط صورة المستخدم
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # علاقة مع الأدوار
    role = db.relationship('Role', back_populates='users')  # استخدام back_populates

    # علاقة مع الجداول الأخرى
    student = db.relationship('Student', backref='user', uselist=False, lazy=True)
    teacher = db.relationship('Teacher', backref='user', uselist=False, lazy=True)
    parent = db.relationship('Parent', backref='user', uselist=False, lazy=True)
    admin = db.relationship('Admin', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role.name == 'أدمن'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    grade = db.Column(db.String(50))  # الصف الدراسي
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))  # ولي الأمر

class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    students = db.relationship('Student', backref='parent', lazy=True)  # الطلاب الذين يرعاهم ولي الأمر

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # اسم المادة
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))  # المدرس المسؤول
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))  # الفصل الدراسي

    # علاقة مع المدرس
    teacher = db.relationship('Teacher', backref='subjects')

    # علاقة مع الفصل الدراسي
    class_ = db.relationship('Class', backref='subjects')

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    subject = db.Column(db.String(100), nullable=False)  # المادة التي يدرسها
    classes = db.relationship('Class', backref='teacher', lazy=True)  # الفصول التي يدرسها المدر

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # اسم الفصل
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))  # المدرس المسؤول
    students = db.relationship('Student', secondary='class_student', backref='classes')

# جدول وسيط للعلاقة بين الطلاب والفصول
class_student = db.Table('class_student',
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True)
)

# دالة لتحميل المستخدم
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))