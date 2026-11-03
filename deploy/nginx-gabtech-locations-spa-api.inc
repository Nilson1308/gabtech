root /var/www/gabtech/dist;
index index.html;

location /static/ {
    alias /var/www/gabtech/backend/staticfiles/;
    expires 7d;
    add_header Cache-Control "public";
}

location /media/ {
    alias /var/www/gabtech/backend/media/;
    expires 1d;
}

location /health/ {
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass http://gabtech_gunicorn;
}

location /admin/ {
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 120s;
    proxy_pass http://gabtech_gunicorn;
}

location /api/ {
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 120s;
    proxy_pass http://gabtech_gunicorn;
}

location / {
    try_files $uri $uri/ /index.html;
}
