#this page has everything to do with posts and their creation and handling

#imports from external projects
from google.appengine.ext import db
from google.appengine.api import memcache
import micawber
import logging

#imports from within the project
from basehandler import BlogHandler
from general.memcache import main_cache
from general.memcache import ranked_cache
from general.memcache import daily_ranked_cache
from general.memcache import exployrer_cache
from general.memcache import profile_cache
from general.memcache import comment_cache
from general.memcache import admin_cache
from general.dbmodels import User
from general.dbmodels import Post
from general.dbmodels import Comment
from general.dbmodels import Vote

#this is the patent key for the Post dbmodel
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

#this page has all of the posts and is under the Discuss tab
class Posts(BlogHandler):
    def get(self):
        #post list
        posts = main_cache()
        posts = posts[:21]
        current_user=None

        user = self.get_user()
        
        self.render('posthome.html', user = user, current_user=user, posts = posts)
                    
            
    def post(self):
        global posts
             
        subject = self.request.get('subject')
        content = self.request.get('content')
            
        postsport = self.request.get('postsport')
        postelement = "general"
            
                
        #this need to be taken out
        if postsport in ("sailing", "diving", "surfing", "kiteboarding", "kayaking", "general sea"):
            postelement ="sea"   
                
        elif postsport in ("skydiving", "paragliding", "hanggliding", "basejumping", "powered flight", "general air"):
            postelement ="air"
                
        elif postsport in ("rockclimbing", "hiking", "camping" "biking", "skiing", "snowboarding", "general land"):
            postelement ="land"
        elif postsport == "admin":
            postsport = "admin"
            postelement = "general"
        else:
            postelement="general"
            postsport = "general"
    
        if subject and content and content != '{{content}}':
            user = self.get_user()
                
            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0]
            
            submitter = currentregistereduser.username
            theid = currentregistereduser.theid
            user_id = currentregistereduser.key.id()
            
            subject = str(subject)
            subject = subject.replace(' ', '25fdsa67ggggsd5')
            subject = ''.join(e for e in subject if e.isalnum())
            subject = subject.replace('25fdsa67ggggsd5', '-')
            
            p = Post(parent = blog_key(), subject = subject, content = content, submitter = submitter, category="post", 
                     element=postelement, sport=postsport, cattype="tbd", comments = 0, upvotes = 0, downvotes = 0, user_id = user_id, ranking = 0)
            p.put()
            
            currentregistereduser.prestige = currentregistereduser.prestige + 2
            currentregistereduser.put()
                        
            ranked_cache(True)
            daily_ranked_cache(True)
            exployrer_cache(True)
            posts = main_cache(True)
            profile_cache(user_id, True)
            if postsport=="admin":
                admin_cache(True)
                
            keyid=str(p.key().id())
            
            self.redirect('/post/%s/%s' % (keyid, subject))
                                              
        #need to find the root problem
        else:
            user = self.get_user()
            
            error = "Hey boss we're gonna need a subject and some content."
            self.render("posthome.html", subject=subject, content=content, error=error, user=user)

#the following six pages are pretty self explainatory
class TopRanked(BlogHandler):   
    def get(self):
        posts = ranked_cache()
        title = 'All Time Greatest Posts'
        user = self.get_user()
        self.render('sport.html', user = user, posts=posts, title=title)

class HotPosts(BlogHandler):   
    def get(self):
        posts = daily_ranked_cache()
        title = 'Hot Posts'
        user = self.get_user()       
        self.render('sport.html', user = user, posts=posts, title=title)
        
class Air(BlogHandler):   
    def get(self, *args, **kwargs):
        activity = kwargs.get("activity")
        if activity in ("skydiving", "paragliding", "hanggliding", "basejumping", "powered flight"):
            posts = db.GqlQuery("select * from Post where sport=:1 order by created desc limit 30", activity)
            title = activity
        else:
            posts = db.GqlQuery("select * from Post where element=:1 order by created desc limit 30", "air")
            title = "air"
        user = self.get_user()       
        self.render('sport.html', user = user, posts=posts, title=title)

class Sea(BlogHandler):   
    def get(self, *args, **kwargs):
        activity = kwargs.get("activity")
        if activity in ("sailing", "kayaking", "kiteboarding", "surfing", "diving"):
            posts = db.GqlQuery("select * from Post where sport=:1 order by created desc limit 30", activity)
            title = activity
        else:
            posts = db.GqlQuery("select * from Post where element=:1 order by created desc limit 30", "sea")
            title = "sea"
        user = self.get_user()       
        self.render('sport.html', user = user, posts=posts, title=title)
        
class Land(BlogHandler):   
    def get(self, *args, **kwargs):
        activity = kwargs.get("activity")
        if activity in ("rockclimbing", "hiking", "camping", "biking", "skiing", "snowboarding"):
            posts = db.GqlQuery("select * from Post where sport=:1 order by created desc limit 30", activity)
            title = activity
        else:
            posts = db.GqlQuery("select * from Post where element=:1 order by created desc limit 30", "land")
            title = "land"
        user = self.get_user()      
        self.render('sport.html', user = user, posts=posts, title=title)
        
