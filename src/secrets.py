# Copy this file into secrets.py and set keys, secrets and scopes.

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here: 
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = "d84z35y3831wi478e5k9md2j9qvdmi6nvif4t6f266085anc46"

# Google APIs
GOOGLE_APP_ID = '832003742789.apps.googleusercontent.com'
GOOGLE_APP_SECRET = 'GL0-XJjZ8PvcjHS-eOZjSoSD'

# Facebook auth apis
FACEBOOK_APP_ID = '273763239402074'
FACEBOOK_APP_SECRET = '95d0cf6c2e48eb384663d2f7b91532a1'

# https://www.linkedin.com/secure/developer
LINKEDIN_CONSUMER_KEY = 'd0egv1dos8f1'
LINKEDIN_CONSUMER_SECRET = 'FOtbJjJDlbTDTitY'

# https://manage.dev.live.com/AddApplication.aspx
# https://manage.dev.live.com/Applications/Index
WL_CLIENT_ID = '00000000480E6996'
WL_CLIENT_SECRET = 'BCdCVLkrxhfC4T3cs-pwu0Chto1iOEU4'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = 'su3p7hycs0dRnqDMYEpLw'
TWITTER_CONSUMER_SECRET = 'Pqf2Dcrw9ggskmtNnBDdeg1wuibxClpt1ZPrbGz5eA'

# config that summarizes the above
AUTH_CONFIG = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
                  'https://www.googleapis.com/auth/userinfo.profile'),
  'facebook'    : (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                  'user_about_me'),
  'windows_live': (WL_CLIENT_ID, WL_CLIENT_SECRET,
                  'wl.signin'),

  # OAuth 1.0 providers don't have scopes
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
  'linkedin'    : (LINKEDIN_CONSUMER_KEY, LINKEDIN_CONSUMER_SECRET),

  # OpenID doesn't need any key/secret
}
