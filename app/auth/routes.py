from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, login_required, logout_user, current_user
from .password import PasswordTool
from app.auth.email import send_email
from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from werkzeug.security import generate_password_hash


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        passw_hash = generate_password_hash(form.password.data)
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            current_user.statue = True
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    current_user.statue = False
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    password = str(form.password.data)
    check = PasswordTool(password)
    check.process_password()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data
                    )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        if send_email(user.email, 'BJUT Forum Confirmation', 'confirm', user=user, token=token):
            flash('The email address is not existed or the network is not connected')
        else:
            flash('You can now check your email')
        # flash('Register successfully')   #判断邮件是否成功发送
        return redirect(url_for('auth.login'))
        # return redirect(url_for('main.index'))
    return render_template('register.html', form=form, level=check.strength_level)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
    else:
        flash('这个确认链接不可用，或已超时')
    current_user.statue = True
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    flash('Invalid email, please try it again')
    return render_template('unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认你的账户',
               'auth/email/confirm', current_user, token)
    flash('新确认账户邮件已发送到邮箱，注意查收.')
    return redirect(url_for('main.index'))
