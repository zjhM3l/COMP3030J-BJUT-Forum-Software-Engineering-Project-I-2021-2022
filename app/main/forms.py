from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import InputRequired, Length, AnyOf
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError


class EditProfileForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'}, validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters,'
                                              'numbers, dots or underscores')])
    birthday = StringField('Birthday', render_kw={'placeholder': 'January 1st'},
                           validators=[DataRequired(), Length(1, 64)])
    institute = StringField('BirthPlace', validators=[AnyOf(values=['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
                                   '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北',
                                   '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏',
                                   '陕西', '甘肃', '青海', '宁夏', '新疆', '台湾', '香港', '澳门', '南海诸岛'])])
    name = StringField('Real name', render_kw={'placeholder': 'ZhangSan'}, validators=[Length(0, 64)])
    about_me = TextAreaField('About me', render_kw={'placeholder': 'Good'},
                             validators=[DataRequired(), Length(0, 500)])
    submit = SubmitField('Save Changes')
    Upload = SubmitField('Change Portrait')

'''
    PersonalizedSignature = TextAreaField('PersonalizedSignature', render_kw={'placeholder': 'Good'},
                                          validators=[DataRequired(), Length(0, 500)])
    submit = SubmitField('save changes')
    UploadPortrait = SubmitField('change portrait')'''


class SearchForm(FlaskForm):
    text = TextAreaField('What are u looking for?', validators=[DataRequired()])
    submit = SubmitField('Search')


class LikePostForm(FlaskForm):
    submit = SubmitField('Might Like')


class PostForm(FlaskForm):
    category_id = TextAreaField('Choose one category above', validators=[DataRequired()])
    title = TextAreaField('Change your title here:', validators=[DataRequired()])
    body = PageDownField('Change your post here:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = StringField('hhhh', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ReplyForm(FlaskForm):
    body = StringField('hhhh', validators=[DataRequired()])
    parent = StringField()
    submit = SubmitField('Submit')


class AnnouncementForm(FlaskForm):
    title = TextAreaField('Enter the title of the Announcement', validators=[DataRequired()])
    body = PageDownField('Enter the content of the Announcement', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ChangeAvatarForm(FlaskForm):
    avatar = FileField('')
    submit = SubmitField('Submit')


class LostAndFoundForm(FlaskForm):
    title = TextAreaField('Add your title here:', validators=[DataRequired()])
    details = TextAreaField('Add some details here:', validators=[DataRequired()])
    # details = PageDownField('Add some details here:', validators=[DataRequired()])
    photo = FileField('',validators=[DataRequired()])
    lorf = StringField('Did you "lose" or "find" something?')
    location = StringField('Where did you lose/find it?', validators=[DataRequired()])
    contact = StringField('Leave your contact', validators=[DataRequired()])
    reward = StringField('reward if u lost, or nothing add here will be o')
    submit = SubmitField('Submit')

    def validate_lorf(self, field):
        if field.data != "lose" and field.data != "find":
            raise ValidationError('Must be "lose" or "find"')
