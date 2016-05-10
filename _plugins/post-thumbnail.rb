# -*- coding: utf-8 -*-
# This is a Liquid filter plugin for jekyll , show the first image as an img tag .
#
# Usage
#
# {{ post.content | thumbnail }}
# => <img src="http://exsample.com/1.jpg" height="100px" width="">
#
# {{ post.content | thumbnail: '200px'}}
# => <img src="http://exsample.com/1.jpg" height="200px" width="">
#
# {{ post.content | thumbnail: '' , '200px'}}
# => <img src="http://exsample.com/1.jpg" height="" width="200px">
#
#
module Jekyll
  module PostThumbnail

    def thumbnail(input, h="100px", w="" )

      # amazonアフィリエイトの空白画像を除く。
      while /src=['"](.*?)["'][^>]*>/ =~ input
        unless /ir-jp.amazon-adsystem.com/ =~ $~[1]
          break
        end
        input.gsub!(/<img.+src=['"]http:\/\/ir-jp.amazon-adsystem.com/, "")
      end

      if /<img.+src=['"](.*?)["']|!\[\]\((.*?)\)/ =~ input
       srcstr = $~[1]
       if /(.*?)staticflickr(.*?)(_[a-z])?\.jpg/ =~ srcstr
         '<img src="' + $~[1] + 'staticflickr' + $~[2] + '_m.jpg" height="' + h + '" width="' + w + '" class="thumbnail" >'
       else
         '<img src="' + srcstr + '" height="' + h + '" width="' + w + '" class="thumbnail" >'
       end
      end

    end # def thumbnail

  end
end

Liquid::Template.register_filter(Jekyll::PostThumbnail)
