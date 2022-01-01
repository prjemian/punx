#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

"""
Manage the NXDL cache directories of this project.

A key component necessary to validate both NeXus data files and
NXDL class files is a current set of the NXDL definitions.

There are two cache directories:

* the source cache
* the user cache

Within each of these cache directories,
there may be one or more subdirectories, each
containing the NeXus definitions subdirectories and files (``*.xml``,
``*.xsl``, & ``*.xsd``) of a specific branch, release, tag, or commit hash
from the NeXus definitions repository.

:source cache: contains default set of NeXus NXDL files
:user cache: contains additional set(s) of NeXus NXDL files, installed by user

The :mod:`~punx.cache_manager` is called by
:mod:`~punx.main`,
:mod:`~punx.schema_manager`,
and :mod:`~punx.nxdl_manager`.

.. rubric:: Public interface

.. autosummary::

   ~CacheManager


.. rubric:: Internal interface

.. autosummary::

   ~get_short_sha
   ~read_json_file
   ~write_json_file
   ~is_extractable
   ~download_NeXus_zip_archive
   ~download_file_set
   ~table_of_caches
   ~Base_Cache
   ~SourceCache
   ~UserCache
   ~NXDL_File_Set

"""

import datetime
import json
import os
import pathlib
import pyRestTable
import requests
import shutil

from PyQt5 import QtCore
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .__init__ import __settings_organization__, __settings_package__
from . import singletons
from . import utils


logger = utils.setup_logger(__name__)

DOWNLOAD_COMPRESS_FORMAT = "zip"  # or "tar.gz"
DEFAULT_NXDL_SET = "v2018.5"  # most recent file set in source cache
GITHUB_NXDL_BRANCH = "main"
GITHUB_NXDL_ORGANIZATION = "nexusformat"
GITHUB_NXDL_REPOSITORY = "definitions"
INFO_FILE_NAME = u"__github_info__.json"
SHORT_SHA_LENGTH = 7
SOURCE_CACHE_SETTINGS_FILENAME = u"punx.ini"
SOURCE_CACHE_SUBDIR = u"cache"
GITHUB_RETRY_COUNT = 3
URL_BASE = (
    "https://github.com/"
    f"{GITHUB_NXDL_ORGANIZATION}/{GITHUB_NXDL_REPOSITORY}"
    "/archive"
)


def get_short_sha(full_sha):
    """
    return the first few unique characters of the git commit hash (SHA)

    :param str full_sha: hash code from Github
    """
    return full_sha[: min(SHORT_SHA_LENGTH, len(full_sha))]


def write_json_file(filename, obj):
    """
    write the structured ``obj`` to the JSON file ``file_name``

    :see: https://docs.python.org/3.5/library/json.html#json.dumps
    """
    open(filename, "w").write(json.dumps(obj, indent=2))


def read_json_file(filename):
    """
    read a structured object from the JSON file ``file_name``

    :see: https://docs.python.org/3.5/library/json.html#json.loads
    """
    return json.loads(open(filename, "r").read())


def is_extractable(item, allowed_endings, allowed_parents):
    """
    decide if this item should be extracted from the ZIP download.

    :return bool:
    """
    path = pathlib.Path(item)
    return (
        path.suffix in allowed_endings
        and
        path.parent.name in allowed_parents
    )


def download_NeXus_zip_archive(url):
    """
    Download the NXDL definitions described by ``url``.

    Return the downloaded content in memory.
    """
    import io
    import zipfile

    # disable warnings about GitHub self-signed https certificates
    disable_warnings(InsecureRequestWarning)

    for _retry in range(GITHUB_RETRY_COUNT):  # noqa
        try:
            print(f"Requesting download from {url}")
            archive = requests.get(url, verify=False)
            return zipfile.ZipFile(io.BytesIO(archive.content))
        except requests.exceptions.ConnectionError as _exc:
            raise IOError(f"ConnectionError from {url}\n{_exc}")

    return None


