apt update
apt install nginx

openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out cert.crt -keyout key.key

mkdir /etc/certs

mv cert.crt /etc/certs/
mv key.key /etc/certs/

cp nginx.conf /etc/nginx/conf.d/