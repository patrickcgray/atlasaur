#this file has all of the small handlers that do not need their own file

#external imports
import json
import time

from google.appengine.api import urlfetch
from google.appengine.api import images
from google.appengine.ext import blobstore

from geopy import geocoders 
from geopy import distance
from geopy import point

#internal imports
from basehandler import BlogHandler
from general.memcache import exployrer_cache
from general.memcache import recent_record_cache
from general.memcache import record_cache
from general.memcache import location_cache
from general.memcache import ranked_location_cache
from general.memcache import main_cache
from general.memcache import admin_cache
from general.memcache import group_record_cache
from general.memcache import group_cache
from general.dbmodels import User
from general.dbmodels import Location

import logging
from operator import attrgetter

#Importing SimpleAuth and it's secrets.py file
from simpleauth import SimpleAuthHandler
import secrets
#added to include needed modules for SimpleAuth

import webapp2

#this is actually my front root page right now
class FrontPage(BlogHandler):
    def get(self):
        user = self.get_user()
        posts = admin_cache()
        if user:
            group_records = []
            groups = []
            
            if user['theid'] == 'google:115668307812600082846':
                user_db_qry = User.query(User.theid == user['theid'])
                user_db_list = user_db_qry.fetch(1)
                currentregistereduser = user_db_list[0]
                       
                currentregistereduser.admin = True
                currentregistereduser.put()
                
            
            #this needs to be cleaned up!!
            if user['groups']:
                for group in user['groups']:
                    try:
                        group_record = group_record_cache(group)[0]
                        group_records.append(group_record)
                        group_record = group_record_cache(group)[1]
                        group_records.append(group_record)
                    except IndexError:
                        nothing = None
                group_records = group_records[:10]
                #I need to optimize this so that it isn't concatenating the all the lists
                #I need to do a while loop that max does 10 iterations
                group_records = sorted(group_records, key=attrgetter('created'), reverse=True)
            
            if not group_records:
                groups = group_cache()
                groups = groups[:10]
            
            new_records = []
            records_to_render = []
            record_photos = []

            if user['geo_center']:
                logging.error('user has a geo center')
                latlng = (user['geo_center']).split(",")
                lat = latlng[0][1:]
                lng = latlng[1][1:-1]
                
                searched_location = point.Point(float(lat), float(lng))
                
                records = record_cache()                   
                for record in records:
                    rec_latlng = (record.GPSlocation).split(",")
                    rec_lat = float(rec_latlng[0][1:])
                    rec_lng = float(rec_latlng[1][1:-1])
                    
                    distance.distance = distance.GreatCircleDistance
                    location_distance = distance.distance(searched_location, point.Point(rec_lat, rec_lng)).miles
                    #make this 20 a variable that the user can set and have it be 10, 25, 50, 100, 200
                    if location_distance < int(150):
                        new_records.append(record)
                
                records_to_render = new_records[:20]
                
                for record in records_to_render:
                #this makes sure that we have some photos
                    if record.blobRefs:
                        logging.error('adding photo')
                        record_photos.append((images.get_serving_url(record.blobRefs[0], size=None, crop=False, secure_url=None), record.title, record.key.id()))
                record_photos=record_photos[:6]

            else:
                nothing=None
            
            self.render("personalfrontpage.html", user=user, groups=groups, record_photos=record_photos, records_to_render=records_to_render, currentregistereduser=user, group_records=group_records, posts=posts)
            
        else:
            image = None
            current_time = int(time.time())
            if current_time % 4 == 0:
                image = "http://i.imgur.com/bxiV9.jpg"
            elif current_time % 3 == 0:
                image = "http://i.imgur.com/L2tSx.jpg"
            elif current_time % 2 == 0:
                image = "http://i.imgur.com/0eyX0.jpg"
            else:
                image = "http://i.imgur.com/VXC47.jpg"                
            
            self.render("frontpage.html", image=image, user=user, posts=posts)

class Exployrers(BlogHandler):   
    def get(self):
        exployrers = exployrer_cache()
        title = 'Top Exployrers'
        user = self.get_user()
        self.render('exployrers.html', user = user, exployrers=exployrers, title=title)
        
class Sponsors(BlogHandler):
    def get(self):
        user = self.get_user()
        self.render('sponsors.html', user = user)
        
class SponsorInfo(BlogHandler):
    def get(self):
        user = self.get_user()
        self.render('sponsorinfo.html', user = user)

