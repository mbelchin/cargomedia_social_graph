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
</pre>

Load JSON file data into mongoDB:
<pre>
python social_graph.py --load [JSON_FILE]
</pre>

Get UserId (1) information:
<pre>
python social_graph.py --info [USER_ID]
</pre>

Get UserId (1) friends:
<pre>
python social_graph.py --friends [USER_ID]
</pre>

Get UserId (1) friends of friends:
<pre>
python social_graph.py --friends_of_friends [USER_ID]
</pre>

Get UserId (1) suggested friends:
<pre>
python social_graph.py --suggested_friends [USER_ID]
</pre>

**Tests**

Run tests using:
<pre>
python social_graph.py --tests
</pre>