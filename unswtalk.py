#!/web/cs2041/bin/python3.6.3


import os
from flask import Flask, render_template, session
import sys
import json

data_folder = 'dataset-large'
template_folder = 'templates'
templates = {
    'profile' : 'profile.html',
    'friends_list' : 'friends_list.html',
    'timeline' : 'timeline.html'
}
#app = Flask(__name__)
app = Flask(__name__,
	template_folder = template_folder,	
	static_folder = data_folder)


def get_student_detail(zid):
	student_detail = {}
	student_txt = data_folder+'/'+zid+'/Student.txt'
	if os.path.exists(student_txt):
		with open(student_txt,'r') as student_file:
			details = student_file.readlines()
		for detail in details:
			key,value = detail.strip().split(':')
			student_detail[key.strip()] = value.strip()
		if 'friends' in student_detail.keys():
			student_detail['friends'] = student_detail['friends'][2:-2].split(',')
		if 'courses' in student_detail.keys():
			student_detail['courses'] = student_detail['courses'][2:-2].split(',')
		if os.path.exists(data_folder+'/'+zid+'/img.jpg'):
			student_detail['img'] = data_folder+'/'+zid+'/img.jpg'
		else:
			student_detail['img'] = data_folder+'/avatar.jpg'
    return student_detail
def get_timeline_posts(zid):
	posts_details = []
	index = {}
	com_index = {}
	student_folder = data_folder+'/'+zid
	if os.path.exists(student_folder):
		posts = os.listdir(student_folder)
		posts.sort(reverse=True)
		l = len(posts)-1
		while l >= 0:
			if posts[l] == 'student.txt' or posts[l] == 'img.jpg':
				del posts[l]
				l += 1
			l -= 1
		i=0
		j=0
		for post in posts:
			#print post
			hier = post.split('.')[0].split('-')
			if len(hier)  == 1:
				key = 'post'
			if len(hier) == 2:
				key = 'comment'
			if len(hier) == 3:
				key = 'reply'
			post_details = {}
			with open(student_folder+'/'+post,'r') as student_file:
				details = student_file.readlines()	
			for detail in details:
				chunks = detail.strip().split(':')
				post_details[str(chunks[0].strip())] = ' '.join(chunks[1:]).strip()
		
			if 'message' in post_details.keys():
				words = post_details['message'].split(' ')
				for ii in range(len(words)):
					word = words[ii]
					if word in os.listdir(data_folder):
						words[ii] = '<a href=\'/user/'+word+'\'>Visit - '+word+'</a>'
				post_details['message'] = ' '.join(words)
		return posts_details
	else:
		return []
@app.route('/friends-list/<zid>')
def show_friends_list(zid):
	friends = []
	friends_list = get_student_detail(zid)['friends']
	for friend in friends_list:
		friend_detail = get_student_detail(friend.strip())
		if len(friend_detail.keys()) > 0:
			friends.append(
				{
				'zid' : friend_detail['zid'],
				'details' : {
						'full_name' : friend_detail['full_name'],
						'img' : friend_detail['img']
					}
				}
			)
	return render_template(templates['friends_list'],result = friends)

@app.route('/user/<zid>')
def show_profile(zid):
	student_txt = data_folder+'/'+zid+'/Student.txt'
	if os.path.exists(data_folder+'/'+zid) and os.path.exists(student_txt):
		if os.path.exists(template_folder+'/'+templates['profile']):
			student_detail =  get_student_detail(zid)
			return render_template(templates['profile'],result = student_detail)
	else:
		return 'Server Error - HTTP 404 - page not found'


@app.route('/timeline/<zid>')
def show_timeline(zid):
	student_txt = data_folder+'/'+zid+'/Student.txt'
	if os.path.exists(data_folder+'/'+zid) and os.path.exists(student_txt):
		if os.path.exists(template_folder+'/'+templates['profile']):
			student_detail =  get_student_detail(zid)
			
			return render_template(templates['timeline'],result = student_detail,posts = get_timeline_posts(zid))
		else:
			return 'Server Error - HTTP 404 - page not found'
	else:
		return 'User not Found'

def validate_user(zid,password):
	user_details = get_student_detail(zid.strip())
	if user_details['password'] == password:
		return True
	else:
		return False
	
@app.route('/login',methods=['GET','POST'])
def show_login_page():
	if os.path.exists(template_folder + '/' + templates['login']):
		if request.method == 'POST':
			zid = request.form.get('zid')
			if zid == None or zid == '':
				return render_template(templates['login'])
			elif validate_user(zid,str(request.form.get('password'))):
				return redirect('/timeline/'+zid)
			else:
				return render_template(templates['login'],error = 'Not a valid user')	
		else:
			return render_template(templates['login'])
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
