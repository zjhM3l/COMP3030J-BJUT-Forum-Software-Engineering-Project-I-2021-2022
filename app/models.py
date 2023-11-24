from datetime import datetime, timezone, timedelta
from markdown import markdown
import bleach
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db
import time


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    '''email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))'''

    def __repr__(self):
        return '<Role %r>' % self.name

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    moment = db.Column(db.String, index=True, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    name = db.Column(db.String(64))
    birthday = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    institute = db.Column(db.Text())
    member_since = db.Column(db.DateTime())
    last_seen = db.Column(db.DateTime())
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    real_avatar = db.Column(db.String(128), default=None)
    keyA = db.Column(db.String, default='')
    keyB = db.Column(db.String, default='')
    keyC = db.Column(db.String, default='')
    keyD = db.Column(db.String, default='')
    keyE = db.Column(db.String, default='')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    lafposts = db.relationship('LAFPost', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    statue = db.Column(db.Boolean, default = False)

    def __init__(self, **kwargs):
        self.follow(self)
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN_A']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.email == current_app.config['FLASKY_ADMIN_B']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.email == current_app.config['FLASKY_ADMIN_C']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.email == current_app.config['FLASKY_ADMIN_D']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.time()
        db.session.add(self)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser
registrations = db.Table('registrations',
                         db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                         db.Column('category_id', db.Integer, db.ForeignKey('categories.id')))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    moment = db.Column(db.String, index=True, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    read_count = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    categories = db.Column(db.String)
    keyA = db.Column(db.String, default='')
    keyB = db.Column(db.String, default='')
    keyC = db.Column(db.String, default='')
    keyD = db.Column(db.String, default='')
    keyE = db.Column(db.String, default='')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
                        'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


class LAFPost(db.Model):
    __tablename__ = 'lafposts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    details = db.Column(db.Text)
    photo = db.Column(db.String(128), default=None)
    lorf = db.Column(db.String)
    statue = db.Column(db.Boolean, default=False)
    location = db.Column(db.String)
    contact = db.Column(db.String)
    reward = db.Column(db.String, default='0')
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    moment = db.Column(db.String, index=True, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, default=11)
    read_count = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='lafpost', lazy='dynamic')
    categories = db.Column(db.String, default='Lost and Found')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
                        'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(32), unique=True, index=True,
                     nullable=False)
    heat = db.Column(db.Integer, default = 0)

    def __repr__(self):
        return '<Category %r>' % self.name

    @staticmethod
    def insert_categories():
        category1 = Category(id=1, name="Entertainment")
        category2 = Category(id=2, name="Science and Technology")
        category3 = Category(id=3, name="Movie")
        category4 = Category(id=4, name="Teleplay")
        category5 = Category(id=5, name="Games")
        category6 = Category(id=6, name="Sports")
        category7 = Category(id=7, name="Knowledge")
        category8 = Category(id=8, name="News")
        category9 = Category(id=9, name="Daily-Life")
        category10 = Category(id=10, name="Fashion")
        category11 = Category(id=11, name="Lost and Found")
        category12 = Category(id=12, name="Second Hand Transactions")
        category13 = Category(id=13, name="BJUT")
        category14 = Category(id=14, name="Others")
        db.session.add_all([category1, category2, category3, category4, category5, category6, category7,
                            category8, category9, category10, category11, category12, category13, category14])
        db.session.commit()


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    moment = db.Column(db.String, index=True, default=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    replies = db.relationship(
        'Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic'),
    lafpost_id = db.Column(db.Integer, db.ForeignKey('lafposts.id')
    )

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean
                                          (markdown(value, output_format='html'),
                                           tags=allowed_tags, strip=True))


class Announcement(db.Model):
    __tablename__ = 'Announcement'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    moment = db.Column(db.String, index=True, default=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    Read = db.Column(db.Integer, default = 0)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
                        'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)
db.event.listen(Announcement.body, 'set', Comment.on_changed_body)
db.event.listen(LAFPost.details, 'set', LAFPost.on_changed_body)
