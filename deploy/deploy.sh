# удаляем все, кроме виртуального окружения python
cd ..
rm ../docs/.htaccess
mkdir tmp
mv cgi/venv tmp
rm -rf cgi/*
mv tmp/* cgi
rm -r tmp

# скачиваем новую версию и распаковываем ее
cd cgi
wget "https://github.com/qwert2603/crmit/archive/$1.tar.gz"
tar -xvf $1.tar.gz
rm $1.tar.gz

rm -rf ../docs/*
mv ./crmit-$1/.htaccess ./../docs/.htaccess

mv crmit-$1/* .
rm -r crmit-$1/

# применяем ключи из файла keys.txt
cd ../deploy
python3 apply_keys.py

# устанавливаем зависимости
cd ../cgi
venv/bin/pip3 install -r requiments.txt

# выполняем миграции БД
export FLASK_APP=start_dev.py
venv/bin/python3 venv/bin/flask db upgrade