В папке main для корректной работы программы должен лежать файл .env со значениями переменных,
которые требуются для подключения базы данных. Содержание должно быть таким:
DB_USER=имя_пользователя_с_правами_на_базу_данных
DB_PASSWORD=секретный_пароль
DB_HOST= адрес_хоста_localhost
DB_PORT=номер_порта_для_подключения_5432
DB_NAME=название_базы_данных
SECRET_KEY=my_secret_key
Последняя опция пока не востребована, так как обмен данных идет без подписей, но при смене режима пригодится

А это скрипт, для возможности работы с базой, даже без сюдо прав:
curl -L -o postres.tar.gz "https://github.com/theseus-rs/postgresql-binaries/releases/download/18.3.0/postgresql-18.3.0-x86_64-unknown-linux-gnu.tar.gz"
tar -xzf postres.tar.gz
mkdir -p ~/pg_local
cd ~/pg_local
mv ~/postgresql-18.3.0-x86_64-unknown-linux-gnu ~/pg_local/
~/pg_local$ echo 'export PATH="$HOME/pg_local/postgresql-18.3.0-x86_64-unknown-linux-gnu/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
~/Desktop$ initdb -D ~/pg_data -U postgres --auth=scram-sha-256 -W
#psql -U admin -d postgres