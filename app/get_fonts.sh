#!/bin/bash

if [ -f "api-key" ]; then
    apikey=$(cat api-key)
    curl "https://www.googleapis.com/webfonts/v1/webfonts?key=$apikey" > googlefonts.json
else
    echo "No API key"
fi
exit


echo '{' > fonts.json

for f in $(find google-fonts -name 'METADATA.pb' -print); do
    echo -n "Reading $f... "
    name=$(grep "^name:" $f | cut -d " " -f 2-) 
    category=$(grep "^category:" $f | cut -d " " -f 2-)
    echo "  $name: {"category": $category}," >> fonts.json
    echo "($category) $name" | tr -d '"'
    #| awk '{print $0 ","}' | tee -a fonts.json #| tr -d '"' 
done
echo '}' >> fonts.json
