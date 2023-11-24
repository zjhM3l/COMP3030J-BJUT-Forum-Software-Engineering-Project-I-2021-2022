from datetime import datetime
from collections import Counter
from flask import render_template, flash, redirect, url_for, session, abort, request, current_app, make_response
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, PostForm, AnnouncementForm, \
    CommentForm, SearchForm, ChangeAvatarForm, ReplyForm, LostAndFoundForm, LikePostForm
from .. import db
from ..decorators import permission_required
from ..models import User, Permission, Post, Comment, Announcement, Category, LAFPost
from .echarts import *
from .keyextract import testKey
from wtforms import ValidationError


@main.route('/lost&found', methods=['GET', 'POST'])
def lindex():
    lform = LostAndFoundForm()
    content = ''
    if lform.validate_on_submit() and \
            current_user.can(Permission.WRITE):
        t = lform.title.data
        photo = request.files['photo']
        fname = photo.filename
        upload_folder = current_app.config['LAF_UPLOAD_FOLDER']
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif']
        fext = fname.rsplit('.', 1)[-1] if '.' in fname else ''
        if fext not in allowed_extensions:
            flash('Please check if its one of png, '
                  'jpg, jpeg and gif')
            return redirect(url_for('.lindex'))
        target = '{}{}.{}'.format(upload_folder, t, fext)
        photo.save(target)
        lpost = LAFPost(title=lform.title.data,
                        details=lform.details.data,
                        author=current_user._get_current_object(),
                        photo='/static/lostAndFoundPhoto/{}.{}'.format(t, fext),
                        contact=lform.contact.data,
                        location=lform.location.data,
                        reward=lform.reward.data,
                        lorf=lform.lorf.data,
                        moment=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        category = Category.query.get(11)
        category.heat += 1
        db.session.add(lpost)
        flash('Your post has been pushed.')
        return redirect(url_for('.lindex'))
    sform = SearchForm()
    if sform.validate_on_submit():
        content = sform.text.data
    page = request.args.get('page', 1, type=int)
    query = LAFPost.query
    pagination = query.filter(
        LAFPost.title.like('%' + content + '%')).order_by(
        LAFPost.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('lindex.html', lform=lform, sform=sform, lposts=posts,
                           pagination=pagination, show_followed=show_followed,
                           )


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    content = ''
    result = testKey()
    keyList = result['key']
    cloudKey = []
    for i in range(len(Post.query.all())):
        k = keyList[i].split()
        for i in k:
            cloudKey.append(i)
        word_counts = Counter(cloudKey)
        cK = word_counts.most_common(10)
        cloudKeys = []
        for i in cK:
            cloudKeys.append(i[0])
    if form.validate_on_submit() and \
            current_user.can(Permission.WRITE):
        category_id = form.category_id.data
        categories = Category.query.get(category_id)
        if not categories:
            flash('There is no such category, please check the number.')
        post = Post(title=form.title.data,
                    body=form.body.data,
                    category_id=form.category_id.data,
                    author=current_user._get_current_object(),
                    moment=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        post.categories = categories.name
        category = Category.query.get(post.category_id)
        category.heat += 1
        db.session.add(post)
        return redirect(url_for('.index'))
    sform = SearchForm()
    liform = LikePostForm()
    if sform.validate_on_submit():
        content = sform.text.data
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts.filter(Post.author_id != current_user.id)
        show_followed = True
    else:
        query = Post.query
        show_followed = False
    categories = Category.query.all()
    category_id = request.args.get('category_id', type=int, default=None)

    pagination = query.filter(
        Post.title.like('%' + content + '%') +
        Post.categories.like('%' + content + '%') +
        Post.keyA.like('%' + content + '%') +
        Post.keyB.like('%' + content + '%') +
        Post.keyC.like('%' + content + '%') +
        Post.keyD.like('%' + content + '%') +
        Post.keyE.like('%' + content + '%')).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    if liform.validate_on_submit():
        userKey = []
        keyPosts = current_user.posts.order_by(Post.timestamp.desc())
        for i in keyPosts:
            userKey.append(i.keyA)
            userKey.append(i.keyB)
            userKey.append(i.keyC)
            userKey.append(i.keyD)
            userKey.append(i.keyE)
        word_counts = Counter(userKey)
        uK = word_counts.most_common(5)
        userKeys = []
        for i in uK:
            userKeys.append(i[0])
        followKey = [];
        paginatio = current_user.followers.paginate(
            page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
            error_out=False)
        follows = [item.follower
                   for item in paginatio.items]
        print(follows, 'type is', type(follows))
        print(follows[0], 'type is', type(follows[0]))
        for i in follows:
            print(i, 'type is', type(i))
            followKey.append(i.keyA)
            followKey.append(i.keyB)
            followKey.append(i.keyC)
            followKey.append(i.keyD)
            followKey.append(i.keyE)
        word_counts = Counter(followKey)
        fK = word_counts.most_common(5)
        followKeys = []
        for i in fK:
            followKeys.append(i[0])
        pagination = query.filter(
            Post.title.like('%' + userKeys[0] + '%') +
            Post.categories.like('%' + userKeys[0] + '%') +
            Post.keyA.like('%' + userKeys[0] + '%') +
            Post.keyB.like('%' + userKeys[0] + '%') +
            Post.keyC.like('%' + userKeys[0] + '%') +
            Post.keyD.like('%' + userKeys[0] + '%') +
            Post.keyE.like('%' + userKeys[0] + '%') +
            Post.title.like('%' + userKeys[0] + '%') +
            Post.categories.like('%' + userKeys[1] + '%') +
            Post.keyA.like('%' + userKeys[1] + '%') +
            Post.keyB.like('%' + userKeys[1] + '%') +
            Post.keyC.like('%' + userKeys[1] + '%') +
            Post.keyD.like('%' + userKeys[1] + '%') +
            Post.keyE.like('%' + userKeys[1] + '%') +
            Post.title.like('%' + userKeys[1] + '%') +
            Post.categories.like('%' + userKeys[2] + '%') +
            Post.keyA.like('%' + userKeys[2] + '%') +
            Post.keyB.like('%' + userKeys[2] + '%') +
            Post.keyC.like('%' + userKeys[2] + '%') +
            Post.keyD.like('%' + userKeys[2] + '%') +
            Post.keyE.like('%' + userKeys[2] + '%') +
            Post.title.like('%' + userKeys[2] + '%') +
            Post.categories.like('%' + userKeys[3] + '%') +
            Post.keyA.like('%' + userKeys[3] + '%') +
            Post.keyB.like('%' + userKeys[3] + '%') +
            Post.keyC.like('%' + userKeys[3] + '%') +
            Post.keyD.like('%' + userKeys[3] + '%') +
            Post.keyE.like('%' + userKeys[3] + '%') +
            Post.title.like('%' + userKeys[3] + '%') +
            Post.categories.like('%' + userKeys[4] + '%') +
            Post.keyA.like('%' + userKeys[4] + '%') +
            Post.keyB.like('%' + userKeys[4] + '%') +
            Post.keyC.like('%' + userKeys[4] + '%') +
            Post.keyD.like('%' + userKeys[4] + '%') +
            Post.keyE.like('%' + userKeys[4] + '%') +
            Post.title.like('%' + userKeys[0] + '%') +
            Post.categories.like('%' + userKeys[0] + '%') +
            Post.keyA.like('%' + followKeys[0] + '%') +
            Post.keyB.like('%' + followKeys[0] + '%') +
            Post.keyC.like('%' + followKeys[0] + '%') +
            Post.keyD.like('%' + followKeys[0] + '%') +
            Post.keyE.like('%' + followKeys[0] + '%') +
            Post.title.like('%' + followKeys[0] + '%') +
            Post.categories.like('%' + followKeys[1] + '%') +
            Post.keyA.like('%' + followKeys[1] + '%') +
            Post.keyB.like('%' + followKeys[1] + '%') +
            Post.keyC.like('%' + followKeys[1] + '%') +
            Post.keyD.like('%' + followKeys[1] + '%') +
            Post.keyE.like('%' + followKeys[1] + '%') +
            Post.title.like('%' + followKeys[1] + '%') +
            Post.categories.like('%' + followKeys[2] + '%') +
            Post.keyA.like('%' + followKeys[2] + '%') +
            Post.keyB.like('%' + followKeys[2] + '%') +
            Post.keyC.like('%' + followKeys[2] + '%') +
            Post.keyD.like('%' + followKeys[2] + '%') +
            Post.keyE.like('%' + followKeys[2] + '%') +
            Post.title.like('%' + followKeys[2] + '%') +
            Post.categories.like('%' + followKeys[3] + '%') +
            Post.keyA.like('%' + followKeys[3] + '%') +
            Post.keyB.like('%' + followKeys[3] + '%') +
            Post.keyC.like('%' + followKeys[3] + '%') +
            Post.keyD.like('%' + followKeys[3] + '%') +
            Post.keyE.like('%' + followKeys[3] + '%') +
            Post.title.like('%' + followKeys[3] + '%') +
            Post.categories.like('%' + followKeys[4] + '%') +
            Post.keyA.like('%' + followKeys[4] + '%') +
            Post.keyB.like('%' + followKeys[4] + '%') +
            Post.keyC.like('%' + followKeys[4] + '%') +
            Post.keyD.like('%' + followKeys[4] + '%') +
            Post.keyE.like('%' + followKeys[4] + '%')).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
            error_out=False)
    if category_id:
        pagination = query.filter(Post.category_id == category_id).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, sform=sform, posts=posts, categories=categories, liform=liform,
                           catgory_id=category_id,
                           pagination=pagination, show_followed=show_followed,
                           Cloud_options=getWordCloud(), KeyWordCloud_options=getKeyWordCloud(), Ball_options=getLiquidBall(),
                           cloudKeys=cloudKeys
                           )


@main.route('/announcement', methods=['GET', 'POST'])
@login_required
def announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        ann = Announcement(title=form.title.data,
                           body=form.body.data,
                           moment=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                           # author=current_user._get_current_object()
                           )
        db.session.add(ann)
        return redirect(url_for('.announcement'))
    page = request.args.get('page', 1, type=int)
    pagination = Announcement.query.order_by(Announcement.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_ANNOUNCEMENT_PER_PAGE'],
        error_out=False)
    announcements = pagination.items
    return render_template('announcement.html', form=form, announcements=announcements,
                           pagination=pagination,
                           Map_options=getMap())


@main.route('/administrator', methods=['Get','Post'])
@login_required
def administrator():
    username = current_user.username
    return render_template('administrator.html', Bar3D_options = getBar3D(),username=username, user=current_user)


@main.route('/administrator2', methods=['Get', 'Post'])
@login_required
def administrator2():
    username = current_user.username
    return render_template('administrator2.html', Map_options = getMap(), username=username, user=current_user)

@main.route('/administrator3', methods=['Get', 'Post'])
@login_required
def administrator3():
    username = current_user.username
    return render_template('administrator3.html', Bar_options = getBar(), username = username, user = current_user)

@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    userKey = []
    keyPosts = user.posts.order_by(Post.timestamp.desc())
    for i in keyPosts:
        userKey.append(i.keyA)
        userKey.append(i.keyB)
        userKey.append(i.keyC)
        userKey.append(i.keyD)
        userKey.append(i.keyE)
    word_counts = Counter(userKey)
    uK = word_counts.most_common(5)
    userKeys = []
    for i in uK:
        userKeys.append(i[0])
    user.keyA = userKeys[0]
    user.keyB = userKeys[1]
    user.keyC = userKeys[2]
    user.keyD = userKeys[3]
    user.keyE = userKeys[4]
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination, userKeys=userKeys)


