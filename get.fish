 #!/usr/bin/env fish
 for id in (cat list.txt);echo http://ac.qq.com/Comic/comicInfo/id/$id;if begin;getComic2.py -u http://ac.qq.com/Comic/comicInfo/id/$id;end;echo success;else;echo $id>>/tmp/error.txt;echo $id error;end;sleep 5;end
