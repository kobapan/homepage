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
      if /<img.+src=['"](.*?)["']|!\[\]\((.*?)\)/ =~ input
        srcstr = $~[1]
        if /(.*?)staticflickr(.*?)(_[a-z])?\.jpg/ =~ srcstr
          '<img src="' + $~[1] + 'staticflickr' + $~[2] + '_m.jpg" height="' + h + '" width="' + w + '">'
        else
          '<img src="' + srcstr + '" height="' + h + '" width="' + w + '">'
        end
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::PostThumbnail)
