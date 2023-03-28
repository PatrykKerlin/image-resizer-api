worker_processes auto;

http {
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;

    server {
        listen              443 ssl;
        server_name         18.159.131.181;
        keepalive_timeout   70;

        ssl_certificate     18.159.131.181.crt;
        ssl_certificate_key 18.159.131.181.key;
        ssl_protocols       TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
        ssl_ciphers         HIGH:!aNULL:!MD5;

        location /static {
            alias /vol/static;
        }

        location / {
            uwsgi_pass              ${APP_HOST}:${APP_PORT};
            include                 /etc/nginx/uwsgi_params;
            client_max_body_size    10M;
        }
    }
}