//ブックマークレットを作るときのTips - Qiita | http://qiita.com/xtetsuji/items/e8b61bb39c41b7a9345e
//ブックマークレット／Bookmarkletの作り方 - catch.jp-wiki | http://www.catch.jp/wiki/?Bookmarklet%A4%CE%BA%EE%A4%EA%CA%FD

// plain
javascript:(function(d,l,i){
    var n=window.open().document;
    n.write('<script>function s(e){e.select();e.focus();};</script>'+
            '<textarea rows="15" cols="80" onclick="s(this);">'+
            '<figure class="related-post"><a href="'+l.href+'"><img src="'+i+'"/></a>'+
            '<figcaption><a href="'+l.href+'">'+d.title.replace(/ \| 自然農 ガットポンポコ/g,"")+'</a></figcaption>'+
            '</figure></textarea>');
    n.close();
})(document,location,document.getElementById("contents").innerHTML.match(/<img(.*?)src=\"(.*?\.jpg)/)[2]);

// compress
javascript:(function(d,l,i){var n=window.open().document;n.write('<script>function s(e){e.select();e.focus();};</script>'+'<textarea rows="15" cols="80" onclick="s(this);">'+'<figure class="related-post"><a href="'+l.href+'"><img src="'+i+'"/></a>'+'<figcaption><a href="'+l.href+'">'+d.title.replace(/ \| 自然農 ガットポンポコ/g,"")+'</a></figcaption>'+'</figure></textarea>');n.close();})(document,location,document.getElementById("contents").innerHTML.match(/<img(.*?)src=\"(.*?\.jpg)/)[2]);


