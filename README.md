# cargomedia_social_graph
Small tests for CargoMedia Social Graph using different approaches and technologies

Python and mongoDB Example
===========

**Requirements for Python-mongDB sample**

* Python
* mongoDB
* pymongo

**Usage**

Get Usage Information:
<pre>
python social_graph.py --help

python social_graph.py -h
</pre>

Load JSON file data into mongoDB:
<pre>
python social_graph.py --load [JSON_FILE]

python social_graph.py -l data.json
</pre>

Get UserId (1) information:
<pre>
python social_graph.py --info [USER_ID]

python social_graph.py -i 1
</pre>

Get UserId (1) friends:
<pre>
python social_graph.py --friends [USER_ID]

python social_graph.py -f 1
</pre>

Get UserId (1) friends of friends:
<pre>
python social_graph.py --friends_of_friends [USER_ID]

python social_graph.py -o 1
</pre>

Get UserId (1) suggested friends:
<pre>
python social_graph.py --suggested_friends [USER_ID]

python social_graph.py -s 1
</pre>

**Tests**

Run tests using:
<pre>
python -m doctestsocial_graph.py
</pre>

Or:
<pre>
python -m doctest -v social_graph.py
</pre>