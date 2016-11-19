---
layout: memo
title: memo
---
<ul>
{% for mem in site.memo %}
   {% unless mem.title == "memo" %}
  <li><a href="{{ site.url }}{{ mem.url }}">{{ mem.title }}</a></li>
  {% endunless %}
{% endfor %}
</ul>