class About(BlogHandler):
    def get(self):
        user = self.get_user()
        self.render('about.html', user = user)
        
class Search(BlogHandler):
    def get(self):
        user = self.get_user()
        self.render('search.html', user = user)

#sent whenever a page has not been completed
class Working(BlogHandler):
    def get(self):
        user = self.get_user()
        self.render('working.html', user = user)
        
class NoAccess(BlogHandler):
    def get(self):
        user = self.get_user()
        self.render('noaccess.html', user = user)

#links to social media info
class Share(BlogHandler):
    def get(self):
        user = self.get_user()
        self.render('share.html', user = user)

#this just lets me put new locations in
class ImportLocationHandler(BlogHandler):
 """ Handler for importing existing apps."""

 def get(self):
   user = self.get_user()
   user_db_qry = User.query(User.theid == user.federated_identity())
   user_db_list = user_db_qry.fetch(1)
   currentregistereduser = user_db_list[0]
        
   submitter = currentregistereduser.username
   user_id = currentregistereduser.key.id()
   # Need admin access to import
   if not user:
     self.error(403)
   # Fetch JSON of published spreadsheet
   url = "https://spreadsheets.google.com/feeds/list/0AsZE8AuY2VhrdGxDMmpoR3BIYy1vdTBWYTZBcEtoRkE/od6/public/values?alt=json"
   result = urlfetch.fetch(url)
   if result.status_code == 200:
     feed_obj = json.loads(result.content)
     if "feed" in feed_obj:
       entries = feed_obj["feed"]["entry"]
       # Make an Application entity for each entry in feed
       for entry in entries:
         description = entry['gsx$description']['$t']
         GPSlocation = entry['gsx$gps']['$t']

         title = entry['gsx$location']['$t']
         title = ''.join([x for x in title if ord(x)<128])
         title = title.replace(' ', '25fdsa67ggggsd5')
         title = ''.join(e for e in title if e.isalnum())
         title = title.replace('25fdsa67ggggsd5', '-')
         
         g = geocoders.GoogleV3()

         try:
             place, (lat, lng) = g.geocode(title)
         except ValueError:
             geocodespot = g.geocode(title, exactly_one=False)
             place, (lat, lng) = geocodespot[0]
         GPSlocation = "("+str(lat)+", "+str(lng)+")"

         location = Location(
                             description = description[:-4], 
                             locationtype = "National Park/Forest",
                             GPSlocation = GPSlocation,
                             Lat = float(lat),
                             Long = float(lng),
                             user_id=user_id,
                             title = str(title),
                             recordRefs = [],
                             updateRefs = [],
                             website = None,
                             todoCount = 0,
                             rating = 0.0,
                             ratingCount = int(0))
         location.put()

#this imports the NC State Parks
class ImportStateParkHandler(BlogHandler):
 """ Handler for importing existing apps."""

 def get(self):
   user = self.get_user()
   user_db_qry = User.query(User.theid == user.federated_identity())
   user_db_list = user_db_qry.fetch(1)
   currentregistereduser = user_db_list[0]
        
   submitter = currentregistereduser.username
   user_id = currentregistereduser.key.id()
   # Need admin access to import
   if not user:
     self.error(403)
   # Fetch JSON of published spreadsheet
   url = "https://spreadsheets.google.com/feeds/list/0AsZE8AuY2VhrdHBkQ0xINHdnbksyaXY0ZVFMcnNIWGc/od6/public/values?alt=json"
   result = urlfetch.fetch(url)
   if result.status_code == 200:
     feed_obj = json.loads(result.content)
     if "feed" in feed_obj:
       entries = feed_obj["feed"]["entry"]
       # Make an Application entity for each entry in feed
       for entry in entries:
         description = entry['gsx$description']['$t']
         g = geocoders.GoogleV3()
         title = entry['gsx$location']['$t']
         title = str(title)
         title = title.replace(' ', '25fdsa67ggggsd5')
         title = ''.join(e for e in title if e.isalnum())
         title = title.replace('25fdsa67ggggsd5', '-')

         try:
             place, (lat, lng) = g.geocode(title+", North Carolina")
         except ValueError:
             geocodespot = g.geocode(title+", North Carolina", exactly_one=False)
             place, (lat, lng) = geocodespot[0]
         GPSlocation = "("+str(lat)+", "+str(lng)+")"
         location = Location(
                             description = description, 
                             locationtype = "State Park/Forest",
                             GPSlocation = GPSlocation,
                             Lat = float(lat),
                             Long = float(lng),
                             user_id=user_id,
                             title = title,
                             recordRefs = [],
                             updateRefs = [],
                             website = None,
                             todoCount = 0,
                             rating = 0.0,
                             ratingCount = int(0))
         location.put()
         