def download_file_set(file_set_name, cache_path, replace=False):
    """
    Download & extract NXDL file set into a subdirectory of ``cache_path``.

    file_set_name str :
        Name of the NXDL file_set to be downloaded.
    cache_path obj :
        Directory with NXDL file_sets (instance of ``pathlib.Path``).
        (A file_set is a directory with a version of the NeXus definitions
        repository.)
    replace bool :
        If ``True`` and file set exists, replace it.
        (default: ``False``)

    USAGE::

        download_file_set(file_set_name, cache_path, replace=False)

    """
    NXDL_refs_dir_name = cache_path / file_set_name
    print(f"Downloading file set: {file_set_name} to {NXDL_refs_dir_name} ...")

    if NXDL_refs_dir_name.exists():
        if replace:
            print(f"Replacing existing file set '{file_set_name}'")
        else:
            print(f"File set '{file_set_name}' exists.  Will not replace.")
            return

    url = f"{URL_BASE}/{file_set_name}.{DOWNLOAD_COMPRESS_FORMAT}"

    zip_content = download_NeXus_zip_archive(url)
    if zip_content is None:
        print(f"Could not download file set: {file_set_name}")
        return

    NXDL_categories = "base_classes applications contributed_definitions".split()
    NXDL_file_endings_list = ".xsd .xml .xsl".split()

    download_path = cache_path / zip_content.filelist[0].filename.split("/")[0]
    allowed_parents = NXDL_categories  # directories
    allowed_parents.append(download_path.name)

    item_count = 0
    dt = (1980, 1, 1, 1, 1, 1)  # start with pre-NeXus date
    for item in zip_content.namelist():
        if is_extractable(item, NXDL_file_endings_list, allowed_parents):
            zip_content.extract(item, cache_path)
            dt = max(zip_content.getinfo(item).date_time, dt)
            item_count += 1
            print(f"{item_count} Extracted: {item}")

    if item_count < 2:
        raise ValueError("no NXDL content downloaded")

    ymd_hms = datetime.datetime(
        *dt[:3], hour=dt[3], minute=dt[4], second=dt[5]
    )

    info = dict(
        ref=file_set_name,
        sha=zip_content.comment.decode("utf8"),
        zip_url=url,
        last_modified=ymd_hms.isoformat(sep=" "),
    )
    info["# description"] = "NXDL files downloaded from GitHub repository"
    info["# written"] = str(datetime.datetime.now())
    # TODO: move this code into the NXDL_File_Set class
    infofile = download_path / INFO_FILE_NAME
    write_json_file(infofile, info)
    print(f"Created: {infofile}")

    # last, rename the ``download_path`` directory to ``file_set_name``
    if NXDL_refs_dir_name.exists():
        shutil.rmtree(NXDL_refs_dir_name, ignore_errors=True)
    shutil.move(download_path, NXDL_refs_dir_name)
    print(f"Installed in directory: {NXDL_refs_dir_name}")


def table_of_caches():
    """
    return a pyRestTable table describing all known file sets in both source and user caches

    :returns obj: instance of pyRestTable.Table with all known file sets

    **Example**::

        ============= ====== =================== ======= ==================================================================
        NXDL file set cache  date & time         commit  path
        ============= ====== =================== ======= ==================================================================
        a4fd52d       source 2016-11-19 01:07:45 a4fd52d /home/prjemian/Documents/projects/prjemian/punx/punx/cache/a4fd52d
        v3.3          source 2017-07-12 10:41:12 9285af9 /home/prjemian/Documents/projects/prjemian/punx/punx/cache/v3.3
        v2018.5       source 2018-05-15 16:34:19 a3045fd /home/prjemian/Documents/projects/prjemian/punx/punx/cache/v2018.5
        Schema-3.4    user   2018-05-15 08:24:34 aa1ccd1 /home/prjemian/.config/punx/Schema-3.4
        main          user   2021-12-17 13:09:18 041c2c0 /home/prjemian/.config/punx/main
        ============= ====== =================== ======= ==================================================================

    """
    cm = CacheManager()
    return cm.table_of_caches()


