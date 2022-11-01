
find ./ -type f -iname \*.rmd\* -exec sed -i 's/\t/ /gI' {} \;
