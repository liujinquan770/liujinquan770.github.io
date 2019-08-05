---
title: VUE笔记1 VSCODE搭建环境
date: 2019-07-21 21:40:20
modified:
tags: [vue]
categories: vue
---

最近打算学习使用 VUE 前端框架。
![示例图片](vue1/6157741.jpg)

<!--more-->

本文主要参考  
1.https://liubing.me/vscode-vue-setting.html  
2.http://www.lovean.com/view-10-306911-0.html

## 安装环境和插件

安装 VSCODE, NODE 以及 VUE 插件 vetur + prettier + eslint。这个三个插件的配置细节请参考http://www.lovean.com/view-10-306911-0.html。
最终的配置脚本是

```json
{
  // 强制单引号
  "prettier.singleQuote": true,
  // 尽可能控制尾随逗号的打印
  "prettier.trailingComma": "all",
  // 开启 eslint 支持
  "prettier.eslintIntegration": true,
  // 保存时自动fix
  "eslint.autoFixOnSave": true,
  // 添加 vue 支持
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    {
      "language": "vue",
      "autoFix": true
    }
  ],
  // 使用插件格式化 html
  "vetur.format.defaultFormatter.html": "js-beautify-html",
  // 格式化插件的配置
  "vetur.format.defaultFormatterOptions": {
    "js-beautify-html": {
      // 属性强制折行对齐
      "wrap_attributes": "force-aligned"
    }
  }
}
```

## 其他插件
https://liubing.me/vscode-vue-setting.html


## nginx部署vue
### 安装nginx
rpm -ivh http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm  
yum install nginx
### 部署VUE
1.服务器创建目录/usr/local/vue/page  
2.将npm run build:prod后生成的dist下面的文件拷贝到该目录下  
3.修改/etc/nginx/conf.d下的default.conf配置文件
```yml
server {
    listen       80;
    server_name  localhost;

    #charset koi8-r;
    #access_log  /var/log/nginx/host.access.log  main;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }

    # proxy the PHP scripts to Apache listening on 127.0.0.1:80
    #
    #location ~ \.php$ {
    #    proxy_pass   http://127.0.0.1;
    #}

    # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
    #
    #location ~ \.php$ {
    #    root           html;
    #    fastcgi_pass   127.0.0.1:9000;
    #    fastcgi_index  index.php;
    #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
    #    include        fastcgi_params;
    #}

    # deny access to .htaccess files, if Apache's document root
    # concurs with nginx's one
    #
    #location ~ /\.ht {
    #    deny  all;
    #}
}

server {
    listen 8080;
    server_name localhost;

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }

    location / {
        root /usr/local/vue/page;
        try_files $uri $uri/ @router;
        index index.html;
    }

    location @router {
        rewrite ^.*$ /index.html last;
    }
}

```
4.重启nginx
