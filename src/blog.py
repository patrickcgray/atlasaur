import os
import re
from string import letters
import webapp2
import jinja2
import hashlib
import json
import datetime
import urllib

#from geo.geomodel import GeoModel

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template

#splitting up the python file
import pagehandlers


#initalize the jinja2 template
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
#I need this Jinja2 filter to be able to pass variables into the templaes and use them in Javascript
jinja_env.filters['json_encode'] = json.dumps

#global variables

#this is used in the Post and Comment database classes to make rendering them easier in HTML
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

#I use this to only select from the past couple days of posts
def hours_ago(time_h):
    return datetime.datetime.now() - datetime.timedelta(hours=time_h)

#these hashing and secure value functions are not actually in use but are for security measures
def hash_str(s):
        return hashlib.md5(s).hexdigest()

def make_secure_val(s):
        return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
        val = h.split('|')[0]
        if h == make_secure_val(val):
                return val
      # Output 404 page

#I don't believe this is actually in use anymore
def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)


############# handlers start here #############

        
#the next three pages are simply categories for the Posts and they are linked to on the main page
#they use the data from the URL to decide what information to search for and display
#I have not yet done a memcache implementation for this though I likely will before too 
        

############# this is the Login Handler #############

##this is not actually in use right now but lets the user add a record to the map 
#class MapRecorder(BlogHandler):
#    def get(self):
#        if users.get_current_user():
#            global visits
#            user = users.get_current_user()
#            logout = users.create_logout_url(self.request.uri)  
#            self.render('maprecorder.html', user = user, visits = visits, logout=logout)
#        else:
#            self.render('pleaselogin.html')
#    def post(self):
#        description = self.request.get('description')
#        title = self.request.get('title')
#        GPSlocation = self.request.get('GPSlocation')
#        postsport = self.request.get('postsport')
#        rating = self.request.get('rating')
#        
#        user = users.get_current_user()
#        user_db_qry = User.query(User.theid == user.federated_identity())
#        user_db_list = user_db_qry.fetch(1)
#        currentregistereduser = user_db_list[0]
#            
#        submitter = currentregistereduser.username
#        user_id = currentregistereduser.key.id()
#        
#        title = str(title)
#        title = title.replace(' ', '25fdsa67ggggsd5')
#        title = ''.join(e for e in title if e.isalnum())
#        title = title.replace('25fdsa67ggggsd5', '-')
#        title = title.lower()
#                
#        if description and submitter and user_id and title and GPSlocation and postsport and rating:
#            record_db = Record(
#                    description=description,
#                    submitter=submitter,
#                    user_id=user_id, 
#                    title=title,
#                    GPSlocation = str(GPSlocation),
#                    postsport = postsport,
#                    rating = int(rating)
#                    )
#            record_db.put()
#            
#            keyid=str(record_db.key.id())
#            
#            record_cache(True)
#            
#            global visits
#            user = users.get_current_user()
#            logout = users.create_logout_url(self.request.uri) 
#            
#            self.redirect('/record/%s/%s' % (keyid, title))
#                    
#        else:
#            description = self.request.get('description')
#            title = self.request.get('title')
#            location = self.request.get('location')
#            GPSlocation = self.request.get('GPSlocation')
#            postsport = self.request.get('postsport')
#            rating = self.request.get('rating')
#            
#            global visits
#            user = users.get_current_user()
#            logout = users.create_logout_url(self.request.uri)
#            
#            error = "Hey Chief you'll need to fill out every field along with a location."                    
#            self.render('maprecorder.html', user = user, visits = visits, logout=logout, description=description, 
#                        submitter=submitter, user_id=user_id, title=title, location=location, GPSlocation = GPSlocation, postsport = postsport, rating = rating, error=error)

#this helps to serve photos but I actually do it through "create serving url"
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key = str(urllib.unquote(blob_key))
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blobstore.BlobInfo.get(blob_key), save_as=True)

