import webapp2
import json
import jinja2
import os
import logging

#added to include needed modules for SimpleAuth
from webapp2_extras import sessions, auth
from google.appengine.api import urlfetch

urlfetch.set_default_fetch_deadline(60) 

#initalize the jinja2 template
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader('templates'),
							   autoescape = True)
#I need this Jinja2 filter to be able to pass variables into the templaes and use them in Javascript
jinja_env.filters['json_encode'] = json.dumps

#this is my base handler and gives some basic functions that most of my handlers use
class BlogHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
	#this doesn't quite work for the general case right now
	def error(self, code):
		super(BlogHandler, self).error(code)
		if code == 404:
			self.render("working.html")
		if code == 500:
			self.render("servererror.html")
	# Output 404 page

	def dispatch(self):
		# Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)

		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
			# Save all sessions.
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session() 
		
	@webapp2.cached_property
	def logged_in(self):
		"""Returns true if a user is currently logged in, false otherwise"""
		try:
			return self.session['_user_id'] is not None
		except KeyError:
			return False
	
	def get_user(self):
		if self.logged_in:
			return self.session['_current_user']
		else:
			return False	   
		
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)