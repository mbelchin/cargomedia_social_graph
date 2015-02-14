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
import os
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


class CommandLineOptions(object):
  """Handles Command-line options and arguments."""

  def error(self, msg, code=2):
    """Shows a given `msg` error to the user and shows more info.

    Args:
      msg: (String) message to display.

    Returns:
      None
    """
    print 
    print msg
    print 
    print 'Use --help to get usage information.'
    print
    sys.exit(2)

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
        print __doc__
        sys.exit(0)

      elif option in ('-v', '--v', '--version'):
        print VERSION
        sys.exit(0)

      elif option in ('-t', '--t', '--tests'):
        import doctest
        doctest.testmod(verbose=True)

      elif option in ('-l', '--l', '--load'):
        if not arguments:
          self.error("Specify JSON data file to load")
        else:
          sg = SocialGraph()
          sg.load(arguments[0])

      elif option in ('-i', '--i', '--info'):
        if not arguments:
          self.error("Specify User ID to get information")
        else:
          sg = SocialGraph()
          sg.info(arguments[0])

      elif option in ('-f', '--f', '--friends'):
        if not arguments:
          self.error("Specify User ID to get friends")
        else:
          sg = SocialGraph()
          sg.friends(arguments[0])

      elif option in ('-o', '--o', '--friends_of_friends'):
        if not arguments:
          self.error("Specify User ID to get friends")
        else:
          sg = SocialGraph()
          sg.friends_of_friends(arguments[0])

      elif option in ('-s', '--s', '--suggested_friends'):
        if not arguments:
          self.error("Specify User ID to get friends")
        else:
          sg = SocialGraph()
          sg.suggested_friends(arguments[0])

    except Exception, e:
      self.error(e, code=1)


