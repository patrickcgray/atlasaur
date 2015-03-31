#this has everything relating to records and adventures (which are the same thing)

#external imports
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers


import string
import logging
import time
from operator import attrgetter

from geopy import geocoders 
from geopy import distance
from geopy import point

#internal imports
from basehandler import BlogHandler
from general.dbmodels import User
from general.dbmodels import Group
from general.dbmodels import Record
from general.dbmodels import RecordComment
from general.dbmodels import Location
from general.dbmodels import Vote
from general.memcache import record_cache
from general.memcache import individual_location_cache
from general.memcache import group_record_cache
from general.memcache import individual_record_cache
from general.memcache import exployrer_cache
from general.memcache import location_cache
from general.memcache import profile_record_cache
from general.memcache import record_comment_cache
from general.memcache import profile_todo_cache


#this lets users add a new record to a location           
class AddAdventure(BlogHandler):
    def get(self, keyid, title):
        user = self.get_user()
        if user:
            location = individual_location_cache(keyid)
            
            groups = None
            if user['groups']:
                logging.error(user['groups'])
                groups = []
                for group in user['groups']:
                    logging.error(user['groups'])
                    groups.append(Group.get_by_id(int(group)))
            
            self.render("addadventure.html", user=user, groups=groups, location=location)
        else:
            self.render('pleaselogin.html')
    def post(self, keyid, title):
        #if the user is adding a new Record
        whatdidyoudo = self.request.get('whatdidyoudo')
        title = self.request.get('title')
        GPSlocation = self.request.get('GPSlocation')
        postsport = self.request.get('postsport')
        rating = self.request.get('rating')
        location_id = self.request.get('location_id')
        location_title = self.request.get('location_title')
        howwasit = self.request.get('howwasit')
        equipment = self.request.get('equipment')
        difficulty = self.request.get('difficulty')
        tags = self.request.get('tags')
        group_tag = self.request.get('group_tag')
        
        #some of the imported GPS coordinated had a strange character in them
        filter(lambda x: x in string.printable, GPSlocation)
        
        
        user = self.get_user()
            
        submitter = user['username']
        user_id = user['model_id']
        
        title = str(title)
        title = title.replace(' ', '25fdsa67ggggsd5')
        title = ''.join(e for e in title if e.isalnum())
        title = title.replace('25fdsa67ggggsd5', '-')
                
        if whatdidyoudo and submitter and user_id and title and GPSlocation and location_id and location_title and postsport and rating and howwasit:
            if not equipment:
                equipment = None
            if not difficulty:
                difficulty = None
            else:
                difficulty = int(difficulty)
            record_db = Record(
                    whatdidyoudo=whatdidyoudo,
                    submitter=submitter,
                    user_id=user_id, 
                    groups = [],
                    title=title,
                    GPSlocation = GPSlocation,
                    location_id = int(location_id),
                    location_title = location_title,
                    postsport = postsport,
                    rating = int(rating),
                    howwasit = howwasit,
                    equipment = equipment,
                    difficulty = difficulty,
                    exceptional = 0,
                    informative = 0,
                    entertaining = 0
                    )
            if group_tag != "choose" and group_tag:
                record_db.groups.append(int(group_tag))
                group = Group.get_by_id(int(group_tag))
                record_db.group_names.append(group.name)              
            if tags:
                record_db.tags = tags.split(', ')
            else:
                record_db.tags = []
            record_db.put()
            
            keyid=str(record_db.key.id())
            
            location = Location.get_by_id(int(location_id))
            
            location.ratingCount = location.ratingCount + 1
            location.rating = float((location.rating * (location.ratingCount-1) + float(rating))/location.ratingCount)
            location.recordRefs.append(int(keyid))
            location.postsport.append(postsport)
            
            location.put()
            
            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0]
            
            try:
                currentregistereduser.todolist.remove(int(location_id))
            except ValueError:
                location_id=location_id
            
            currentregistereduser.prestige = currentregistereduser.prestige + 4
            currentregistereduser.put()
            
            #for some reason this is giving an error because the currentregistereduser.group property isn't json serilizable
#            currentregistereduser.created = None
#            currentregistereduser.last_modified = None
#            currentregistereduser.avatar = None
#            self.session['_current_user'] = currentregistereduser.to_dict()

            exployrer_cache(True)
            individual_location_cache(location_id, True)
            individual_record_cache(keyid, True)
            location_cache(True)
            record_cache(True)

            if group_tag != "choose" and group_tag:
                group = Group.get_by_id(int(group_tag))
                group.recordCount = group.recordCount + 1
                group.put()
                group_record_cache(int(group_tag), True)
            
            self.redirect('/record/%s/%s' % (keyid, title))
                    
        else:
            whatdidyoudo = self.request.get('whatdidyoudo')
            title = self.request.get('title')
            postsport = self.request.get('postsport')
            rating = self.request.get('rating')
            location_title = self.request.get('location_title')
            howwasit = self.request.get('howwasit')
            equipment = self.request.get('equipment')
            difficulty = self.request.get('difficulty')
            group_tag = self.request.get('group_tag')
            
            location = individual_location_cache(keyid)
            
            error = "Hey Chief you'll need to fill out every field along with a location."                    
            self.render('addadventure.html', user = user, whatdidyoudo=whatdidyoudo, howwasit=howwasit, location=location, equipment=equipment,
                        submitter=submitter, user_id=user_id, title=title, GPSlocation = GPSlocation, postsport = postsport, rating = rating, error=error)

