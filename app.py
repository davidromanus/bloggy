from os import environ
from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy 
from forms import LoginForm,EditPageForm,PostForm,EditPostForm
from datetime import datetime
from flask_login import LoginManager,UserMixin,current_user,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.urls import url_parse
#from flask_bcrypt import Bcrypt 
from flask_ckeditor import CKEditor
import os
import secrets
from PIL import Image
from flask_migrate import Migrate
from config import Config



app=Flask(__name__)
app.config.from_object(Config)
login=LoginManager(app)
login.login_view='login'
ckeditor=CKEditor(app)
db=SQLAlchemy(app)
migrate = Migrate(app,db)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(db.Model,UserMixin):
	id=db.Column(db.Integer,primary_key=True)
	email=db.Column(db.String(120),index=True,unique=True)
	ps_hsh=db.Column(db.String(140))
	about=db.Column(db.String)
	posts=db.relationship('Post',backref='author',lazy='dynamic')


	def set_password(self,password):
		self.ps_hsh = generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.ps_hsh, password)





class Post(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	picture=db.Column(db.String(20),nullable=False)
	sub_title=db.Column(db.String)
	content=db.Column(db.String)
	posted=db.Column(db.DateTime,default=datetime.utcnow)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return f'Post("{self.sub_title}","{self.content}","{self.pub_date}")'



#save picture function
def save_picture(form_picture):
	random_hex=secrets.token_hex(8)
	_,f_ext=os.path.splitext(form_picture.filename)
	picture_fn=random_hex + f_ext
	picture_path=os.path.join(app.root_path,'static/blog_pics',picture_fn)

	output_size=(250,250)
	i=Image.open(form_picture)
	i.thumbnail(output_size)


	i.save(picture_path)

	return picture_fn


#the routes
@app.route('/')
def index():
	posts=Post.query.order_by(Post.posted.desc()).all()
	return render_template('index.html',posts=posts,title='My Blog')

@app.route('/login',methods=['POST','GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('account'))
	form=LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is None or not user.check_password(form.password.data):
		    flash('invalid username or password!','danger')
		    return redirect(url_for('login'))
		login_user(user)
		return redirect(url_for('account'))
		next_page=request.args.get('next')
		if not next_page or url_parse(next_page).netloc !='':
			next_page=url_for('index')
		return redirect(next_page)
	return render_template('login.html',title='login page',form=form)

@app.route('/account')
@login_required
def account():
	posts=Post.query.order_by(Post.posted.desc()).all()
	return render_template('account.html',title='admin page',posts=posts)

@app.route('/create_post',methods=['POST','GET'])
@login_required
def create_post():
	form=PostForm()
	if form.validate_on_submit():
		pic=save_picture(form.picture.data)
		post=Post(sub_title=form.sub_title.data,content=form.content.data,picture=pic)
		db.session.add(post)
		db.session.commit()
		flash('posted','success')
		return redirect(url_for('account'))
	return render_template('create_post.html',form=form)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
	item_to_delete=Post.query.get_or_404(id)
	db.session.delete(item_to_delete)
	db.session.commit()
	flash('deleted','danger')
	return redirect(url_for('account'))

@app.route('/edit/<int:id>',methods=['POST','GET'])
@login_required
def edit_post(id):
	form=EditPostForm()
	task_to_edit=Post.query.get_or_404(id)

	if form.validate_on_submit():
		if form.picture.data:
			pic=save_picture(form.picture.data)
			post.task_to_edit.picture=pic 
		task_to_edit.sub_title=form.sub_title.data
		task_to_edit.content=form.content.data
		db.session.commit()
		flash('updated successfully','success')
		return redirect(url_for('account',sub_title=task_to_edit.sub_title,
			content=task_to_edit.content,picture=task_to_edit.picture))
	elif request.method=='GET':
		form.picture.data=task_to_edit.picture
		form.sub_title.data=task_to_edit.sub_title
		form.content.data=task_to_edit.content
	return render_template('edit_post.html',form=form)

@app.route('/the_full_gist/<int:id>')
def full_post(id):
	post=Post.query.get_or_404(id)
	return render_template('article.html',post=post)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__=='__main__':
	app.run(debug=True)