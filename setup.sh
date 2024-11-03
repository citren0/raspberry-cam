apt update
apt install nginx

openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out cert.crt -keyout key.key

mkdir -p /etc/certs

mv cert.crt /etc/certs/
mv key.key /etc/certs/

cp raspberry-cam /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/raspberry-cam /etc/nginx/sites-enabled/