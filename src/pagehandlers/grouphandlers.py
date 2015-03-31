#this page has everything relating to groups

#external imports
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

from operator import attrgetter
import json

from geopy import geocoders 
from geopy import distance
from geopy import point


#internal imports
from basehandler import BlogHandler
from general.dbmodels import User
from general.dbmodels import Record
from general.dbmodels import Group
from general.dbmodels import GroupComment
from general.memcache import group_record_cache
from general.memcache import group_member_cache
from general.memcache import group_cache
from general.memcache import record_cache
from general.memcache import individual_record_cache
from general.memcache import group_comment_cache

#this displays the main group page
class GroupHandler(BlogHandler):
    def get(self):
        groups = group_cache()
        search_location = self.request.get("search_location")
        search_postsport = self.request.get("search_postsport")
        GPSlocation = None
        error=None
        groups_to_render = None
        
        if search_location:
            g = geocoders.GoogleV3()
            searched_location = None
            #to catch an error where there is no corresponding location
            try:
                #to catch an error where there are multiple returned locations
                try:
                    place, (lat, lng) = g.geocode(search_location)
                    place, searched_location = g.geocode(search_location)
                except ValueError:
                    geocodespot = g.geocode(search_location, exactly_one=False)
                    place, (lat, lng) = geocodespot[0]
                    place, searched_location = geocodespot[0]
                GPSlocation = "("+str(lat)+", "+str(lng)+")"
                
                groups = group_cache()
                return_groups = []                   
                for group in groups:
                    distance.distance = distance.GreatCircleDistance
                    location_distance = distance.distance(searched_location, point.Point(group.lat, group.lng)).miles
                    #make this 20 a variable that the user can set and have it be 10, 25, 50, 100, 200
                    if location_distance < 300:
                        return_groups.append(group)
                groups = return_groups
                search=True
                groups_to_render = sorted(groups, key=attrgetter('recordCount'), reverse=True)
                groups_to_render = groups_to_render[:10]
            #this is straight from the docs:  http://code.google.com/p/geopy/wiki/Exceptions and happens when there is no location that matches
            except geocoders.google.GQueryError:
                error = "We cannot find " + search_location +"... try to be a little more specific or search a nearby location."
            
        
        user = self.get_user() 
        self.render('groups.html', groups=groups, user = user, error=error, groups_to_render=groups_to_render, GPSlocation=GPSlocation)
    def post(self):
        name = self.request.get("name")
        description = self.request.get("description")
        location = self.request.get("location")
        postsport = self.request.get("postsport")
        public = self.request.get("public")
        
        error = None
        GPSlocation = None
        lat = None
        lng = None
        
        if location:        
                g = geocoders.GoogleV3()
                #to catch an error where there is no corresponding location
                try:
                    #to catch an error where there are multiple returned locations
                    try:
                        place, (lat, lng) = g.geocode(location)
                        place, searched_location = g.geocode(location)
                    except ValueError:
                        geocodespot = g.geocode(location, exactly_one=False)
                        place, (lat, lng) = geocodespot[0]
                        place, searched_location = geocodespot[0]
                    GPSlocation = "("+str(lat)+", "+str(lng)+")"                 

                #this is straight from the docs:  http://code.google.com/p/geopy/wiki/Exceptions and happens when there is no location that matches
                except geocoders.google.GQueryError:
                    error = "We cannot find " + location +"... try to be a little more specific or search a nearby location."
                    
        if error:
            groups = group_cache
            user = self.get_user()
            self.render('groups.html', groups=groups, name=name, description=description, location=location, error=error, user = user)
        
        publicbool = True
        if public == "false":
            publicbool = False
        
        name = str(name)
        name = name.replace(' ', '25fdsa67ggggsd5')
        name = ''.join(e for e in name if e.isalnum())
        name = name.replace('25fdsa67ggggsd5', '-')
        
        user = self.get_user()
            
        creator = user['username']
        user_id = user['model_id']
        
        if name and description:
            group_db = Group(
                    description=description,
                    creator=creator,
                    user_id=user_id, 
                    name=name,
                    GPSlocation=GPSlocation,
                    lat=lat,
                    lng=lng,
                    public = publicbool,
                    recordCount = 0,
                    postsport=[]
                    )
            group_db.postsport.append(postsport)
            group_db.put()
            

            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0]
            
            #need to check if the user has any groups yet
            if not user['groups']:
                currentregistereduser.groups = []
            currentregistereduser.groups.append(group_db.key.id())
            currentregistereduser.put()
            
            currentregistereduser.created = None
            currentregistereduser.last_modified = None
            currentregistereduser.avatar = None
            self.session['_current_user'] = currentregistereduser.to_dict()
            
            group_cache(True)
            
            self.redirect('/groups/%s/%s' % (group_db.key.id(), group_db.name))
        else:
            groups = group_cache()
            error = "Hey boss you'll need to provide both a title and a short description." 
            self.render('groups.html', groups=groups, name=name, description=description, location=location, error=error, user = user)

