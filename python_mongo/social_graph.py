#!/usr/bin/env python  
# -*- coding: utf-8 -*-
#
# Author: Moises Belchin <moisesbelchin@gmail.com>
# Date: February 2015
"""CargoMedia social graph task application. 

Usage:

  social_graph.py [options]

Options:
  -h, --h, --help               : Show help.
  -v, --v, --version            : Show version software.
  -t, --t, --tests              : Run tests.
  -l, --l, --load               : Load given [JSON FILE] into mongoDB.
  -i, --i, --info               : Get info for a given [USER ID].
  -f, --f, --friends            : Get friends for a given [USER ID].
  -o, --o, --friends_of_friends : Get friends of friends for a given [USER ID].
  -s, --s, --suggested_friends  : Get suggested friends for a given [USER ID].

Requirements:

  This software requires mongoDB and pymongo. 

  mongoDB should be running in your system. 

Default values:
  
  This software uses these values by default.

  mongoDB server: localhost
  mongoDB port: 27017
  mongoDB database name: social-graph
  mongoDB users collection name: users

  If you need to change any of these values edit config.py file.
"""
import sys
from os import path
import getopt
from json import load
from pymongo import MongoClient
from bson.json_util import dumps
import config

#==============================================================================
# Globals
#==============================================================================
### Software version
VERSION = '0.0.1'


class MongoConnectionException(Exception):
  """MongoDB Connection Exception."""


class Response(object):
  """Class to handle responses to the client applications.

  This class uses JSON format by default however it could be easily changed to 
  support different response formats.
  """

  def __init__(self, error=False, message="", results=[], format="JSON"):
    """Initialize Response object.

    Args:
      error: (Bool) Determines whether an error occurred while processing request.
      message: (String) Error message if error is True.
      results: (List) List of results fetched from mongoDB.

    Returns:
      None
    """
    self.format = format
    self.error = error
    self.message = message
    self.results = []

  def write(self):
    """Write response to client in `format`.

    Args:
      None

    Returns:
      None
    """
    if self.format == 'JSON':
      print dumps({
        "error": self.error,
        "message": self.message,
        "results": self.results,
      })

class SocialGraphAPI(object):
  """SocialGraph API.
  
  Parse command-line options and arguments, gets results using `SocialGraph` class
  and print out results.

  This class uses `Response` class to print out the client responses in different 
  formats.
  """

  # `Response` object
  response = None

  def __init__(self):
    """Initialize API class.

    Args:
      None

    Returns:
      None
    """
    self.response = Response()

  def error(self, message):
    """Write an error message to the client.

    Args:
      message: (String) with error description

    Returns:
      None
    """
    self.response.error = True
    self.response.message = '%s \n\nUse -h for more information' % message
    self.response.write()

  def parse(self, options, arguments):
    """Parse command-line options.

    Args:
      options: (List) command-line options
      arguments: (List) command-line arguments

    Returns:
      None
    """
    try:
      option, value = options[0]
      if option in ('-h', '--h', '--help'):
        self.response.message = __doc__
        
      elif option in ('-v', '--v', '--version'):
        self.response.message = VERSION
        
      elif option in ('-t', '--t', '--tests'):
        import doctest
        doctest.testmod(verbose=True)
        
      elif option in ('-l', '--l', '--load'):
        if not arguments:
          raise Exception("Specify JSON data file to load")
        sg = SocialGraph()
        result = sg.load(arguments[0])
        self.response.message = result[0]
        self.response.results = result[1]

      elif option in ('-i', '--i', '--info'):
        if not arguments:
          raise Exception("Specify User ID to get information")
        sg = SocialGraph()
        self.response.results = sg.info(arguments[0])

      elif option in ('-f', '--f', '--friends'):
        if not arguments:
          raise Exception("Specify User ID to get friends")
        sg = SocialGraph()
        self.response.results = sg.friends(arguments[0])

      elif option in ('-o', '--o', '--friends_of_friends'):
        if not arguments:
          raise Exception("Specify User ID to get friends of friends")
        sg = SocialGraph()
        self.response.results = sg.friends_of_friends(arguments[0])

      elif option in ('-s', '--s', '--suggested_friends'):
        if not arguments:
          raise Exception("Specify User ID to get suggested friends")
        sg = SocialGraph()
        self.response.results = sg.suggested_friends(arguments[0])

    except Exception, e:
      self.response.error = True
      self.response.message = str(e)

    finally:
      self.response.write()


