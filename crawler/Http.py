from cookielib import CookieJar, DefaultCookiePolicy
import urllib2

class Http(object):
   def __init__(self):
      self.policy = DefaultCookiePolicy(rfc2965=True, strict_ns_domain=DefaultCookiePolicy.DomainStrict)
      self.cj = CookieJar(self.policy)


   def get(self, url, headers=None):
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
      opener.addheaders = [('User-agent', 'Mozilla/5.0')]
      if headers != None:
         opener.addheaders = headers
      return opener.open(url).read()


   def post(self, url, params, headers=None):
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
      opener.addheaders = [('User-agent', 'Mozilla/5.0')]
      if headers != None:
         opener.addheaders = headers
      return opener.open(url, params).read()
