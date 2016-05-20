
'''
maintain the local cache of NeXus NXDL and XML Schema files
'''

import datetime
import lxml.etree
import os
import StringIO
import sys
import urllib
import zipfile

SOURCE_CACHE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cache'))
GITHUB_ORGANIZATION = 'nexusformat'
GITHUB_REPOSITORY = 'definitions'


def gmt():
    'current ISO8601 time in GMT, matches format from GitHub'
    return 'T'.join(str(datetime.datetime.utcnow()).split()).split('.')[0] + 'Z'


def githubMasterInfo(org, repo):
    '''
    get information about the organization's repository master branch from the HTML page
    
    :returns: dict (as below) or None if could not get info
    
    ========  ================================================
    key       meaning
    ========  ================================================
    datetime  ISO-8601-compatible timestamp
    sha       short (7 character) hash tag of latest commit
    zip       URL of downloadable ZIP file
    ========  ================================================
    '''
    url = 'https://github.com/%s/%s' % (org, repo)
    commit_xpath_str = '//div[@class="commit-tease js-details-container"]'
    sha_xpath_str = '//a[@class="commit-tease-sha"]'
    timestamp_xpath_str = '//relative-time'
    
    def get_node(parent, xpath_str):
        node_list = parent.xpath(xpath_str)
        # raise IndexError if list is empty
        return node_list[0]
    
    text = urllib.urlopen(url).read()
    parser = lxml.etree.HTMLParser()
    tree = lxml.etree.parse(StringIO.StringIO(text), parser)
    
    try:
        commit_node = get_node(tree, commit_xpath_str)
    except IndexError:
        return None
    # print lxml.etree.tostring(commit_node, pretty_print=True)
    sha = get_node(commit_node, sha_xpath_str).text.strip()
    iso8601 = get_node(commit_node, timestamp_xpath_str).attrib['datetime']
    zip_url = url + '/archive/master.zip'
    
    return dict(sha=sha, datetime=iso8601, zip=zip_url)


def updateCache(info, path):
    '''
    download the repository ZIP file and extract the NXDL XML, XSL, and XSD files to the path
    '''
    info_file = os.path.join(path, 'info.txt')
    cache_subdir = os.path.join(path, 'definitions-master')

    cache_info = read_info(info_file)
    if (info['datetime'] <= cache_info['datetime']) and os.path.exists(cache_subdir):
        return
    
    url = info['zip']
    u = urllib.urlopen(url)
    content = u.read()
    buf = StringIO.StringIO(content)
    zip_content = zipfile.ZipFile(buf)
    # How to save this zip_content to disk?
    
    categories = 'base_classes applications contributed_definitions'.split()
    for item in zip_content.namelist():
        parts = item.rstrip('/').split('/')
        if len(parts) == 2:             # get the XML Schema files
            if os.path.splitext(parts[1])[-1] in ('.xsd',):
                zip_content.extract(item, 'cache')
        elif len(parts) == 3:         # get the NXDL files
            if parts[1] in categories:    # the NXDL categories
                if os.path.splitext(parts[2])[-1] in ('.xml .xsl'.split()):
                    zip_content.extract(item, 'cache')
    
    write_info(info, info_file)


def write_info(info, fname):
    '''
    describe the current cache contents in file
    '''
    f = open(fname, 'w')
    f.write('# file: info.txt\n')
    f.write('# written: %s\n' % str(datetime.datetime.now()))
    f.write('# GMT: %s\n\n' % gmt())
    for k, v in info.items():
        f.write('%s: %s\n' % (k, v))
    f.close()


def read_info(fname):
    '''
    read current cache contents from file
    '''
    db = dict(datetime='0')
    if os.path.exists(fname):
        for line in open(fname, 'r').readlines():
            line = line.strip()
            if line.startswith('#'):
                continue
            if len(line) == 0:
                continue
            pos = line.find(': ')
            db[ line[:pos] ] = line[pos+1:]
    return db


def update_NXDL_Cache(path=SOURCE_CACHE_PATH):
    info = githubMasterInfo(GITHUB_ORGANIZATION, GITHUB_REPOSITORY)
    if info is not None:
        updateCache(info, SOURCE_CACHE_PATH)


if __name__ == '__main__':
    update_NXDL_Cache()
