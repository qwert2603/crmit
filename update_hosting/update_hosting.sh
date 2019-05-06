cd ..
mkdir tmp
cd cgi
mv venv update_hosting.sh keys.txt ../tmp
cd ..
rm -rf cgi/*
mv tmp/* cgi
rm -rf tmp
cd cgi

wget "https://github.com/qwert2603/crmit/archive/$1.tar.gz"
tar -xvf $1.tar.gz
rm $1.tar.gz

rm -rf ../docs/*
mv ./crmit-$1/.htaccess ./../docs/.htaccess

mv crmit-$1/* .
rm -r crmit-$1/