##### the majority of this until is not in use and is from a class I took on Udacity but it is still somewhat relevant
# might be useful for creating my review/rating pages

            
############## this is old don't worry about this stuff starts here #############
#class BlogFront(BlogHandler):
#    def get(self):
#        posts = db.GqlQuery("select * from Post order by created desc limit 10")
#        self.render('front.html', posts = posts)
#
#class NewPost(BlogHandler):
#    def get(self):
#        self.render("newpost.html")
#
#    def post(self):
#        subject = self.request.get('subject')
#        content = self.request.get('content')
#
#        if subject and content:
#            p = Post(parent = blog_key(), subject = subject, content = content)
#            p.put()
#            self.redirect('/blog/%s' % str(p.key().id()))
#        else:
#            error = "subject and content, please!"
#            self.render("newpost.html", subject=subject, content=content, error=error)
#            
#class PostList(BlogHandler):
#    def get(self):
#        posts = db.GqlQuery("select * from Post order by created desc limit 10")
#        self.render('postlist.html', posts = posts)
#
#
#
####### Unit 2 HW's
#USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
#def valid_username(username):
#    return username and USER_RE.match(username)
#
#PASS_RE = re.compile(r"^.{3,20}$")
#def valid_password(password):
#    return password and PASS_RE.match(password)
#
#EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
#def valid_email(email):
#    return not email or EMAIL_RE.match(email)
#
#class Signup(BlogHandler):
#
#    def get(self):
#        self.render("signup-form.html")
#
#    def post(self):
#        have_error = False
#        username = self.request.get('username')
#        password = self.request.get('password')
#        verify = self.request.get('verify')
#        email = self.request.get('email')
#
#        params = dict(username = username,
#                      email = email)
#
#        if not valid_username(username):
#            params['error_username'] = "That's not a valid username."
#            have_error = True
#
#        if not valid_password(password):
#            params['error_password'] = "That wasn't a valid password."
#            have_error = True
#        elif password != verify:
#            params['error_verify'] = "Your passwords didn't match."
#            have_error = True
#
#        if not valid_email(email):
#            params['error_email'] = "That's not a valid email."
#            have_error = True
#
#        if have_error:
#            self.render('signup-form.html', **params)
#        else:
#            self.redirect('/unit2/welcome?username=' + username)
#
#class Welcome(BlogHandler):
#    def get(self):
#        username = self.request.get('username')
#        if valid_username(username):
#            self.render('welcome.html', username = username)
#        else:
#            self.redirect('/unit2/signup')

############# old stuff ends here #############

from pagehandlers import posthandlers
from pagehandlers import grouphandlers
from pagehandlers import locationhandlers
from pagehandlers import otherhandlers
from pagehandlers import profilehandlers
from pagehandlers import recordhandlers
from pagehandlers import tester

#Web2App Extras config needed by SimpleAuth
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