class CacheManager(singletons.Singleton):

    """
    manager both source and user caches

    .. autosummary::

        ~select_NXDL_file_set
        ~find_all_file_sets
        ~cleanup

    """

    def __init__(self):
        self.default_file_set = None
        self.source = SourceCache()
        self.user = UserCache()

        self.NXDL_file_sets = self.find_all_file_sets()
        logger.debug(
            " NXDL_file_sets names = %s",
            sorted(list(self.NXDL_file_sets.keys()))
        )
        try:
            self.select_NXDL_file_set()
        except KeyError:
            pass
        if self.default_file_set is None:
            logger.debug(" CacheManager: no default_file_set selected yet")

        # TODO: update the .ini file as needed (remember the default_file_set value

    # - - - - - - - - - - - - - -
    # public

    def select_NXDL_file_set(self, ref=None):
        """
        Return the named self.default_file_set instance.

        Raise KeyError exception if unknown.

        :return obj:
        """
        logger.debug(" given ref: " + str(ref))

        def sorter(value):
            return self.NXDL_file_sets[value].last_modified

        if ref is None and len(self.NXDL_file_sets) > 0:
            ref = ref or sorted(self.NXDL_file_sets, key=sorter, reverse=True)[0]
        ref = ref or cache_manager.GITHUB_NXDL_BRANCH
        logger.debug(" final ref: " + str(ref))

        if ref not in self.NXDL_file_sets:
            # msg = 'unknown NXDL file set: ' + str(ref)
            msg = "expected one of " + " ".join(sorted(self.NXDL_file_sets.keys()))
            msg += ", received: " + str(ref)
            raise KeyError(msg)
        self.default_file_set = self.NXDL_file_sets[ref]
        logger.debug(" default file set: " + str(self.default_file_set))
        return self.default_file_set

    # - - - - - - - - - - - - - -
    # private

    def find_all_file_sets(self):
        """return dictionary of all NXDL file sets in both source & user caches"""
        fs = {k: v for k, v in self.source.find_all_file_sets().items()}
        msg = " source file set names: "
        msg += str(sorted(list(fs.keys())))
        logger.debug(msg)

        for k, v in self.user.find_all_file_sets().items():
            if k not in fs:
                #     raise ValueError('user cache file set already known: ' + k)
                # else:
                fs[k] = v

        self.NXDL_file_sets = fs  # remember
        msg = " all known file set names: "
        msg += str(sorted(list(fs.keys())))
        logger.debug(msg)
        return fs

    def cleanup(self):
        """removes any temporary directories"""
        self.source.cleanup()
        self.user.cleanup()

    def table_of_caches(self):
        """
        return a pyRestTable table describing all known file sets in both source and user caches

        :returns obj: instance of pyRestTable.Table with all known file sets

        **Example**::

            ============= ====== =================== ======= ==================================================================
            NXDL file set cache  date & time         commit  path
            ============= ====== =================== ======= ==================================================================
            a4fd52d       source 2016-11-19 01:07:45 a4fd52d /home/prjemian/Documents/projects/prjemian/punx/punx/cache/a4fd52d
            v3.3          source 2017-07-12 10:41:12 9285af9 /home/prjemian/Documents/projects/prjemian/punx/punx/cache/v3.3
            v2018.5       source 2018-05-15 16:34:19 a3045fd /home/prjemian/Documents/projects/prjemian/punx/punx/cache/v2018.5
            Schema-3.4    user   2018-05-15 08:24:34 aa1ccd1 /home/prjemian/.config/punx/Schema-3.4
            main          user   2021-12-17 13:09:18 041c2c0 /home/prjemian/.config/punx/main
            ============= ====== =================== ======= ==================================================================

        """
        t = pyRestTable.Table()
        fs = self.find_all_file_sets()
        t.labels = ["NXDL file set", "cache", "date & time", "commit", "path"]
        for k, v in fs.items():
            # print(k, str(v))
            row = [
                k,
            ]
            v.short_sha = get_short_sha(v.sha)
            for w in "cache last_modified short_sha path".split():
                row.append(str(v.__getattribute__(w)))
            t.rows.append(row)
        return t


