#!/usr/bin/env python

'''
issue #42: test some code to replace the use of urllib2
'''

import urllib2
import json
#import requests
import requests.packages.urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning


url_commits = 'https://api.github.com/repos/prjemian/punx/commits'
text = urllib2.urlopen(url_commits).read()
buf = json.loads(text)

url = u'https://github.com/prjemian/punx/archive/master.zip'
u = urllib2.urlopen(url)
content = u.read()

print len(buf), len(content)
# prints: 30 4050903


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
r = requests.get(url_commits, verify=False)
print r.status_code
# prints: 200