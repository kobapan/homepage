# -*- coding: utf-8 -*-
# This is a Liquid filter plugin for jekyll
# show tag url configured in _config.yml
module Jekyll
  module TagUrl
    def tag_url(input)
      tag_urls = @context.registers[:site].config['tag_urls']
      tag_urls[input]
    end
  end
end

Liquid::Template.register_filter(Jekyll::TagUrl)
