from . import db
from .models import User, Role, Admin



def create_admin():
    # إنشاء دور الأدمن إذا لم يكن موجودًا
    admin_role = Role.query.filter_by(name='أدمن').first()
    if not admin_role:
        admin_role = Role(name='أدمن')
        db.session.add(admin_role)
        db.session.commit()

    # إنشاء مستخدم أدمن
    admin_user = User(
        name='Admin User',
        email='ahmedalbahrawy-2010@hotmail.com',
        role_id=admin_role.id
    )
    admin_user.set_password('adminpassword')
    db.session.add(admin_user)
    db.session.commit()

    # إضافة المستخدم إلى جدول الأدمن
    admin = Admin(user_id=admin_user.id)
    db.session.add(admin)
    db.session.commit()


def add_roles():
    # إضافة الأدوار الأساسية
    roles = ['طالب', 'مدرس', 'ولي أمر', 'أدمن']
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            new_role = Role(name=role_name)
            db.session.add(new_role)
    db.session.commit()
    