#lets the user delete a post        
class DeletePost(BlogHandler):
    #this should probably be a post
    def get(self, post_id, subject):        
       
        user = self.get_user()
        
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        key = str(key)
        post = db.get(key)
        if user['model_id'] == post.user_id:
            comments = Comment.query(Comment.postid == post_id).order(Comment.created)
            for comment in comments:
                comment.key.delete()
            post.delete()
            
            main_cache(True)
            ranked_cache(True)
            daily_ranked_cache(True)
            profile_cache(user['model_id'], True)
            self.render('deletesuccess.html', user = user)
        else:
            self.render('noaccess.html', user = user)

#lets user edit a post          
class EditPost(BlogHandler):
    #this should probably be a post
    def get(self, post_id, subject):        
       
        user = self.get_user()
        
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        key = str(key)
        post = db.get(key)
        if user['model_id'] == post.user_id:
            self.render('editpost.html', subject=post.subject, post=post, content = post.content, user = user)
        else:
            self.render('noaccess.html', user = user)
    def post(self, post_id, title):
        content = self.request.get('content')
        subject = self.request.get('subject')
        postsport = self.request.get('postsport')
                      
        if content and subject and postsport:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            key = str(key)
            post = db.get(key)
            post.content = content
            post.subject = subject
            post.postsport = postsport
            
            post.put()
            
            #I should probably recalculate the whole location rating here as well
            
            main_cache(True)
            ranked_cache(True)
            daily_ranked_cache(True)
            profile_cache(post.user_id, True)
            memcache.set(key, post)
            
            
            self.redirect('/post/%s/%s' % (post_id, title))
                    
        else:
            content = self.request.get('content')
            subject = self.request.get('subject')
        
            user = self.get_user()
            error = "Hey Chief you'll need to fill out every field."                    
            self.render('editpost.html', user = user, error=error, content=content, subject=subject)
            
#this is the page where posts from Discuss are rendered
class PostPage(BlogHandler):
    def get(self, post_id, subject):
        #why did I do this here instead of just using the regular post_id?
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        key = str(key)
        post = memcache.get(key)
        if post is None:
            logging.error('DB QUERY')
            post = db.get(key)
            memcache.set(key, post)
            
        if not post:
            self.error(404)
            return   
        
        comments = comment_cache(post_id)
        user = self.get_user()
        
        try:
            providers = micawber.bootstrap_embedly()     
            urls, data = micawber.parsers.extract(post.content, providers)
            mic_content = None
            for url in urls:
                mic_content = micawber.parse_text_full(url, providers, urlize_all=False, maxwidth="700px")
                break
            if mic_content:
                if mic_content[:4] == "http":
                    mic_content = None 
        except KeyError:
            #I would like to change this so that it handles it and display it
            mic_content = None
        
        owner = False
        if user:
            if user['model_id'] == post.user_id:
                owner=True
             
        self.render("permalink.html", post = post, user=user, comments=comments, owner=owner, mic_content = mic_content)
        
    def post(self, post_id, subject):
        user = self.get_user()
        if user:
            content = self.request.get('content')
            vote = self.request.get("vote")
                
            submitter = user['username']
            user_id = user['model_id']
            
            if content:
                key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                key = str(key)
                
                c = Comment(content = content, submitter = submitter, postid = post_id, upvotes = 0, downvotes = 0, user_id = user_id)
                c.put()
                comment_cache(post_id, True)
                post_id = int(post_id)
                post = Post.get_by_id(post_id, parent=blog_key())
                post.comments = post.comments + 1
                post.ranking = (post.comments * 4) + (post.upvotes * 2) - post.downvotes
                post.put()
                memcache.set(key, post)
                main_cache(True)
                ranked_cache(True)
                daily_ranked_cache(True)
                self.redirect('/post/%s/%s' % (post_id, subject))
            elif vote:
                keyname = str(user_id) + "-" + str(post_id) + "-post"
                vote_record = Vote.get_by_key_name(keyname)
                if vote_record != None:
                    self.redirect('/post/%s/%s' % (post_id, subject))
                else:
                    vote_record = Vote.get_or_insert(keyname, value=str(user_id))
                    
                    # i can make this more efficient or at least more consistent
                    key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                    key = str(key)
                    post_id = int(post_id)
                    if vote == "upvote":
                        post = Post.get_by_id(post_id, parent=blog_key())
                        post.upvotes = post.upvotes + 1
                        post.ranking = (post.comments * 4) + (post.upvotes * 2) - post.downvotes
                        post.put()
                        memcache.set(key, post)
                        #add this
                        #user.prestige = user.prestige + 1    
                        #user.put()                     
                        #exployrer_cache(True)
                        main_cache(True)
                        ranked_cache(True)
                    elif vote == "downvote":
                        post = Post.get_by_id(post_id, parent=blog_key())
                        post.downvotes = post.downvotes + 1
                        post.ranking = (post.comments * 4) + (post.upvotes * 2) - post.downvotes
                        post.put()
                        memcache.set(key, post)
                        #add this
                        #user.prestige = user.prestige - 1
                        #user.put()           
                        #exployrer_cache(True)
                        main_cache(True)
                        ranked_cache(True)
                    daily_ranked_cache(True)
                    post_id = str(post_id)
                    self.redirect('/post/%s/%s' % (post_id, subject))
            else:                    
                error = "Hey boss we're gonna need a some content or a vote if you want to submit something."
                self.render("permalink.html", post=post, error=error, user=user)
        else:
            self.redirect('/post/%s/%s' % (post_id, subject))