upstream app_backend {
    server 10.10.10.21:8000 max_fails=2 fail_timeout=10s;
    server 10.10.10.22:8000 max_fails=2 fail_timeout=10s;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://app_backend;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}