class Base_Cache(object):

    """
    provides comon methods to get the QSettings path and file name

    .. autosummary::

       ~find_all_file_sets
       ~fileName
       ~path
       ~cleanup

    """

    qsettings = None
    is_temporary_directory = False

    @property
    def path(self):
        """directory containing the QSettings file"""
        if self.qsettings is None:
            raise RuntimeError("cache qsettings not defined!")
        return os.path.dirname(self.fileName())

    def fileName(self):
        """full path of the QSettings file"""
        if self.qsettings is None:
            raise RuntimeError("cache qsettings not defined!")
        fn = str(self.qsettings.fileName())
        return fn

    def find_all_file_sets(self):
        """index all NXDL file sets in this cache"""
        fs = {}
        if self.qsettings is None:
            raise RuntimeError("cache qsettings not defined!")
        cache_path = self.path
        logger.debug(" cache path: " + str(cache_path))

        for item in os.listdir(cache_path):
            if os.path.isdir(os.path.join(cache_path, item)):
                info_file = os.path.join(cache_path, item, INFO_FILE_NAME)
                if os.path.exists(info_file):
                    fs[item] = NXDL_File_Set()
                    fs[item].read_info_file(info_file)
        return fs

    def cleanup(self):
        """removes any temporary directories"""
        if self.is_temporary_directory:
            os.removedirs(self.path)
            self.is_temporary_directory = False


class SourceCache(Base_Cache):

    """manage the source directory cache of NXDL files"""

    def __init__(self):
        path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), SOURCE_CACHE_SUBDIR)
        )

        ini_file = os.path.abspath(os.path.join(path, SOURCE_CACHE_SETTINGS_FILENAME))
        self.qsettings = QtCore.QSettings(ini_file, QtCore.QSettings.IniFormat)


class UserCache(Base_Cache):

    """manage the user directory cache of NXDL files"""

    def __init__(self):
        self.qsettings = QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            __settings_organization__,
            __settings_package__,
        )

        path = self.path
        if not os.path.exists(path):
            os.mkdir(path)


class NXDL_File_Set(object):

    """describe a single set of NXDL files"""

    path = None
    cache = None
    info = None
    ref = None
    sha = None
    zip_url = None
    last_modified = None

    # these keys are written and read to the JSON info files in each downloaded file set
    json_file_keys = "ref sha zip_url last_modified".split()

    # TODO: #94 consider defining the SchemaManager here (perhaps lazy load)?
    # see nxdl_manager for example code:  __getattribute__()
    schema_manager = None
    __schema_manager_loaded__ = False

    def __getattribute__(self, *args, **kwargs):
        """implement lazy load of definition content"""
        if (
            len(args) == 1
            and args[0] == "schema_manager"
            and self.path is not None
            and os.path.exists(self.path)
            and not self.__schema_manager_loaded__
        ):
            from punx import schema_manager

            self.schema_manager = schema_manager.SchemaManager(self.path)
            self.__schema_manager_loaded__ = True
        return object.__getattribute__(self, *args, **kwargs)

    def __str__(self):
        if self.ref is None:
            return object.__str__(self)

        return(
            "NXDL_File_Set("
            f", last_modified={self.last_modified}"
            f", cache={self.cache}"
            f", short_sha={get_short_sha(self.sha)}"
            f", path= {self.path}"
            ")"
        )

    def read_info_file(self, file_name=None):
        if file_name is None and self.ref is None:
            raise ValueError("NXDL_File_Set() does not refer to any files")

        file_name = file_name or self.info
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"info file not found: {file_name}")

        self.info = file_name
        self.path = os.path.abspath(os.path.dirname(file_name))
        if self.path.find(os.path.join("punx", "cache")) > 0:
            self.cache = u"source"
        else:
            self.cache = u"user"

        # read the NXDL file set's info file for GitHub information
        obj = read_json_file(file_name)
        for k in self.json_file_keys:
            self.__setattr__(k, obj.get(k))
