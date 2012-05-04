#!/bin/bash
# Minify the CSS and Javascript for a mobile site

mobile_domain=$1

if [ -z "$mobile_domain" ]; then
    echo "usage: minify.sh mobile_domain"
    exit 1
fi

sitebase=/var/www/$mobile_domain

if [ ! -d "${sitebase}" ]; then
    echo "Mobile site '$mobile_domain' not found"
    exit 2
fi

scratchdir=$(mktemp -d)
function cleanup {
    rm -fr $scratchdir
}
trap cleanup EXIT

mincss="$sitebase/static/combined-min.css"
minjs="$sitebase/static/combined-min.js"

# generate minned CSS
cp /var/www/share/globalstatic/files/base.css $scratchdir/combined.css
if [ -r $sitebase/static/site.css ]; then
    cat $sitebase/static/site.css >> $scratchdir/combined.css
fi
yui-compressor $scratchdir/combined.css > "$mincss"

# generate minned JS
cp /var/www/share/globalstatic/files/offset.js $scratchdir/combined.js
if [ -r $sitebase/static/site.js ]; then
    cat $sitebase/static/site.js >> $scratchdir/combined.js
fi
yui-compressor $scratchdir/combined.js > "$minjs"
