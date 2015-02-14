# cargomedia_social_graph
Small tests for CargoMedia usign different approaches and technologies

CargoMedia Social Graph 
Python and mongoDB Example
===========

**Requirements for Python-mongDB sample**

* Python
* mongoDB
* pymongo

**Usage**

Get UserId (1) information:
<pre>
python social_graph.py -info 1
</pre>

Get UserId (1) friends:
<pre>
python social_graph.py -friends 1
</pre>

Get UserId (1) friends of friends:
<pre>
python social_graph.py -fof 1
</pre>

Get UserId (1) suggested friends:
<pre>
python social_graph.py -sf 1
</pre>

**Tests**

Run tests using:
<pre>
python social_graph.py -tests
</pre>