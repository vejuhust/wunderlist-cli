#!/bin/bash

create_directory () {
    if [ ! -d $1 ]; then
        mkdir $1
    fi
}

TZ='Asia/Shanghai'; export TZ
yesterday="$(date '+%Y-%m-%d' -d '-1 day')"

cd "$( dirname "${BASH_SOURCE[0]}" )"

dir_md=Archive_Markdown
dir_html=Archive_HTML

file_md="$yesterday".md
file_html="$yesterday".html

create_directory $dir_md
create_directory $dir_html

for ((INDEX=1;INDEX<=3;INDEX++));
do
    python yesterday.py
    mv content.md content"$INDEX".md
    sleep 5
done

mv $(ls -S content*.md | head -1) "$file_md"

grip --export "$file_md" "$file_html"

mail -a "Content-type: text/html; charset='utf-8'" -s "Daily Log of "$yesterday" @Inbox" vejuhust@gmail.com < "$file_html"

mv "$file_md" "$dir_md"
mv "$file_html" "$dir_html"

rm -vf content*.md