@main.route('/ucomments/<username>', methods=['GET', 'POST'])
def ucomments(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('ucomments.html', user=user, comments=comments,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    aform = ChangeAvatarForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.birthday = form.birthday.data
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        current_user.institute = form.institute.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated')
        return redirect(url_for('main.edit_profile', username=current_user.username))
    if aform.validate_on_submit():
        avatar = request.files['avatar']
        fname = avatar.filename
        upload_folder = current_app.config['UPLOAD_FOLDER']
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif']
        fext = fname.rsplit('.', 1)[-1] if '.' in fname else ''
        if fext not in allowed_extensions:
            flash('Please check if its one of png, '
                  'jpg, jpeg and gif')
            return redirect(url_for('main.edit_profile',
                                    username=current_user.username))
        target = '{}{}.{}'.format(upload_folder, current_user.username, fext)
        avatar.save(target)
        current_user.real_avatar = '/static/avatars/{}.{}'.format(current_user.username, fext)
        db.session.add(current_user)
        flash('Your avatar has been updated.')
        return redirect(url_for('main.edit_profile', username=current_user.username))
    form.username.data = current_user.username
    form.birthday.data = current_user.birthday
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    form.institute.data = current_user.institute
    username = current_user.username
    return render_template('userinfo.html', aform=aform, form=form, username=username, user=current_user)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user. ')
        return redirect(url_for(' .index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'moment': item.moment}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'moment': item.moment}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/lpost/<int:id>', methods=['GET', 'Post'])
def lpost(id):
    lpost = LAFPost.query.get_or_404(id)
    lpost.read_count += 1
    category = Category.query.get(lpost.categories)
    category.heat += 1
    comment_count = lpost.comments.count()
    form = CommentForm()
    rform = ReplyForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=lpost,
                          author=current_user._get_current_object(),
                          moment=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published')
        return redirect(url_for('.lpost', id=lpost.id, page=-1, user=current_user))
    if rform.validate_on_submit():
        comment = Comment(body=rform.body.data,
                          post=lpost,
                          author=current_user._get_current_object(),
                          moment=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          parent=int(rform.parent))
        db.session.add(comment)
        db.session.commit()
        flash('Your reply has been published')
        return redirect(url_for('.lpost', id=lpost.id, page=-1, user=current_user))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (lpost.comments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = lpost.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('lpost.html', posts=[lpost], form=form,
                           comments=comments, pagination=pagination, user=current_user, comment_count=comment_count)


@main.route('/post/<int:id>', methods=['GET', 'Post'])
def post(id):
    result = testKey()
    keyList = result['key']
    keys = []
    k = keyList[id - 1].split()
    for i in k:
        keys.append(i)
    post = Post.query.get_or_404(id)
    post.read_count += 1
    category = Category.query.get(post.category_id)
    category.heat += 1
    post.keyA = keys[0]
    post.keyB = keys[1]
    post.keyC = keys[2]
    post.keyD = keys[3]
    post.keyE = keys[4]
    comment_count = post.comments.count()
    form = CommentForm()
    rform = ReplyForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object(),
                          moment=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published')
        return redirect(url_for('.post', id=post.id, page=-1, user=current_user))
    if rform.validate_on_submit():
        comment = Comment(body=rform.body.data,
                          post=post,
                          author=current_user._get_current_object(),
                          moment=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          parent=int(rform.parent))
        db.session.add(comment)
        db.session.commit()
        flash('Your reply has been published')
        return redirect(url_for('.post', id=post.id, page=-1, user=current_user))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination, user=current_user, comment_count=comment_count)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category_id = form.category_id.data
        categories = Category.query.get(post.category_id)
        post.categories = categories.name
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('main.index'))
        # return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category_id.data = post.category_id
    return render_template('edit_post.html', form=form)
