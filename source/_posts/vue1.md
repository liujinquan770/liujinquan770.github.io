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
