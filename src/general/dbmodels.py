#this document has all of my database models

from google.appengine.ext import db
from google.appengine.ext import ndb
from pagehandlers.basehandler import render_str

class Comment(ndb.Model):
    content = ndb.TextProperty(required = True, indexed=False)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    submitter = ndb.StringProperty(required = True)
    user_id = ndb.IntegerProperty()
    postid = ndb.StringProperty(required = True)
    
    upvotes = ndb.IntegerProperty(required = True)
    downvotes = ndb.IntegerProperty(required = True)
    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("comment.html", c = self)

class RecordComment(ndb.Model):
    content = ndb.TextProperty(required = True, indexed=False)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)
    submitter = ndb.StringProperty(required = True)
    user_id = ndb.IntegerProperty()
    keyid = ndb.StringProperty(required = True)
    
    upvotes = ndb.IntegerProperty(required = True)
    downvotes = ndb.IntegerProperty(required = True)
    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("comment.html", c = self)
    
class LocationUpdate(ndb.Model):
    content = ndb.TextProperty(required = True, indexed=False)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)
    submitter = ndb.StringProperty(required = True)
    user_id = ndb.IntegerProperty()
    location_id = ndb.StringProperty(required = True)
    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("comment.html", c = self)

class GroupComment(ndb.Model):
    content = ndb.TextProperty(required = True, indexed=False)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)
    submitter = ndb.StringProperty(required = True)
    user_id = ndb.IntegerProperty()
    group_id = ndb.IntegerProperty(required = True)
    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("comment.html", c = self)
    
#this is the User database class
class User(ndb.Model):
    name = ndb.StringProperty()
    username = ndb.StringProperty()
    theid = ndb.StringProperty()
    model_id = ndb.IntegerProperty()
    email = ndb.StringProperty()
    bio = ndb.StringProperty()
    medals = ndb.IntegerProperty()
    prestige = ndb.IntegerProperty()
    quote = ndb.StringProperty()
    avatar = ndb.BlobKeyProperty()
    todolist = ndb.IntegerProperty(repeated = True)
    groups = ndb.IntegerProperty(repeated = True)
    geo_center = ndb.StringProperty()

    spam = ndb.IntegerProperty()
    spamComfirmed = ndb.BooleanProperty()
    visits = ndb.IntegerProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)
    admin = ndb.BooleanProperty()

#this is the Post database class
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    submitter = db.StringProperty(required = True)
    user_id = db.IntegerProperty()
    
    category = db.StringProperty(required = True)
    element = db.StringProperty(required = True)
    sport = db.StringProperty(required = True)
    cattype = db.StringProperty(required = True)
    
    comments = db.IntegerProperty(required = True)
    upvotes = db.IntegerProperty(required = True)
    downvotes = db.IntegerProperty(required = True)
    ranking = db.IntegerProperty()
    spam = db.IntegerProperty()
    spamComfirmed = db.BooleanProperty()
    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)
    def render_front(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("postfront.html", p = self)
    def render_admin(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("admin_post.html", p = self)

class Location(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)
    title = ndb.StringProperty(required = True)
    locationtype = ndb.StringProperty(required = True)
    description = ndb.TextProperty(required = True)
    ratingCount = ndb.IntegerProperty(required = True)
    rating = ndb.FloatProperty(required = True)
    GPSlocation = ndb.StringProperty(required = True)
    user_id = ndb.IntegerProperty(required = True)
    Long = ndb.FloatProperty(required = True)
    Lat = ndb.FloatProperty(required = True)
    website = ndb.StringProperty()
    postsport = ndb.StringProperty(repeated=True)
    Area = ndb.FloatProperty()
    recordRefs = ndb.IntegerProperty(repeated=True)
    updateRefs = ndb.IntegerProperty(repeated=True)
    todoCount = ndb.IntegerProperty()
    incorrect_location = ndb.IntegerProperty()
    spam = ndb.IntegerProperty()
    spamComfirmed = ndb.BooleanProperty()

    def render(self):
        self._render_text = self.description.replace('\n', '<br>')
        return render_str("location.html", loc = self)  
    def render_front(self):
        self._render_text = self.description.replace('\n', '<br>')
        return render_str("locationfront.html", loc = self) 
    def render_share(self):
        self._render_text = self.description.replace('\n', '<br>')
        return render_str("locationshare.html", loc = self)

class Record(ndb.Model):
    whatdidyoudo = ndb.TextProperty(required = True)
    howwasit = ndb.TextProperty(required = True)
    title = ndb.StringProperty(required = True)
    GPSlocation = ndb.StringProperty(required = True)
    location_id = ndb.IntegerProperty(required = True)
    location_title = ndb.StringProperty(required = True)
    postsport = ndb.StringProperty(required = True)
    rating = ndb.IntegerProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    submitter = ndb.StringProperty(required = True)
    user_id = ndb.IntegerProperty()
    blobRefs = ndb.BlobKeyProperty(repeated=True)
    equipment = ndb.StringProperty()
    difficulty = ndb.IntegerProperty()
    groups = ndb.IntegerProperty(repeated = True)
    group_names = ndb.StringProperty(repeated = True)
    exceptional = ndb.IntegerProperty(required = True)
    informative = ndb.IntegerProperty(required = True)
    entertaining = ndb.IntegerProperty(required = True)
    tags = ndb.StringProperty(repeated = True)
    spam = ndb.IntegerProperty()
    spamComfirmed = ndb.BooleanProperty()
        
    def render(self):
        self._render_text = self.whatdidyoudo.replace('\n', '<br>')
        return render_str("record.html", r = self)
    
    def render_front(self):
        self._render_text = self.whatdidyoudo.replace('\n', '<br>')
        return render_str("recordfront.html", r = self)
    
class Group(ndb.Model):
    description = ndb.TextProperty(required = True)
    name = ndb.StringProperty(required = True)
    postsport = ndb.StringProperty(repeated = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    public = ndb.BooleanProperty(required = True)
    user_id = ndb.IntegerProperty(required = True)
    creator = ndb.StringProperty(required = True)
    recordCount = ndb.IntegerProperty(required = True)
    avatar = ndb.BlobKeyProperty()
    GPSlocation = ndb.StringProperty()
    spam = ndb.IntegerProperty()
    spamComfirmed = ndb.BooleanProperty()
    lat = ndb.FloatProperty()
    lng = ndb.FloatProperty()


#this is the mechanism for preventing duplicate voting
class Vote(db.Model):
    vote_record = db.StringProperty() # just simply seeing if this user has voted before
    
############# database models end here #############