# удаляем все, кроме виртуального окружения python
cd ..
rm ../docs/.htaccess
mkdir tmp
mv cgi/venv tmp
rm -rf cgi/*
mv tmp/* cgi
rm -r tmp

# скачиваем новую версию и распаковываем ее
version=$1
cd cgi
wget "https://github.com/qwert2603/crmit/archive/$version.tar.gz"
tar -xvf $version.tar.gz
rm $version.tar.gz

# настройка переадресации запросов в Flask-приложение
rm -rf ../docs/*
mv ./crmit-$version/.htaccess ./../docs/.htaccess

mv crmit-$version/* .
rm -r crmit-$version/

# применяем ключи из файла keys.txt
cd ../deploy
python3 apply_keys.py

# устанавливаем зависимости
cd ../cgi
venv/bin/pip3 install -r requiments.txt

# выполняем миграции БД
export FLASK_APP=start_dev.py
venv/bin/python3 venv/bin/flask db upgrade
