from flask_wtf import FlaskForm
from ..models import Role
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, Optional
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Email(message='بريد إلكتروني غير صالح')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='هذا الحقل مطلوب')
    ])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    fullname = StringField('الاسم الكامل', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Length(min=3, max=50, message='يجب أن يكون الاسم بين 3 و 50 حرفاً')
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Email(message='بريد إلكتروني غير صالح')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Length(min=6, message='يجب أن تكون كلمة المرور 6 أحرف على الأقل')
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])
    submit = SubmitField('إنشاء حساب')
    
    


class ProfileForm(FlaskForm):
    profile_image = FileField('صورة الملف الشخصي', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'يجب أن تكون الصورة بصيغة jpg أو png أو jpeg')
    ])
    submit = SubmitField('حفظ التغييرات')
    
    
class EditUserForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired()])
    role_id = QuerySelectField('الدور', query_factory=lambda: Role.query.all(), get_label='name', allow_blank=True, validators=[DataRequired()], get_pk=lambda x: x.id)
    submit = SubmitField('حفظ التغييرات')

class AddClassForm(FlaskForm):
    name = StringField('اسم الفصل', validators=[DataRequired()])
    teacher_id = SelectField('المدرس', coerce=int, validators=[DataRequired()])
    submit = SubmitField('إضافة الفصل')
    
class EditParentForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    submit = SubmitField('حفظ التغييرات')

class EditTeacherForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    subject = StringField('المادة', validators=[DataRequired()])
    submit = SubmitField('حفظ التغييرات')
    
    
class AddSubjectForm(FlaskForm):
    name = StringField('اسم المادة', validators=[DataRequired()])
    teacher_id = SelectField('المدرس', coerce=int, validators=[DataRequired()])
    class_id = SelectField('الفصل الدراسي', coerce=int, validators=[DataRequired()])
    submit = SubmitField('إضافة المادة')

class EditSubjectForm(FlaskForm):
    name = StringField('اسم المادة', validators=[DataRequired()])
    teacher_id = SelectField('المدرس', coerce=int, validators=[DataRequired()])
    class_id = SelectField('الفصل الدراسي', coerce=int, validators=[DataRequired()])
    submit = SubmitField('حفظ التغييرات')
    
