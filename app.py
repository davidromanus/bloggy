from os import environ
'''
in this small project, i want to create a dynamic blog where the admin can create and delete posts
the admin page will be restricted to only authenticated the user who can make,edit and delete posts
this is just basic so i will put it in just one file or two maybe
'''

from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy 
from forms import LoginForm,EditPageForm,PostForm,EditPostForm
from datetime import datetime
from flask_login import LoginManager,UserMixin,current_user,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.urls import url_parse
from flask_bcrypt import Bcrypt 

app=Flask(__name__)
login=LoginManager(app)
login.login_view='login'
app.config['SQLALCHEMY_DATABASE_URI']=environ.get('DATABASE_URL') or 'sqlite:///site.db'
app.config['SECRET_KEY']='mysecret'
bc=Bcrypt(app)
db=SQLAlchemy(app)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(db.Model,UserMixin):
	id=db.Column(db.Integer,primary_key=True)
	email=db.Column(db.String(120),index=True,unique=True)
	ps_hsh=db.Column(db.String(140))
	posts=db.relationship('Post',backref='author',lazy='dynamic')


class Post(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	sub_title=db.Column(db.String)
	content=db.Column(db.String)
	posted=db.Column(db.DateTime,default=datetime.utcnow)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return f'Post("{self.sub_title}","{self.content}","{self.pub_date}")'

class PageInfo(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	name=db.String(db.String(60))
	desc=db.Column(db.String)


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
		if user:
		    login_user(user)
		    flash('Welcome, David the handsome one','success')
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
		post=Post(sub_title=form.sub_title.data,content=form.content.data)
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

	if request.method=='POST':
		task_to_edit.sub_title=form.sub_title.data
		task_to_edit.content=form.content.data
		db.session.commit()
		flash('updated successfully','success')
		return redirect(url_for('account',sub_title=task_to_edit.sub_title,content=task_to_edit.content))
	elif request.method=='GET':
		form.sub_title.data=task_to_edit.sub_title
		form.content.data=task_to_edit.content
	return render_template('edit_post.html',form=form)

'''@app.route('/view-full-post/<int:id>')
@login_required
def view_full_post(id):
	selected=Post.query.get_or_404(id)
	return render_template('view-post-page.html',selected=selected)'''

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__=='__main__':
	app.run(debug=True)

	#https://obscure-wave-28106.herokuapp.com/