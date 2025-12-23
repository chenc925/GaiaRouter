# GaiaRouter 管理后台

基于 Vue 3 + Arco Design Vue 的后台管理界面。

## 技术栈

- Vue 3 (Composition API)
- TypeScript
- Vite
- Arco Design Vue
- Pinia
- Vue Router
- Axios
- ECharts

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发环境运行

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口封装
│   ├── assets/            # 静态资源
│   ├── components/        # 公共组件
│   ├── views/             # 页面组件
│   ├── stores/            # Pinia 状态管理
│   ├── router/            # 路由配置
│   ├── utils/             # 工具函数
│   ├── types/             # TypeScript 类型定义
│   ├── App.vue
│   └── main.ts
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 功能模块

- 组织管理（CRUD）
- API Key 管理（CRUD）
- 数据统计可视化
- 用户认证

## 环境变量

创建 `.env.development` 和 `.env.production` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 开发说明

1. 确保后端 API 服务已启动（默认端口 8000）
2. 使用 API Key 进行登录
3. 所有 API 请求都需要在 Header 中包含 `Authorization: Bearer {api_key}`
