---
layout: page
title: memo
---
<ul>
{% for mem in site.memo %}
  <li>{{ site.url }}{{ mem.url }} {{ mem.title }}</li>
{% endfor %}
</ul>