class SocialGraph(object):
  """SocialGraph class to solve CargoMedia social graph task."""

  # mongoDB client
  _client = None
  # mongoDB database
  _db = None
  # mongoDB users collection
  _users = None
  # response dict
  _response = {}

  def __init__(self):
    """Initialize mongoDB connection.

    Args:
      None

    Returns:
      None
    """
    try:
      self._client = MongoClient('mongodb://%s:%s/' % (config.MONGO_SERVER, config.MONGO_PORT))
      self._db = self._client[config.MONGO_DB_NAME]
      self._users = self._db[config.MONGO_COLLECTION_USERS]
      self._response = {
        'error': True,
        'message': "",
        'results': [],
      }
    except Exception, e:
      raise MongoConnectionException('%s._mongo_connect %s' % (self.__class__.__name__, e))

  def load(self, file):
    """Reads a given JSON file, loads it into mongoDB and returns JSON response
    with operation result.

    Args:
      file: (String) filepath and name to read and load.

    Returns:
      String with operation result and inserted documents.

    Tests:
      >>> sg = SocialGraph()

      >>> sg.load()
      Traceback (most recent call last):
         ...
      TypeError: load() takes exactly 2 arguments (1 given)

      >>> sg.load('')
      Traceback (most recent call last):
         ...
      Exception: Specify a correct JSON data filename

      >>> sg.load('/foo/bar')
      Traceback (most recent call last):
         ...
      Exception: Specify a correct JSON data filename and path

      >>> sg.load('data.json')
      ('JSON file successfully loaded. Inserted 20 users', [{u'surname': u'Crowe', u'firstName': u'Paul', u'gender': u'male', u'age': 28, '_id': 1, u'friends': [2]}, {u'surname': u'Fitz', u'firstName': u'Rob', u'gender': u'male', u'age': 23, '_id': 2, u'friends': [1, 3]}, {u'surname': u"O'Carolan", u'firstName': u'Ben', u'gender': u'male', u'age': None, '_id': 3, u'friends': [2, 4, 5, 7]}, {u'surname': u'', u'firstName': u'Victor', u'gender': u'male', u'age': 28, '_id': 4, u'friends': [3]}, {u'surname': u'Mac', u'firstName': u'Peter', u'gender': u'male', u'age': 29, '_id': 5, u'friends': [3, 6, 11, 10, 7]}, {u'surname': u'Barry', u'firstName': u'John', u'gender': u'male', u'age': 18, '_id': 6, u'friends': [5]}, {u'surname': u'Lane', u'firstName': u'Sarah', u'gender': u'female', u'age': 30, '_id': 7, u'friends': [3, 5, 20, 12, 8]}, {u'surname': u'Downe', u'firstName': u'Susan', u'gender': u'female', u'age': 28, '_id': 8, u'friends': [7]}, {u'surname': u'Stam', u'firstName': u'Jack', u'gender': u'male', u'age': 28, '_id': 9, u'friends': [12]}, {u'surname': u'Lane', u'firstName': u'Amy', u'gender': u'female', u'age': 24, '_id': 10, u'friends': [5, 11]}, {u'surname': u'Phelan', u'firstName': u'Sandra', u'gender': u'female', u'age': 28, '_id': 11, u'friends': [5, 10, 19, 20]}, {u'surname': u'Murphy', u'firstName': u'Laura', u'gender': u'female', u'age': 33, '_id': 12, u'friends': [7, 9, 13, 20]}, {u'surname': u'Daly', u'firstName': u'Lisa', u'gender': u'female', u'age': 28, '_id': 13, u'friends': [12, 14, 20]}, {u'surname': u'Johnson', u'firstName': u'Mark', u'gender': u'male', u'age': 28, '_id': 14, u'friends': [13, 15]}, {u'surname': u'Crowe', u'firstName': u'Seamus', u'gender': u'male', u'age': 24, '_id': 15, u'friends': [14]}, {u'surname': u'Slater', u'firstName': u'Daren', u'gender': u'male', u'age': 28, '_id': 16, u'friends': [18, 20]}, {u'surname': u'Zoltan', u'firstName': u'Dara', u'gender': u'male', u'age': 48, '_id': 17, u'friends': [18, 20]}, {u'surname': u'D', u'firstName': u'Marie', u'gender': u'female', u'age': 28, '_id': 18, u'friends': [17]}, {u'surname': u'Long', u'firstName': u'Catriona', u'gender': u'female', u'age': 28, '_id': 19, u'friends': [11, 20]}, {u'surname': u'Couch', u'firstName': u'Katy', u'gender': u'female', u'age': 28, '_id': 20, u'friends': [7, 11, 12, 13, 16, 17, 19]}])

      >>> isinstance(sg.load('data.json'), tuple)
      True
    """
    if not len(file):
      raise Exception("Specify a correct JSON data filename")

    if not path.exists(file) or not path.isfile(file):
      raise Exception("Specify a correct JSON data filename and path")

    json_file = open(file)
    users = load(json_file)
    json_file.close()
    
    for u in users:
      u['_id'] = u.pop('id')
    self._users.remove()
    self._users.insert( users )
    
    return ('JSON file successfully loaded. Inserted %s users' % len(users), users)
    
  def info(self, user_id):
    """Gets information for a given `user_id` and returns JSON response with resutls.

    Args:
      user_id: (int) User Id.

    Returns:
      List with the found user as a dict. Eg.: {"surname": "Lane", "firstName": "Amy", "gender": "female", "age": 24, "friends": [5, 11], "_id": 10}

    Tests:
      >>> sg = SocialGraph()

      >>> sg.info()
      Traceback (most recent call last):
         ...
      TypeError: info() takes exactly 2 arguments (1 given)

      >>> sg.info("a")
      Traceback (most recent call last):
         ...
      ValueError: Invalid User ID

      >>> sg.info(0)
      Traceback (most recent call last):
         ...
      Exception: Specify a correct User ID

      >>> sg.info(1)
      [{u'surname': u'Crowe', u'firstName': u'Paul', u'gender': u'male', u'age': 28, u'_id': 1, u'friends': [2]}]

      >>> isinstance(sg.info(1), list)
      True
      
      >>> sg.info(10)
      [{u'surname': u'Lane', u'firstName': u'Amy', u'gender': u'female', u'age': 24, u'_id': 10, u'friends': [5, 11]}]

      >>> sg.info(33)
      []

      >>> isinstance(sg.info(33), list)
      True
    """
    try: user_id = int(user_id)
    except: raise ValueError("Invalid User ID")
    if not user_id: raise Exception("Specify a correct User ID")

    u = self._users.find_one( {'_id': user_id} )
    return [u] if u else []

  def friends(self, user_id):
    """Gets friends of a given `user_id` and returns JSON reponse with results.
    
    Args: 
      user_id: (int) User Id.

    Returns:
      None

    Tests:
      >>> sg = SocialGraph()

      >>> sg.friends()
      Traceback (most recent call last):
        ...
      TypeError: friends() takes exactly 2 arguments (1 given)

      >>> sg.friends("a")
      Traceback (most recent call last):
         ...
      ValueError: Invalid User ID

      >>> sg.friends(0)
      Traceback (most recent call last):
         ...
      Exception: Specify a correct User ID

      >>> sg.friends(1)
      [{u'surname': u'Fitz', u'firstName': u'Rob', u'gender': u'male', u'age': 23, u'_id': 2, u'friends': [1, 3]}]

      >>> isinstance(sg.friends(1), list)
      True

      >>> sg.friends(10)
      [{u'surname': u'Mac', u'firstName': u'Peter', u'gender': u'male', u'age': 29, u'_id': 5, u'friends': [3, 6, 11, 10, 7]}, {u'surname': u'Phelan', u'firstName': u'Sandra', u'gender': u'female', u'age': 28, u'_id': 11, u'friends': [5, 10, 19, 20]}]

      >>> sg.friends(33)
      []

      >>> isinstance(sg.friends(33), list)
      True
    """
    try: user_id = int(user_id)
    except: raise ValueError("Invalid User ID")
    if not user_id: raise Exception("Specify a correct User ID")

    u = list(self._users.find( {'friends': {"$in": [user_id]}} ))
    return u if u else []

  def friends_of_friends(self, user_id):
    """Gets friends of friends of a given `user_id` and returns JSON response
    with results.

    Args: 
      user_id: (int) User Id.

    Returns:
      None

    Tests:
      >>> sg = SocialGraph()

      >>> sg.friends_of_friends()
      Traceback (most recent call last):
        ...
      TypeError: friends_of_friends() takes exactly 2 arguments (1 given)

      >>> sg.friends_of_friends("a")
      Traceback (most recent call last):
         ...
      ValueError: Invalid User ID

      >>> sg.friends_of_friends(0)
      Traceback (most recent call last):
         ...
      Exception: Specify a correct User ID

      >>> sg.friends_of_friends(1)
      [{u'surname': u"O'Carolan", u'firstName': u'Ben', u'gender': u'male', u'age': None, u'_id': 3, u'friends': [2, 4, 5, 7]}]

      >>> isinstance(sg.friends_of_friends(1), list)
      True

      >>> sg.friends_of_friends(10)
      [{u'surname': u"O'Carolan", u'firstName': u'Ben', u'gender': u'male', u'age': None, u'_id': 3, u'friends': [2, 4, 5, 7]}, {u'surname': u'Barry', u'firstName': u'John', u'gender': u'male', u'age': 18, u'_id': 6, u'friends': [5]}, {u'surname': u'Lane', u'firstName': u'Sarah', u'gender': u'female', u'age': 30, u'_id': 7, u'friends': [3, 5, 20, 12, 8]}, {u'surname': u'Long', u'firstName': u'Catriona', u'gender': u'female', u'age': 28, u'_id': 19, u'friends': [11, 20]}, {u'surname': u'Couch', u'firstName': u'Katy', u'gender': u'female', u'age': 28, u'_id': 20, u'friends': [7, 11, 12, 13, 16, 17, 19]}]

      >>> sg.friends_of_friends(33)
      []

      >>> isinstance(sg.friends_of_friends(33), list)
      True
    """
    try: user_id = int(user_id)
    except: raise ValueError("Invalid User ID")
    if not user_id: raise Exception("Specify a correct User ID")

    friends = self.friends(user_id)
    fof = list(self._users.find( {
      '_id': {
              "$in": [ i for f in friends for i in f['friends'] ] , 
              "$nin": ( [i['_id'] for i in friends] + [user_id] ), 
             }
    } ))
    return fof if fof else []

  def suggested_friends(self, user_id):
    """Gets people in the group who know 2 or more direct friends of the given 
    user `user_id`, but are not directly connected to the user.
    Returns JSON response with results.

    Args: 
      user_id: (int) User Id.

    Returns:
      None

    Tests:
      >>> sg = SocialGraph()

      >>> sg.suggested_friends()
      Traceback (most recent call last):
        ...
      TypeError: suggested_friends() takes exactly 2 arguments (1 given)

      >>> sg.suggested_friends("a")
      Traceback (most recent call last):
         ...
      ValueError: Invalid User ID

      >>> sg.suggested_friends(0)
      Traceback (most recent call last):
         ...
      Exception: Specify a correct User ID

      >>> sg.suggested_friends(1)
      []

      >>> isinstance(sg.suggested_friends(1), list)
      True

      >>> sg.suggested_friends(10)
      []

      >>> sg.suggested_friends(7)
      [{u'surname': u'Phelan', u'firstName': u'Sandra', u'gender': u'female', u'age': 28, u'_id': 11, u'friends': [5, 10, 19, 20]}, {u'surname': u'Daly', u'firstName': u'Lisa', u'gender': u'female', u'age': 28, u'_id': 13, u'friends': [12, 14, 20]}]

      >>> isinstance(sg.suggested_friends(7), list)
      True

      >>> sg.suggested_friends(33)
      []

      >>> isinstance(sg.suggested_friends(33), list)
      True
    """
    try: user_id = int(user_id)
    except: raise ValueError("Invalid User ID")
    if not user_id: raise Exception("Specify a correct User ID")

    f = self.friends(user_id)
    df = set([f['_id'] for f in f])
    fof = self.friends_of_friends(user_id)
    sf = []
    for u in fof:
      if len(df.intersection(u['friends'])) > 1 and u not in sf:
        sf.append(u)
    return sf


def main():
  """Main method. Parse options and arguments.

  Args:
    None
  
  Returns:
    None
  """
  try:
    api = SocialGraphAPI()
    opts, args = getopt.getopt(sys.argv[1:], 'h, v, t, l, i, f, o, s', \
      ['help', 'version', 'tests', 'load', 'info', 'friends', 'friends_of_friends', 
       'suggested_friends'])
    api.parse(opts, args)
  except getopt.error, msg:
    api.error(msg)
  
if __name__ == '__main__':
  main()