class SocialGraph(object):
  """SocialGraph class to solve CargoMedia social graph task. """

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

  def __response(self):
    """Write response in JSON format to client applications.

    Args:
      None

    Returns:
      None
    """
    try:
      print dumps(self._response)
    except Exception, e:
      print '%s.__response %s' % (self.__class__.__name__, e)

  def load(self, file):
    """Reads a given JSON file, loads it into mongoDB and returns JSON response
    with operation result.

    Args:
      file: (String) filepath and name to read and load.

    Returns:
      None

    Tests:
      >>> sg = SocialGraph()

      >>> sg.load()
      Traceback (most recent call last):
         ...
      TypeError: load() takes exactly 2 arguments (1 given)

      >>> sg.load('')
      {"message": "Specify a correct JSON data filename", "results": [], "error": true}

      >>> sg.load('/foo/bar')
      {"message": "Specify a correct JSON data filename and path", "results": [], "error": true}

      >>> sg.load('data.json')
      {"message": "JSON file successfully loaded. Inserted 20 users", "results": [], "error": false}
    """
    try:
      if not len(file):
        raise Exception("Specify a correct JSON data filename")

      if not os.path.exists(file) or not os.path.isfile(file):
        raise Exception("Specify a correct JSON data filename and path")

      json_file = open(file)
      users = load(json_file)
      json_file.close()
      
      self._users.remove()
      self._users.insert( users )
      
      self._response['error'] = False
      self._response['message'] = 'JSON file successfully loaded. Inserted %s users' % len(users)
    except Exception, e:
      self._response['message'] = str(e)
    finally:
      self.__response()

  def info(self, user_id):
    """Gets information for a given `user_id` and returns JSON response with resutls.

    Args:
      user_id: (int) User Id.

    Returns:
      None

    Tests:
      >>> sg = SocialGraph()

      >>> sg.info()
      Traceback (most recent call last):
         ...
      TypeError: info() takes exactly 2 arguments (1 given)

      >>> sg.info("a")
      {"message": "Invalid User ID", "results": [], "error": true}

      >>> sg.info(0)
      {"message": "Specify a correct User ID", "results": [], "error": true}

      >>> sg.info(1)
      {"message": "", "results": [{"surname": "Crowe", "firstName": "Paul", "gender": "male", "age": 28, "friends": [2], "id": 1}], "error": false}
      
      >>> sg.info(10)
      {"message": "", "results": [{"surname": "Lane", "firstName": "Amy", "gender": "female", "age": 24, "friends": [5, 11], "id": 10}], "error": false}

      >>> sg.info(33)
      {"message": "", "results": [], "error": false}
    """
    try:
      try: user_id = int(user_id)
      except: raise ValueError("Invalid User ID")
      if not user_id: raise Exception("Specify a correct User ID")

      u = self.__get_info(user_id)
      
      self._response['error'] = False
      self._response['message'] = ""
      self._response['results'] = [u] if u else []
    except Exception, e:
      self._response['message'] = str(e)
    finally:
      self.__response()

  def __get_info(self, user_id):
    """Gets info for a given `user_id`.

    Args:
      user_id: (int) User ID.

    Returns:
      dict with user information.
      Eg.: {"surname": "Lane", "firstName": "Amy", "gender": "female", "age": 24, "friends": [5, 11], "id": 10}
    """
    return self._users.find_one( {'id': user_id} , {'_id': 0} )

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
      {"message": "Invalid User ID", "results": [], "error": true}

      >>> sg.friends(0)
      {"message": "Specify a correct User ID", "results": [], "error": true}

      >>> sg.friends(1)
      {"message": "", "results": [{"surname": "Fitz", "firstName": "Rob", "gender": "male", "age": 23, "friends": [1, 3], "id": 2}], "error": false}

      >>> sg.friends(10)
      {"message": "", "results": [{"surname": "Mac", "firstName": "Peter", "gender": "male", "age": 29, "friends": [3, 6, 11, 10, 7], "id": 5}, {"surname": "Phelan", "firstName": "Sandra", "gender": "female", "age": 28, "friends": [5, 10, 19, 20], "id": 11}], "error": false}

      >>> sg.friends(33)
      {"message": "", "results": [], "error": false}
    """
    try:
      try: user_id = int(user_id)
      except: raise ValueError("Invalid User ID")
      if not user_id: raise Exception("Specify a correct User ID")

      u = self.__get_friends(user_id)
      
      self._response['error'] = False
      self._response['message'] = ""
      self._response['results'] = u if u else []
    except Exception, e:
      self._response['message'] = str(e)
    finally:
      self.__response()

  def __get_friends(self, user_id):
    """Gets friends of a given `user_id`.

    Args:
      user_id: (int) User ID.

    Returns:
      List with friends.
    """
    return list(self._users.find( {'friends': {"$in": [user_id]}} , {'_id': 0} ))

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
      {"message": "Invalid User ID", "results": [], "error": true}

      >>> sg.friends_of_friends(0)
      {"message": "Specify a correct User ID", "results": [], "error": true}

      >>> sg.friends_of_friends(1)
      {"message": "", "results": [{"surname": "O'Carolan", "firstName": "Ben", "gender": "male", "age": null, "friends": [2, 4, 5, 7], "id": 3}], "error": false}

      >>> sg.friends_of_friends(10)
      {"message": "", "results": [{"surname": "O'Carolan", "firstName": "Ben", "gender": "male", "age": null, "friends": [2, 4, 5, 7], "id": 3}, {"surname": "Barry", "firstName": "John", "gender": "male", "age": 18, "friends": [5], "id": 6}, {"surname": "Lane", "firstName": "Sarah", "gender": "female", "age": 30, "friends": [3, 5, 20, 12, 8], "id": 7}, {"surname": "Long", "firstName": "Catriona", "gender": "female", "age": 28, "friends": [11, 20], "id": 19}, {"surname": "Couch", "firstName": "Katy", "gender": "female", "age": 28, "friends": [7, 11, 12, 13, 16, 17, 19], "id": 20}], "error": false}

      >>> sg.friends_of_friends(33)
      {"message": "", "results": [], "error": false}
    """
    try:
      try: user_id = int(user_id)
      except: raise ValueError("Invalid User ID")
      if not user_id: raise Exception("Specify a correct User ID")

      u = self.__get_friends_of_friends(user_id)
      
      self._response['error'] = False
      self._response['message'] = ""
      self._response['results'] = u if u else []
    except Exception, e:
      self._response['message'] = str(e)
    finally:
      self.__response()

  def __get_friends_of_friends(self, user_id):
    """Gets friends of friends for a given `user_id`.

    Args:
      user_id: (int) User Id.

    Returns:
      List with friends of friends.
    """
    friends = self.__get_friends(user_id)
    return list(self._users.find( 
      {
        'id': {
                "$in": [ i for f in friends for i in f['friends'] ] , 
                "$nin": ( [i['id'] for i in friends] + [user_id] ), 
              }
      } , {'_id': 0} 
      )
    )

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
      {"message": "Invalid User ID", "results": [], "error": true}

      >>> sg.suggested_friends(0)
      {"message": "Specify a correct User ID", "results": [], "error": true}

      >>> sg.suggested_friends(1)
      {"message": "", "results": [], "error": false}

      >>> sg.suggested_friends(10)
      {"message": "", "results": [], "error": false}

      >>> sg.suggested_friends(7)
      {"message": "", "results": [{"surname": "Phelan", "firstName": "Sandra", "gender": "female", "age": 28, "friends": [5, 10, 19, 20], "id": 11}, {"surname": "Daly", "firstName": "Lisa", "gender": "female", "age": 28, "friends": [12, 14, 20], "id": 13}], "error": false}

      >>> sg.suggested_friends(33)
      {"message": "", "results": [], "error": false}
    """
    try:
      try: user_id = int(user_id)
      except: raise ValueError("Invalid User ID")
      if not user_id: raise Exception("Specify a correct User ID")

      u = self.__get_suggested_friends(user_id)
      
      self._response['error'] = False
      self._response['message'] = ""
      self._response['results'] = u if u else []
    except Exception, e:
      self._response['message'] = str(e)
    finally: 
      self.__response()

  def __get_suggested_friends(self, user_id):
    """Returns people in the group who know 2 or more direct friends of the chosen user, but are not directly connected to the user.

    Args:
      user_id: (int) User Id.

    Returns:
      List with suggested friends.

    Tests:

    """
    f = self.__get_friends(user_id)
    df = set([f['id'] for f in f])
    fof = self.__get_friends_of_friends(user_id)
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
    cmdo = CommandLineOptions()
    opts, args = getopt.getopt(sys.argv[1:], 'h, v, t, l, i, f, o, s', \
      ['help', 'version', 'tests', 'load', 'info', 'friends', 'friends_of_friends', 
       'suggested_friends'])
  except getopt.error, msg:
    cmdo.error(msg)
  cmdo.parse(opts, args)
  
if __name__ == '__main__':
  main()
