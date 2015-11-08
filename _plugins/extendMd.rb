# -*- coding: utf-8 -*-
module Jekyll
  module Converters
    class Markdown < Converter
      alias old_convert convert
      
      def convert(content)
        
        # ここにコンバート処理を記述
        
        # small word
        content.gsub! /<s>(.*)<\/s>/ do
          "<small>#{$1}</small>"
        end
        
        old_convert(content)
      end
    end
  end
end