#this lets the user find the location to add a new adventure
class ShareAdventure(BlogHandler):
    def get(self):
        inputlocation = self.request.get("location")
        radius = self.request.get("radius")
        locations = location_cache()
        records = record_cache()
        records = records[:10]
        GPSlocation = None
        error=None
        locations_to_render = None
        
        search = False
        if inputlocation:        
            g = geocoders.GoogleV3()
            searched_location = None
            #to catch an error where there is no corresponding location
            try:
                #to catch an error where there are multiple returned locations
                try:
                    place, (lat, lng) = g.geocode(inputlocation)
                    place, searched_location = g.geocode(inputlocation)
                except ValueError:
                    geocodespot = g.geocode(inputlocation, exactly_one=False)
                    place, (lat, lng) = geocodespot[0]
                    place, searched_location = geocodespot[0]
                GPSlocation = "("+str(lat)+", "+str(lng)+")"
                
                locations = location_cache()
                new_locations = []                   
                for location in locations:
                    distance.distance = distance.GreatCircleDistance
                    location_distance = distance.distance(searched_location, point.Point(location.Lat, location.Long)).miles
                    #make this 20 a variable that the user can set and have it be 10, 25, 50, 100, 200
                    if location_distance < int(radius):
                        new_locations.append(location)
                locations_to_render = new_locations
                search=True
                locations_to_render = locations_to_render[:15]
            #this is straight from the docs:  http://code.google.com/p/geopy/wiki/Exceptions and happens when there is no location that matches
            except geocoders.google.GQueryError:
                error = "We cannot find " + inputlocation +"... try to be a little more specific or increase the search area."
                
        user = self.get_user()
        self.render('shareadventure.html', locations=locations, radius=radius, centerlocation=GPSlocation, records=records, locations_to_render=locations_to_render, error=error, user = user, search=search)

#this lets the user delete a record            
class DeleteRecord(BlogHandler):
    #this should probably be a post
    def get(self, record_id, title):        
       
        user = self.get_user()
        
        record = Record.get_by_id(int(record_id))
        if user['model_id'] == record.user_id:
            location_id = record.location_id
            location = Location.get_by_id(int(record.location_id))
            location.recordRefs.remove(int(record_id))
            location.put()
            individual_location_cache(location_id, True)
            comments = RecordComment.query(RecordComment.keyid == record_id).order(RecordComment.created)
            for comment in comments:
                comment.key.delete()
            record.key.delete()
            
            individual_record_cache(record_id, True)
            profile_record_cache(user['model_id'], True)
            record_cache(True)
            self.render('deletesuccess.html', user = user)
        else:
            self.render('noaccess.html', user = user)

#this takes the user to a new page and lets them edit the record   
class EditRecord(BlogHandler):
    #this should probably be a post
    def get(self, record_id, title):        
       
        user = self.get_user()
        
        record = Record.get_by_id(int(record_id))
        if user['model_id'] == record.user_id:
            unsplit_tags = None
            if record.tags:
                unsplit_tags = ', '.join(record.tags)
            self.render('editrecord.html', record=record, unsplit_tags=unsplit_tags, user = user)
        else:
            self.render('noaccess.html', user = user)
    def post(self, record_id, title):
        whatdidyoudo = self.request.get('whatdidyoudo')
        howwasit = self.request.get('howwasit')
        postsport = self.request.get('postsport')
        rating = self.request.get('rating')
        tags = self.request.get('tags')
        equipment = self.request.get('equipment')
        difficulty = self.request.get('difficulty')
        
        user = self.get_user()
                      
        if postsport and rating and difficulty:
            record = Record.get_by_id(int(record_id))
            record.whatdidyoudo = whatdidyoudo
            record.howwasit = howwasit
            record.postsport=postsport
            record.rating = int(rating)
            record.tags = tags.split(', ')
            record.equipment = equipment
            record.difficulty = int(difficulty)
            
            record.put()
            
            #I should probably recalculate the whole location rating here as well
            individual_record_cache(record_id, True)
            profile_record_cache(record.user_id, True)
            record_cache(True)
            
            self.redirect('/record/%s/%s' % (record_id, title))
                    
        else:
            whatdidyoudo = self.request.get('whatdidyoudo')
            postsport = self.request.get('postsport')
            rating = self.request.get('rating')
        
            error = "Hey Chief you'll need to fill out every field."                    
            record = Record.get_by_id(int(record_id))
            
            self.render('editrecord.html', record=record, error=error, unsplit_tags=', '.join(record.tags), user = user)
            
