#!/bin/bash

echo "启动职业规划顾问后端服务..."

if [ ! -f .env ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
fi

echo "启动Docker容器..."
docker-compose up -d

echo "等待数据库初始化..."
sleep 10

echo "服务启动完成！"
echo "API地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