#this displays individual group pages
class GroupPage(BlogHandler):
    def get(self, group_id, name):
        group = Group.get_by_id(int(group_id))
        records = group_record_cache(int(group_id))
        members = group_member_cache(int(group_id))
        comments = group_comment_cache(int(group_id))
        
        avatar=None
        if group.avatar:
            avatar = images.get_serving_url(group.avatar, size=None, crop=False, secure_url=None)
        if not avatar:
            avatar = 'http://i.imgur.com/RE9OX.jpg'
        
        creator = False
        member = False
        user = self.get_user()
        if user:

            user_id = user['model_id']
            
            if str(user_id) == str(group.user_id):
                creator = True
            elif int(group_id) in user['groups']:
                member = True
                
        upload_url = blobstore.create_upload_url('/groupupload/%s/%s' % (group_id, name))
        self.render('grouppage.html', group=group, records=records, members=members, member=member, upload_url=upload_url, creator=creator, 
                    comments=comments, avatar=avatar, user = user)
    def post(self, group_id, name):
        content = self.request.get('content')
        if content:
            user = self.get_user()
                
            submitter = user['username']
            user_id = user['model_id']
            
            c = GroupComment(content = content, submitter = submitter, group_id=int(group_id), user_id = user_id)
            c.put()
            group_comment_cache(int(group_id), True)
            
        self.redirect('/groups/%s/%s' % (group_id, name))

#this lets users join a group
class JoinGroup(BlogHandler):
    def get(self, group_id, name):
        user = self.get_user()       
        
        if group_id not in user['groups']:
            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0] 
            
            currentregistereduser.groups.append(int(group_id))
            currentregistereduser.put()
            
#            can't serialize a list and then put it into the currentuser object
#            currentregistereduser.created = None
#            currentregistereduser.last_modified = None
#            currentregistereduser.avatar = None
#            currentregistereduser.groups = json.dumps(currentregistereduser.groups)
#            self.session['_current_user'] = currentregistereduser.to_dict()
            
            group_member_cache(group_id, True)
        
        self.redirect('/groups/%s/%s' % (group_id, name))
        
class LeaveGroup(BlogHandler):
    def get(self, group_id, name):
        user = self.get_user()      
        
        if int(group_id) in user['groups']:
            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0] 
            
            currentregistereduser.groups.remove(int(group_id))
            currentregistereduser.put()
            
            currentregistereduser.created = None
            currentregistereduser.last_modified = None
            currentregistereduser.avatar = None
            self.session['_current_user'] = currentregistereduser.to_dict()
            
            group_member_cache(group_id, True)
        
        self.redirect('/groups')
        
class GroupUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, group_id, name):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        blobRef = blob_info.key()
        group = Group.get_by_id(int(group_id))
        group.avatar = blobRef
        group.put()
        group_cache(True)
        self.redirect('/groups/%s/%s' % (group_id, name)) 
        
class DeleteGroup(BlogHandler):
    #this should probably be a post
    def get(self, group_id, name):        
        user = self.get_user()
        
        group = Group.get_by_id(int(group_id))
        if user['model_id'] == group.user_id:
            records = Record.query(Record.groups == int(group_id))
            for record in records:
                record.groups.remove(int(group_id))
                record.put()
                individual_record_cache(record.key.id(), True)
            record_cache(True)
            
            group_users = User.query(User.groups == int(group_id))
            for a_user in group_users:
                a_user.groups.remove(int(group_id))
                a_user.put()
            
            group_comments = GroupComment.query(GroupComment.group_id == int(group_id))
            for comment in group_comments:
                comment.key.delete()
            
            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0]
            
            currentregistereduser.created = None
            currentregistereduser.last_modified = None
            currentregistereduser.avatar = None
            self.session['_current_user'] = currentregistereduser.to_dict()
            
            group.key.delete()
            group_cache(True)
            
            self.render('deletesuccess.html', user = user)
        else:
            self.render('noaccess.html', user = user)