#this is the permalink for all records
class RecordPage(BlogHandler):
    def get(self, keyid, title):
        record = individual_record_cache(keyid)
        upload_url = blobstore.create_upload_url('/upload/%s' % (keyid))
        photos = []
        for blobRef in record.blobRefs:
            photos.append(images.get_serving_url(blobRef, size=None, crop=False, secure_url=None))
                
        recordcomments = record_comment_cache(keyid)
        
        profile_id = record.user_id
                
        user = self.get_user()
        
        owner = False
        if user:
            if profile_id == user['model_id']:
                owner=True          
                
        groups = None
        if record.groups:
            groups = []
            for group in record.groups:
                groups.append(Group.get_by_id(int(group)))
                
             
        self.render("recordpermalink.html", user=user, record=record, recordcomments=recordcomments, owner=owner,
                    groups=groups, photos=photos, upload_url=upload_url, keyid=keyid)
        
    def post(self, keyid, title):
        content = self.request.get('content')
        entertaining = self.request.get('entertaining')
        exceptional = self.request.get('exceptional')
        informative = self.request.get('informative')
        
        if content:
            user = self.get_user()
                
            submitter = user['username']
            user_id = user['model_id']
            
            c = RecordComment(content = content, submitter = submitter, keyid=keyid, upvotes = 0, downvotes = 0, user_id = user_id)
            c.put()
            record_comment_cache(keyid, True)
            
            self.redirect('/record/%s/%s' % (keyid, title))
            
        elif exceptional or entertaining or informative:
            user = self.get_user()
            user_id = user['model_id']
            
            keyname = str(user_id) + "-" + str(keyid) + "-record_adjective"
            vote_record = Vote.get_by_key_name(keyname)
            if vote_record != None:
                self.redirect('/record/%s/%s' % (keyid, title))
            else:
                vote_record = Vote.get_or_insert(keyname, value=str(user_id))
                record = Record.get_by_id(int(keyid))
                if exceptional:
                    record.exceptional = record.exceptional + 1
                if entertaining:
                    record.entertaining = record.entertaining + 1
                if informative:
                    record.informative = record.informative + 1
                #do the others
                record.put()  
                      
                individual_record_cache(int(record.key.id()), True)
                
                self.redirect('/record/%s/%s' % (keyid, title)) 
            
        else:
            record = individual_record_cache(keyid)
            upload_url = blobstore.create_upload_url('/upload/%s' % (keyid))
            photos = []
            for blobRef in record.blobRefs:
                photos.append(images.get_serving_url(blobRef, size=None, crop=False, secure_url=None))
            
            recordcomments = record_comment_cache(keyid)
                
            error = "Hey boss we're gonna need a some content if you want to submit something."
            self.render("recordpermalink.html", error=error, record=record, recordcomments=recordcomments, user=user, photos=photos, upload_url=upload_url, keyid=keyid)


#puts a new record on a user's ToDo List          
class AddToDo(BlogHandler):
    def get(self, location_id, title):        
        user = self.get_user()
        
        contains = False
        for item in user['todolist']:
            if int(location_id) == int(item):
                contains = True
        if contains == False:
            location = Location.get_by_id(int(location_id))
            if location:
                location.todoCount = location.todoCount + 1
                location.put()
                
                user_db_qry = User.query(User.theid == user['theid'])
                user_db_list = user_db_qry.fetch(1)
                currentregistereduser = user_db_list[0]
                
                currentregistereduser.todolist.append(int(location_id))
                currentregistereduser.put()   
                user_id = currentregistereduser.key.id()   
                profile_todo_cache(user_id, update = True)
        
        self.redirect("/location/%s/%s" % (location_id, title))
        
#this lets users upload photos
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, record_id):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        blobRef = blob_info.key()
        record = Record.get_by_id(int(record_id))
        record.blobRefs.append(blobRef)
        record.put()
        individual_record_cache(record_id, True)
        record_cache(True)
        profile_record_cache(True)
        self.redirect('/record/%s/%s' % (record_id, record.title))
        
class RecentRecords(BlogHandler):
    def get(self):
        records = record_cache()
        user = self.get_user()
        
        self.render("recentrecords.html", records=records, user=user)
        
class RecentLocalRecords(BlogHandler):
    def get(self, GPSlocation):
        latlng = (GPSlocation).split(",")
        lat = float(latlng[0][1:])
        lng = float(latlng[1][1:-1])
        
        records_to_render = []
        
        records = record_cache()                   
        for record in records:
            rec_latlng = (record.GPSlocation).split(",")
            rec_lat = float(rec_latlng[0][1:])
            rec_lng = float(rec_latlng[1][1:-1])
            
            distance.distance = distance.GreatCircleDistance
            location_distance = distance.distance(point.Point(lat, lng), point.Point(rec_lat, rec_lng)).miles
            #make this 20 a variable that the user can set and have it be 10, 25, 50, 100, 200
            if location_distance < int(100):
                records_to_render.append(record)
        
        records_to_render = records_to_render[:20]
        
        #as long as they exist pass them in to the template as records
        if records_to_render:
            records = records_to_render

        user = self.get_user()
        
        self.render("recentrecords.html", records=records, user=user)