module Jekyll
  class TagAwarePreviousNextGenerator < Generator

    safe true
    priority :high

    def generate(site)
      site.tags.each_pair do |tag_name, posts|
        posts.sort! { |a, b| b <=> a }

        posts.each do |post|
          position = posts.index post

          if position && position < posts.length - 1
            tag_previous = posts[position + 1]
          else
            tag_previous = nil
          end

          if position && position > 1
            tag_next = posts[position - 1]
          else
            tag_next = nil
          end

          post.data["tag_previous"] = tag_previous unless tag_previous.nil?
          post.data["tag_next"] = tag_next unless tag_next.nil?
        end
      end
    end
  end
end
