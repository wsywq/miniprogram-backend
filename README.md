# 微信小程序 - 习惯打卡系统后端

基于 FastAPI 开发的微信小程序习惯打卡系统后端服务。

## 🚀 功能特性

- **用户管理**: 微信授权登录、用户信息管理
- **习惯管理**: 创建、编辑、删除习惯，支持分类和提醒
- **打卡功能**: 每日打卡、补卡、图片上传
- **积分系统**: 打卡奖励、连续打卡奖励、积分兑换
- **数据统计**: 个人统计、习惯分析、趋势图表
- **文件上传**: 图片压缩和存储

## 🛠 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0 + Redis 7.0
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT + 微信登录
- **部署**: Docker + Docker Compose + Nginx

## 📦 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- Docker (可选)

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd miniprogram-backend
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和微信参数
```

4. **初始化数据库**
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE habit_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行迁移
alembic upgrade head
```

5. **启动服务**
```bash
python run.py
```

服务将在 http://localhost:8000 启动

### Docker 部署

1. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件
```

2. **启动服务**
```bash
docker-compose up -d
```

## 📚 API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

#### 认证接口
- `POST /api/auth/login` - 微信登录
- `GET /api/auth/me` - 获取用户信息

#### 习惯管理
- `GET /api/habits` - 获取习惯列表
- `POST /api/habits` - 创建习惯
- `PUT /api/habits/{id}` - 更新习惯
- `DELETE /api/habits/{id}` - 删除习惯

#### 打卡功能
- `GET /api/checkins` - 获取打卡记录
- `POST /api/checkins` - 创建打卡
- `POST /api/checkins/makeup` - 补卡
- `GET /api/checkins/calendar/{habit_id}` - 获取日历

#### 统计分析
- `GET /api/statistics/overview` - 用户统计概览
- `GET /api/statistics/habits` - 习惯统计
- `GET /api/statistics/daily` - 每日统计
- `GET /api/statistics/trends` - 趋势数据

#### 积分系统
- `GET /api/points/summary` - 积分概览
- `GET /api/points/history` - 积分记录
- `GET /api/points/rewards` - 可兑换奖励
- `POST /api/points/exchange` - 积分兑换

#### 文件上传
- `POST /api/upload/image` - 上传图片

## 🗄 数据库设计

### 主要表结构

- `users` - 用户表
- `habits` - 习惯表
- `checkins` - 打卡记录表
- `point_records` - 积分记录表

详细设计参考 `技术方案.md`

## 🎯 积分规则

- 每日打卡：+10 积分
- 连续 7 天：+50 积分奖励
- 连续 30 天：+200 积分奖励
- 月度完成率 100%：+300 积分奖励
- 补卡功能：-20 积分

## 🔧 配置说明

### 环境变量

```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/habit_tracker
REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 微信配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# 文件上传配置
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB

# 环境配置
ENVIRONMENT=development
DEBUG=True
```

## 🚀 部署指南

### 生产环境部署

1. **准备服务器**
   - Ubuntu 20.04+ 或 CentOS 8+
   - 2核4G内存起步
   - Docker 和 Docker Compose

2. **配置域名和 SSL**
   - 配置域名解析
   - 申请 SSL 证书
   - 更新 nginx.conf

3. **部署应用**
```bash
# 克隆代码
git clone <repository-url>
cd miniprogram-backend

# 配置环境变量
cp .env.example .env
vim .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 微信小程序配置

1. **服务器域名配置**
   - 登录微信公众平台
   - 进入小程序后台 -> 开发 -> 开发设置
   - 配置服务器域名：`https://your-domain.com`

2. **接口权限**
   - 确保开通必要的接口权限
   - 配置业务域名（如需要）

## 🔍 监控和维护

### 日志管理
- 应用日志：`logs/app_YYYYMMDD.log`
- 访问日志：nginx 访问日志
- 错误日志：应用和 nginx 错误日志

### 数据备份
```bash
# 数据库备份
docker exec mysql mysqldump -u root -p habit_tracker > backup_$(date +%Y%m%d).sql

# 文件备份
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### 性能监控
- 使用 `docker stats` 监控容器资源使用
- 配置 Redis 监控
- 设置数据库慢查询日志

## 🤝 开发指南

### 代码结构
```
app/
├── api/          # API 路由
├── models/       # 数据模型
├── schemas/      # Pydantic 模型
├── services/     # 业务逻辑
├── utils/        # 工具函数
├── config.py     # 配置
├── database.py   # 数据库连接
└── main.py       # 应用入口
```

### 开发规范
- 遵循 PEP 8 代码规范
- 使用类型注解
- 编写单元测试
- 提交前运行代码检查

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
miniprogram-backend to support it
