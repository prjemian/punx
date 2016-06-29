#!/usr/bin/env python

'''
issue #42: test some code to replace the use of urllib2
'''

# import urllib2
# import json
#import requests
import requests.packages.urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import StringIO
import zipfile


url_commits = 'https://api.github.com/repos/nexusformat/definitions/commits'
url_zip = u'https://github.com/nexusformat/definitions/archive/master.zip'


# requests.exceptions.ConnectionError
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
r = requests.get(url_commits, verify=False)
print r.status_code
# prints: 200

latest = r.json()[0]

sha = latest['sha']
iso8601 = latest['commit']['committer']['date']
print latest


content = requests.get(url_zip).content
buf = StringIO.StringIO(content)
zip_content = zipfile.ZipFile(buf)

print len(zip_content.namelist())
print zip_content.namelist()
