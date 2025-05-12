# DSP广告管理系统

基于Flask+Vue的DSP（Demand-Side Platform）广告管理系统，采用微服务架构设计，提供广告主管理、广告活动管理、实时投放监控和数据分析等核心功能。

## 系统架构

### 技术栈

* **前端**：Vue 3 + TypeScript + Ant Design Vue Pro
* **后端**：Python Flask + SQLAlchemy + Celery（异步任务）
* **数据库**：MySQL 8.0（事务型数据） + Redis 7（实时计数缓存）
* **安全方案**：JWT认证 + AES数据加密 + 防CSRF过滤

### 系统模块

1. **广告主管理**
   - 资质审核工作流
   - RBAC权限系统
   - 账户资金管理

2. **广告活动管理**
   - 智能投放策略引擎
   - 创意管理功能
   - 预算控制

3. **实时投放监控**
   - 数据看板实现
   - 频次控制模块
   - 阈值告警系统

4. **数据分析模块**
   - OLAP查询优化
   - 归因模型实现
   - 自定义指标解析

## 快速开始

### 环境要求

* Python 3.9+
* Node.js 16+
* MySQL 8.0+
* Redis 7.0+

### 后端安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库连接等信息

# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 运行开发服务器
flask run
```

### 前端安装

```bash
# 安装依赖
cd frontend
npm install

# 运行开发服务器
npm run dev

# 打包生产环境
npm run build
```

## 项目结构

```
dsp-ad-system/
├── backend/                # 后端代码
│   ├── app/                # 主应用
│   │   ├── api/            # API接口
│   │   ├── core/           # 核心模块
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑服务
│   │   └── utils/          # 工具函数
│   ├── config/             # 配置文件
│   ├── migrations/         # 数据库迁移
│   └── tests/              # 测试代码
├── frontend/               # 前端代码
│   ├── public/             # 静态资源
│   └── src/                # 源代码
│       ├── api/            # API请求
│       ├── assets/         # 资源文件
│       ├── components/     # 通用组件
│       ├── layouts/        # 布局组件
│       ├── router/         # 路由配置
│       ├── store/          # 状态管理
│       ├── utils/          # 工具函数
│       └── views/          # 页面组件
└── README.md               # 项目说明
```

## 核心功能实现

### 广告主管理

1. **资质审核工作流**
   - 支持PDF/PNG/JPG格式文件上传
   - 审核状态机（待审/通过/驳回）
   - WebSocket+邮件消息通知

2. **RBAC权限系统**
   - 基于JSON配置的角色权限矩阵
   - 数据隔离中间件实现广告主数据沙箱
   - 完整的操作日志审计功能

### 广告活动管理

1. **智能投放策略引擎**
   - 支持地域+设备+人群的位运算优化查询
   - 灵活的出价算法接口，预留RTB对接扩展

2. **创意管理功能**
   - 多媒体文件分片上传
   - 集成阿里云内容安全API的审核流程
   - 基于权重的创意组合算法

### 实时投放监控

1. **数据看板实现**
   - 使用Redis HyperLogLog的实时指标计算
   - 集成ECharts的可视化组件
   - 可配置的Webhook告警系统

2. **频次控制模块**
   - 基于Redis和Lua脚本的分布式计数器
   - 设备ID+IP哈希的用户曝光指纹算法

### 数据分析模块

1. **OLAP查询优化**
   - 基于ClickHouse的预聚合Cube设计
   - 自定义指标解析器
   - 高性能分页查询优化

2. **归因模型实现**
   - 使用Neo4j存储多触点路径
   - 马尔可夫链归因算法实现

## 性能优化

1. **查询缓存策略**
   - Redis+内存缓存分级设计
   - 热点数据智能预加载

2. **数据库优化**
   - 按广告主ID哈希的分表规则
   - 索引优化和慢查询分析

## 安全加固

1. **防注入保护**
   - 请求参数校验管道
   - SQL注入过滤中间件

2. **频率控制**
   - 基于装饰器的API频率限制

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证。 