#class for google's verification code  
class GoogleWMT(BlogHandler):
    def get(self):
        self.render('googlefd0f335255a9094e.html')
        
#this is the old front page but is /home on Exployre and under the Inspire tab
class Community(BlogHandler):
    def get(self):
        
        photosandinfo = []
        for record in record_cache():
            #this makes sure that we have some photos and that the record is of good quality
            if record.blobRefs and record.exceptional > 0 :
                photosandinfo.append((images.get_serving_url(record.blobRefs[0], size=None, crop=False, secure_url=None), record.title, record.key.id(), record.whatdidyoudo))
                
        records = recent_record_cache()
        records = records[:10]
        
        groups = group_cache()
        groups = groups[:10]
        groups = sorted(groups, key=attrgetter('recordCount'), reverse=True)

        
        posts = main_cache()
        posts = posts[:10]
        
        exployrers = exployrer_cache()

        #need to set this up for all of the other locations places whenever a new record is made and rated
        ranked_locations = location_cache()
        ranked_locations = ranked_locations[:10]
        ranked_locations = sorted(ranked_locations, key=attrgetter('rating'), reverse=True)

        user = self.get_user()
        
        self.render('community.html', user = user, photosandinfo=photosandinfo, posts=posts, groups=groups, exployrers=exployrers, ranked_locations=ranked_locations)

class AuthHandler(BlogHandler, SimpleAuthHandler):
    """Authentication handler for all kinds of auth."""
    def _on_signin(self, data, auth_info, provider):
        """Callback whenever a new or existing user is logging in.
        data is a user info dictionary.
        auth_info contains access token or oauth token and secret.

        See what's in it with logging.info(data, auth_info)
        """

        logging.info(data, auth_info)
            
        auth_id = '%s:%s' % (provider, data['id'])
        
        # 1. check whether user exist, e.g.
        #    User.get_by_auth_id(auth_id)
        #
        # 2. create a new user if it doesn't
        #    User(**data).put()
        #
        # 3. sign in the user
        #    self.session['_user_id'] = auth_id
        #
        # 4. redirect somewhere, e.g. self.redirect('/profile')
        #
        # See more on how to work the above steps here:
        # http://webapp-improved.appspot.com/api/webapp2_extras/auth.html
        # http://code.google.com/p/webapp-improved/issues/detail?id=20
    
        currentregistereduser = None
        #check for user existance upon login/registration
        try:
            user_db_qry = User.query(User.theid == auth_id)
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0]
            
        #if the user does not exist yet
        except IndexError:
            name = None
            #
            try:
                name = data['name']
            except KeyError:
                name = None
                
            user_db = User(
                name=name,
                theid=auth_id,
                visits = 0,
                medals = 0,
                prestige = 100,
                )
            user_db.put()
            user_db.model_id = user_db.key.id()
            user_db.put()
            
            currentregistereduser = user_db
            exployrer_cache(True)
                        
        self.session['_user_id'] = auth_id
        self.session['data'] = data
        currentregistereduser.created = None
        currentregistereduser.last_modified = None
        currentregistereduser.avatar = None
        self.session['_current_user'] = currentregistereduser.to_dict()
        
        if currentregistereduser.username:
            self.redirect("/")
        else:
            self.redirect("/profile")
    
    def logout(self):
        self.session['_user_id'] = None
        self.session['data'] = None
        self.session['_current_user'] = None
        self.redirect('/login')
    
    def _callback_uri_for(self, provider):
        return self.uri_for('auth_callback', provider=provider, _full=True)
    
    def _get_consumer_info_for(self, provider):
        """Should return a tuple (key, secret) for auth init requests.
        For OAuth 2.0 you should also return a scope, e.g.
        ('my app id', 'my app secret', 'email,user_about_me')
        
        The scope depends solely on the provider.
        See example/secrets.py.template
        """
        return secrets.AUTH_CONFIG[provider]

#Exployre uses OpenID as its login system right now and I would like it changed to SimpleAuth
class Login(BlogHandler):
    def get(self):        
        user = self.get_user()
        self.render('login.html', user = user, logged_in = self.logged_in)
