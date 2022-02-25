from flask_wtf import FlaskForm 
from wtforms import PasswordField,TextAreaField,SubmitField,StringField,TextField
from wtforms.validators import DataRequired,Length 
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Length(min=2,max=100)])
	password=PasswordField('Password',validators=[DataRequired(),Length(min=8,max=120)])
	submit=SubmitField('Sign In')

class EditPageForm(FlaskForm):
	name=StringField('page name',validators=[DataRequired(),Length(min=2,max=100)])
	desc=TextField('description',validators=[DataRequired(),Length(min=8,max=120)])
	submit=SubmitField('Update')

class PostForm(FlaskForm):
	sub_title=StringField('Title',validators=[DataRequired()])
	content=CKEditorField('Content',validators=[DataRequired()])
	submit=SubmitField('Post')

class EditPostForm(FlaskForm):
	sub_title=StringField('New Title',validators=[DataRequired()])
	content=CKEditorField('Content',validators=[DataRequired()])
	submit=SubmitField('update')