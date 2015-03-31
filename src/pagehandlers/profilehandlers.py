#this file has everything relating to the user's personal profile

#external imports
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.ext import blobstore

from geopy import geocoders
import logging


#internal imports
from basehandler import BlogHandler
from general.dbmodels import User
from general.dbmodels import Location
from general.dbmodels import Group
from general.memcache import profile_cache
from general.memcache import profile_record_cache
from general.memcache import profile_todo_cache

#this class is for the User before they have filled out their profile information
#if they have already filled it out then they are redirected to ProfilePage   
class Profile(BlogHandler):
    def get(self):
        if self.get_user():
            user = self.get_user()
            logging.error("username")
            logging.error(user['username'])
            profile_id = user['model_id']
            
            if user['username']:
                self.redirect('/profile/%s' % (profile_id))
            else:      
                self.redirect('/editprofile')
        else:
            self.redirect("/login")
            
#this lets users provide a photo
class ProfileUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, profile_id):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        blobRef = blob_info.key()
        user = User.get_by_id(int(profile_id))
        user.avatar = blobRef
        user.put()
        user.created = None
        user.last_modified = None
        profile_cache(profile_id, True)
        self.redirect('/profile/%s' % (profile_id))   

#this class is where users are redirected if it is someone else's profile or if they have already filled in profile information
class ProfilePage(BlogHandler):
    def get(self, *args, **kwargs):
        if self.get_user():
            profile_id = int(kwargs.get("profile_id"))
            profileowner = User.get_by_id(profile_id)
            
            user = self.get_user()
                
            current_profile_id = user['model_id']
            
            records = profile_record_cache(profile_id)
            photosandinfo = []
            for record in records:
                if record.blobRefs:
                    for blobRef in record.blobRefs:
                        photosandinfo.append((images.get_serving_url(blobRef, size=None, crop=False, secure_url=None), record.title, record.key.id()))
            user_id = str(profileowner.key.id())
            
            quote = profileowner.quote
            
            avatar=None
            if profileowner.avatar:
                avatar = images.get_serving_url(profileowner.avatar, size=None, crop=False, secure_url=None)
            if not avatar:
                avatar = 'http://i.imgur.com/RE9OX.jpg'
                
            #as you can probably tell personalposts is where I am storing the posts from the profile owner
            if current_profile_id == profile_id:
                owner = True
            else:
                owner = None                   
            
            groups = None
            if profileowner.groups:
                groups = []
                for group in profileowner.groups:
                    groups.append(Group.get_by_id(int(group)))
                
            upload_url = blobstore.create_upload_url('/profileupload/%s' % (profile_id))
            
            self.render('profile.html', user=user, quote=quote, groups=groups, avatar=avatar, records=records, 
                        photosandinfo=photosandinfo, profile_id=profile_id, upload_url=upload_url, profileowner=profileowner, owner=owner)

        else:
            self.render('pleaselogin.html')

#this handler is for all of the other tabs on the user profile
class SpecificProfilePage(BlogHandler):
    def get(self, *args, **kwargs):
        if self.get_user():
            profile_id = int(kwargs.get("profile_id"))
            pagetype = str(kwargs.get("pagetype"))
            profileowner = User.get_by_id(profile_id)
            
            user = self.get_user()
                
            current_profile_id = user['model_id']
            
            user_id = str(profileowner.key.id())
            quote = profileowner.quote
            
            avatar=None
            if profileowner.avatar:
                avatar = images.get_serving_url(profileowner.avatar, size=None, crop=False, secure_url=None)
            if not avatar:
                avatar = 'http://i.imgur.com/RE9OX.jpg'
                
            #I am declaring these now because I don't want to retreive them unless I need them
            records = None
            owner = None
            personalposts = None
            todolocations = None
            
                
            #as you can probably tell personalposts is where I am storing the posts from the profile owner
            if current_profile_id == profile_id:
                owner = True
            if pagetype == "adventures":
                #then I need to send in the locations from this user and I need to render that with a map
                records = profile_record_cache(profile_id)
                
            elif pagetype == "posts":
                #then I need to render the posts
                personalposts = profile_cache(user_id, True)
            
            elif pagetype == "todolist":
                #give the todolist locations list
                todolocationids = profile_todo_cache(user_id)
                todolocations=[]
                for id in todolocationids:
                    todolocations.append(Location.get_by_id(id))
            else:
                self.redirect('/profile/%s' % (profile_id))
                                
            self.render('specificprofile.html', user=user, quote=quote, avatar=avatar, records=records, 
                        personalposts=personalposts, todolocations=todolocations, pagetype=pagetype, profile_id=profile_id, profileowner=profileowner, owner=owner)

        else:
            self.render('pleaselogin.html')

#this class is where the user is sent when they want to edit their profile info after it has already been entered
class EditProfile(BlogHandler):
    def get(self):
        if not self.get_user():
            self.redirect("/login")
        else:
            user = self.get_user()
            
            username = None
            bio = None
            quote = None
            geo_center=None
            email = None
            
            if user['username']:
                username = user['username']
            if user['bio']:
                bio = user['bio']
            if user['quote']:
                quote = user['quote']
            if user['geo_center']:
                geo_center = user['geo_center']
            if user['email']:
                email = user['email']
                
            self.render('editprofile.html', bio=bio, username=username, quote=quote, GPS=geo_center, user = user, email=email)
    def post(self):
        username = self.request.get('username')
        bio = self.request.get('bio')
        quote = self.request.get('quote')
        geo_center = self.request.get('geo_center')
        email = self.request.get('email')
        
        if username and bio:
            user = self.get_user()
            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0]
            
            profile_id = currentregistereduser.key.id()
            currentregistereduser.username = username
            currentregistereduser.bio = bio
            currentregistereduser.quote = quote
            currentregistereduser.email = email
            
            error = None
            GPSlocation = None
            if geo_center:
                g = geocoders.GoogleV3()
                #to catch an error where there is no corresponding location
                try:
                    #to catch an error where there are multiple returned locations
                    try:
                        place, (lat, lng) = g.geocode(geo_center)
                        place, searched_location = g.geocode(geo_center)
                    except ValueError:
                        geocodespot = g.geocode(geo_center, exactly_one=False)
                        place, (lat, lng) = geocodespot[0]
                        place, searched_location = geocodespot[0]
                    GPSlocation = "("+str(lat)+", "+str(lng)+")"                 

                #this is straight from the docs:  http://code.google.com/p/geopy/wiki/Exceptions and happens when there is no location that matches
                except geocoders.google.GQueryError:
                    error = "We cannot find " + geo_center +"... try to be a little more specific or search a nearby location."
                    
                    if error:
                        user = self.get_user()
                        self.render('editprofile.html', bio=bio, username=username, error=error, quote=quote, user = user)
            
            if GPSlocation:
                currentregistereduser.geo_center = GPSlocation
            if not currentregistereduser.geo_center:
                currentregistereduser.geo_center = None
                
            if currentregistereduser.key.id() == 125002:
                currentregistereduser.admin = True
            
            currentregistereduser.put()
            currentregistereduser.created = None
            currentregistereduser.last_modified = None
            currentregistereduser.avatar = None
            self.session['_current_user'] = currentregistereduser.to_dict()
            
            profile_cache(profile_id, True)

            self.redirect('/profile/%s' % (profile_id))
                    
        elif not username or not bio:
            user = self.get_user()
                    
            error = "Come on you can put a little something."
            self.render("editprofile.html", username=username, bio=bio, quote=quote, email=email, error=error, user=user)   