#this is the information for all the handlers and their regexes and everything
app = webapp2.WSGIApplication([('/', otherhandlers.FrontPage),
                               ('/home', otherhandlers.FrontPage),
                               ('/community', otherhandlers.Community),
                               ('/tester', tester.Tester),
                               ('/posts', posthandlers.Posts),
                               ('/about', otherhandlers.About),
                               ('/profile', profilehandlers.Profile),
                               ('/editprofile', profilehandlers.EditProfile),
                               webapp2.Route(r'/profile<:/?><profile_id:[0-9]*?>', defaults={"profile_id":""}, handler=profilehandlers.ProfilePage, name="profile"),
                               webapp2.Route(r'/profile<:/?><profile_id:[0-9]*?><:/?><pagetype:[a-z]*?>', defaults={"profile_id":"", "pagetype":""}, handler=profilehandlers.SpecificProfilePage, name="specificprofile"),
                               ('/working', otherhandlers.Working),
                               ('/noaccess', otherhandlers.NoAccess),
                               ('/topranked', posthandlers.TopRanked),
                               ('/hotposts', posthandlers.HotPosts),
                               ('/exployrers', otherhandlers.Exployrers),
                               ('/newlocation', locationhandlers.NewLocation),
                               ('/map', locationhandlers.Map),
                               (r'/incorrectlocation/(.*)/(.*)', locationhandlers.IncorrectLocation),
                               ('/listincorrectlocations', locationhandlers.ListIncorrectLocations),
                               (r'/modifylocation/(.*)/(.*)', locationhandlers.ModifyLocation),
                               ('/share', otherhandlers.Share),
                               ('/sponsors', otherhandlers.Sponsors),
                               ('/sponsorinfo', otherhandlers.SponsorInfo),
                               (r'/addadventure/(.*)/(.*)', recordhandlers.AddAdventure),
                               ('/shareadventure', recordhandlers.ShareAdventure),
                               ('/recentrecords', recordhandlers.RecentRecords),
                               ('/recentrecords/(.*)', recordhandlers.RecentLocalRecords),
                               (r'/addtodo/(.*)/(.*)', recordhandlers.AddToDo),
                               (r'/deleterecord/(.*)/(.*)', recordhandlers.DeleteRecord),
                               (r'/editrecord/(.*)/(.*)', recordhandlers.EditRecord),
                               (r'/deletepost/(.*)/(.*)', posthandlers.DeletePost),
                               (r'/editpost/(.*)/(.*)', posthandlers.EditPost),
                               ('/login', otherhandlers.Login),
                               (r'/post/(.*)/(.*)', posthandlers.PostPage),
                               (r'/record/(.*)/(.*)', recordhandlers.RecordPage),
                               (r'/location/(.*)/(.*)', locationhandlers.LocationPage),
                               ('/recentlocations', locationhandlers.RecentLocations),
                               ('/groups', grouphandlers.GroupHandler),
                               (r'/groups/(.*)/(.*)', grouphandlers.GroupPage),
                               (r'/joingroup/(.*)/(.*)', grouphandlers.JoinGroup),
                               (r'/deletegroup/(.*)/(.*)', grouphandlers.DeleteGroup),
                               (r'/leavegroup/(.*)/(.*)', grouphandlers.LeaveGroup),
                               ('/search', otherhandlers.Search),
                               webapp2.Route(r'/land<:/?><activity:[a-zA-Z]*?>', defaults={"activity":""}, handler=posthandlers.Land, name="land"),
                               webapp2.Route(r'/air<:/?><activity:[a-zA-Z]*?>', defaults={"activity":""}, handler=posthandlers.Air, name="air"),
                               webapp2.Route(r'/sea<:/?><activity:[a-zA-Z]*?>', defaults={"activity":""}, handler=posthandlers.Sea, name="sea"),
                               ('/googlefd0f335255a9094e.html', otherhandlers.GoogleWMT),
                               (r'/upload/(.*)', recordhandlers.UploadHandler),
                               (r'/groupupload/(.*)/(.*)', grouphandlers.GroupUploadHandler),
                               (r'/profileupload/(.*)', profilehandlers.ProfileUploadHandler),
                               ('/serve/([^/]+)?', ServeHandler),
                               ('/importlocations', otherhandlers.ImportLocationHandler),
                               ('/importstateparks', otherhandlers.ImportStateParkHandler),
                               #SimpleAuth stuff is here down
                               webapp2.Route('/auth/<provider>', handler='pagehandlers.otherhandlers.AuthHandler:_simple_auth', name='auth_login'),
                               webapp2.Route('/auth/<provider>/callback', handler='pagehandlers.otherhandlers.AuthHandler:_auth_callback', name='auth_callback'),
                               webapp2.Route('/logout', handler='pagehandlers.otherhandlers.AuthHandler:logout', name='logout'),
                               ('/sa_login', tester.SimpleAuthLogin),
                               ('/sa_profile', tester.SimpleAuthProfile),                               
                               ],
                               debug=True, 
                               config=config) #Needed for SimpleAuth

############# end all code #############