from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm, ProfileForm, EditUserForm, AddClassForm, EditParentForm, EditTeacherForm, AddSubjectForm, EditSubjectForm
from ..models import User, Role, Student, Teacher, Parent, Class, Subject, Admin
from .. import db
from werkzeug.utils import secure_filename
import os

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.home'))
        flash('البريد الإلكتروني أو كلمة المرور غير صحيحة')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # البحث عن دور الطالب
        student_role = Role.query.filter_by(name='طالب').first()
        if not student_role:
            flash('دور الطالب غير موجود في النظام', 'error')
            return redirect(url_for('auth.register'))
        
        # إنشاء المستخدم مع تعيين الدور كطالب
        user = User(
            name=form.fullname.data,
            email=form.email.data,
            role_id=student_role.id  # تعيين الدور كطالب
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # إنشاء طالب جديد
        student = Student(user_id=user.id)
        db.session.add(student)
        db.session.commit()
        
        flash('تم إنشاء حسابك بنجاح!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)



@auth.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    # Fetch all users, parents, and teachers
    users = User.query.all()
    parents = Parent.query.all()
    teachers = Teacher.query.all()
    
    return render_template('admin_dashboard.html', users=users, parents=parents, teachers=teachers)

@auth.route('/admin/convert_to_parent/<int:student_id>', methods=['POST'])
@login_required
def convert_to_parent(student_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    student = Student.query.get_or_404(student_id)
    user = student.user

    # إنشاء ولي أمر جديد
    parent = Parent(user_id=user.id)
    db.session.add(parent)
    
    # حذف الطالب
    db.session.delete(student)
    
    db.session.commit()
    
    flash('تم تحويل الطالب إلى ولي أمر بنجاح', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/convert_to_teacher/<int:student_id>', methods=['POST'])
@login_required
def convert_to_teacher(student_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    student = Student.query.get_or_404(student_id)
    user = student.user

    # إنشاء مدرس جديد
    teacher = Teacher(user_id=user.id, subject='مادة جديدة')  # يمكنك تعديل المادة
    db.session.add(teacher)
    
    # حذف الطالب
    db.session.delete(student)
    
    db.session.commit()
    
    flash('تم تحويل الطالب إلى مدرس بنجاح', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():
        # Remove user from old role class
        if user.role.name == 'طالب':
            student = Student.query.filter_by(user_id=user.id).first()
            if student:
                db.session.delete(student)
        elif user.role.name == 'مدرس':
            teacher = Teacher.query.filter_by(user_id=user.id).first()
            if teacher:
                db.session.delete(teacher)
        elif user.role.name == 'ولي أمر':
            parent = Parent.query.filter_by(user_id=user.id).first()
            if parent:
                db.session.delete(parent)
        elif user.role.name == 'أدمن':
            admin = Admin.query.filter_by(user_id=user.id).first()
            if admin:
                db.session.delete(admin)

        # Update user details
        user.name = form.name.data
        user.email = form.email.data
        user.role_id = form.role_id.data.id  # Ensure role_id is set to the integer ID
        db.session.commit()

        # Add user to new role class
        new_role = Role.query.get(user.role_id)
        if new_role.name == 'طالب':
            student = Student(user_id=user.id, grade='')  # Add default grade or modify as needed
            db.session.add(student)
        elif new_role.name == 'مدرس':
            teacher = Teacher(user_id=user.id, subject='مادة جديدة')  # يمكنك تعديل المادة
            db.session.add(teacher)
        elif new_role.name == 'ولي أمر':
            parent = Parent(user_id=user.id)
            db.session.add(parent)
        elif new_role.name == 'أدمن':
            admin = Admin(user_id=user.id)
            db.session.add(admin)

        db.session.commit()
        flash('تم تحديث بيانات المستخدم بنجاح', 'success')
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template('edit_user.html', form=form, user=user)

@auth.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/edit_parent/<int:parent_id>', methods=['GET', 'POST'])
@login_required
def edit_parent(parent_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    parent = Parent.query.get_or_404(parent_id)
    form = EditParentForm(obj=parent)
    parent.name = form.name.data
    parent.email = form.email.data
    
    if form.validate_on_submit():
        parent.user.name = form.name.data
        parent.user.email = form.email.data
        db.session.commit()
        flash('تم تحديث بيانات ولي الأمر بنجاح', 'success')
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template('edit_parent.html', form=form, parent=parent)

@auth.route('/admin/delete_parent/<int:parent_id>', methods=['POST'])
@login_required
def delete_parent(parent_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    parent = Parent.query.get_or_404(parent_id)
    db.session.delete(parent)
    db.session.commit()
    flash('تم حذف ولي الأمر بنجاح', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    teacher = Teacher.query.get_or_404(teacher_id)
    form = EditTeacherForm(obj=teacher)
    
    teacher.user_id.name = form.name.data
    teacher.email = form.email.data
    
    if form.validate_on_submit():
        teacher.user.name = form.name.data
        teacher.user.email = form.email.data
        teacher.subject = form.subject.data
        db.session.commit()
        flash('تم تحديث بيانات المدرس بنجاح', 'success')
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template('edit_teacher.html', form=form, teacher=teacher)

@auth.route('/admin/delete_teacher/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('تم حذف المدرس بنجاح', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/add_class', methods=['GET', 'POST'])
@login_required
def add_class():
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    form = AddClassForm()
    
    if form.validate_on_submit():
        new_class = Class(
            name=form.name.data,
            teacher_id=form.teacher_id.data
        )
        db.session.add(new_class)
        db.session.commit()
        flash('تم إضافة الفصل الدراسي بنجاح', 'success')
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template('add_class.html', form=form)

@auth.route('/admin/delete_class/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    class_to_delete = Class.query.get_or_404(class_id)
    db.session.delete(class_to_delete)
    db.session.commit()
    flash('تم حذف الفصل الدراسي بنجاح', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    form = AddSubjectForm()
    
    if form.validate_on_submit():
        new_subject = Subject(
            name=form.name.data,
            teacher_id=form.teacher_id.data,
            class_id=form.class_id.data
        )
        db.session.add(new_subject)
        db.session.commit()
        flash('تم إضافة المادة الدراسية بنجاح', 'success')
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template('add_subject.html', form=form)

@auth.route('/admin/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    subject = Subject.query.get_or_404(subject_id)
    form = EditSubjectForm(obj=subject)
    
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.teacher_id = form.teacher_id.data
        subject.class_id = form.class_id.data
        db.session.commit()
        flash('تم تحديث المادة الدراسية بنجاح', 'success')
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template('edit_subject.html', form=form, subject=subject)

@auth.route('/admin/delete_subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        flash('غير مصرح لك بتنفيذ هذه العملية', 'error')
        return redirect(url_for('main.home'))
    
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('تم حذف المادة الدراسية بنجاح', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            # حفظ الصورة
            filename = secure_filename(form.profile_image.data.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.profile_image.data.save(filepath)
            current_user.profile_image = filename
            db.session.commit()
            flash('تم تحديث الصورة بنجاح', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('profile.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))