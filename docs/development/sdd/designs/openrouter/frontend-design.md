# 前端设计文档

## 概述

本文档详细描述 GaiaRouter 后台管理界面的前端设计，包括技术选型、架构设计、页面设计等。

## 技术栈

### 核心框架

- **Vue 3**：使用 Composition API，提供更好的类型推断和代码组织
- **TypeScript**：提供类型安全，提高代码质量
- **Vite**：快速的前端构建工具，提供优秀的开发体验

### UI 组件库

- **Arco Design Vue**：企业级 UI 组件库，提供丰富的组件和良好的设计规范

### 状态管理

- **Pinia**：Vue 3 官方推荐的状态管理库，替代 Vuex

### 路由

- **Vue Router**：Vue 官方路由管理器

### HTTP 客户端

- **Axios**：基于 Promise 的 HTTP 客户端

### 图表库

- **ECharts**：强大的数据可视化库，支持多种图表类型

### 工具库

- **dayjs**：轻量级日期处理库
- **lodash-es**：工具函数库（按需引入）

## 项目结构

```
frontend/
├── public/                 # 静态资源
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── api/               # API 接口封装
│   │   ├── organizations.ts
│   │   ├── apiKeys.ts
│   │   ├── stats.ts
│   │   ├── auth.ts
│   │   └── index.ts
│   ├── assets/            # 资源文件
│   │   ├── images/
│   │   └── styles/
│   ├── components/        # 公共组件
│   │   ├── Layout/
│   │   │   ├── MainLayout.vue
│   │   │   ├── Header.vue
│   │   │   └── Sidebar.vue
│   │   ├── Table/
│   │   │   └── DataTable.vue
│   │   ├── Form/
│   │   │   └── DynamicForm.vue
│   │   └── Chart/
│   │       ├── LineChart.vue
│   │       ├── BarChart.vue
│   │       └── PieChart.vue
│   ├── views/             # 页面组件
│   │   ├── Dashboard/
│   │   │   └── index.vue
│   │   ├── Organizations/
│   │   │   ├── List.vue
│   │   │   ├── Detail.vue
│   │   │   └── Form.vue
│   │   ├── ApiKeys/
│   │   │   ├── List.vue
│   │   │   ├── Detail.vue
│   │   │   └── Form.vue
│   │   └── Stats/
│   │       ├── Dashboard.vue
│   │       ├── OrganizationStats.vue
│   │       └── ApiKeyStats.vue
│   ├── stores/            # Pinia 状态管理
│   │   ├── auth.ts
│   │   ├── organizations.ts
│   │   ├── apiKeys.ts
│   │   └── stats.ts
│   ├── router/            # 路由配置
│   │   ├── index.ts
│   │   └── guards.ts      # 路由守卫
│   ├── utils/             # 工具函数
│   │   ├── request.ts     # Axios 封装
│   │   ├── format.ts      # 格式化工具
│   │   ├── validate.ts    # 验证工具
│   │   └── constants.ts   # 常量定义
│   ├── types/             # TypeScript 类型定义
│   │   ├── api.ts
│   │   ├── organization.ts
│   │   ├── apiKey.ts
│   │   └── stats.ts
│   ├── App.vue            # 根组件
│   └── main.ts            # 入口文件
├── .env                   # 环境变量
├── .env.development       # 开发环境变量
├── .env.production        # 生产环境变量
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## 页面设计

### 1. 登录页面

- 用户名/密码登录
- API Key 登录（可选）
- 记住我功能
- 忘记密码（可选）

### 2. 仪表盘（Dashboard）

- 全局统计概览卡片：
  - 总组织数
  - 总 API Key 数
  - 今日请求数
  - 今日 Token 使用量
  - 今日费用
- 最近活动列表
- 快速操作入口

### 3. 组织管理

#### 3.1 组织列表

- 表格展示：
  - 组织 ID
  - 组织名称
  - 状态
  - API Key 数量
  - 月度请求数
  - 月度 Token 使用量
  - 月度费用
  - 创建时间
  - 操作（查看、编辑、删除）
- 搜索框（按名称搜索）
- 筛选器（按状态筛选）
- 分页器
- 创建组织按钮

#### 3.2 组织详情

- 基本信息：
  - 组织 ID
  - 组织名称
  - 描述
  - 管理员
  - 状态
  - 创建时间
  - 更新时间
- 使用限制：
  - 月度请求次数限制
  - 月度 Token 限制
  - 月度费用限制
- 关联的 API Keys 列表
- 使用统计图表
- 操作按钮（编辑、删除）

#### 3.3 创建/编辑组织

- 表单字段：
  - 组织名称（必填）
  - 描述（可选）
  - 管理员用户 ID（可选）
  - 月度请求次数限制（可选）
  - 月度 Token 限制（可选）
  - 月度费用限制（可选）
- 表单验证
- 提交按钮
- 取消按钮

### 4. API Key 管理

#### 4.1 API Key 列表

- 表格展示：
  - ID
  - 名称
  - **API Key（隐藏显示：`sk-****...****`）**
  - 描述
  - 状态（标签显示：active/inactive/expired）
  - 最后使用时间
  - 操作（查看、删除）
- 搜索框（按名称搜索）
- 筛选器（按组织、状态筛选）
- 分页器
- 创建 API Key 按钮
- **安全功能**：
  - API Key 列显示隐藏格式（前4位 + 20个* + 后4位）
  - 每行提供"复制"按钮（复制完整 key）
  - 后端实际返回 `null`，前端从缓存或状态中获取

#### 4.2 API Key 详情

- 基本信息：
  - API Key ID
  - 名称
  - 描述
  - **API Key（隐藏显示：`sk-****...****`）**
  - 所属组织
  - 权限列表（标签显示）
  - 状态（标签显示）
  - 创建时间
  - 过期时间
  - 最后使用时间
- **安全功能**：
  - API Key 隐藏显示（前4位 + 20个* + 后4位）
  - 提供"复制 API Key"按钮
  - 后端返回 `null`，前端显示隐藏格式
- 使用统计图表
- 操作按钮（删除、查看统计）

#### 4.3 创建/编辑 API Key

**实际实现**（简化版本）：

- 表单字段：
  - 所属组织（必填，下拉选择）- **唯一需要用户输入的字段**
- 自动生成字段（无需用户输入）：
  - 名称：自动生成为 `{组织名} API Key`
  - 描述：自动生成为 `Auto-generated API Key for {组织名}`
  - 权限：固定为 `["read", "write"]`
  - 过期时间：固定为 `null`（永不过期）
- 创建成功后显示完整 API Key（**仅一次，使用 textarea 展示**）
  - 显示复制按钮（带图标）
  - 显示"返回列表"按钮
  - 警告提示：请妥善保存，仅显示一次
- 业务规则：
  - **一个组织只能创建一个活跃的 API Key**
  - 如果组织已有 API Key，禁用"分配 API Key"按钮
- 编辑功能：**不支持**（需删除后重新创建）

**安全显示**：

- **列表页面**：API Key 隐藏显示为 `sk-****...****` 格式
  - 仅显示前4个字符和后4个字符
  - 中间用 20 个 `*` 替代
  - 提供"复制"按钮（复制完整 key）
- **详情页面**：同列表页面，隐藏显示
- **创建成功**：显示完整 API Key（唯一机会）

### 5. 统计页面

#### 5.1 全局统计

- 统计概览卡片
- 时间范围选择器
- 图表展示：
  - 请求趋势图（折线图）
  - Token 使用趋势图（折线图）
  - 费用趋势图（折线图）
  - 模型使用分布（饼图）
  - 提供商使用分布（饼图）
- 数据导出按钮

#### 5.2 组织统计

- 组织选择器
- 统计概览卡片
- 时间范围选择器
- 图表展示（同全局统计）
- 数据导出按钮

#### 5.3 API Key 统计

- API Key 选择器
- 统计概览卡片
- 时间范围选择器
- 图表展示（同全局统计）
- 数据导出按钮

## 组件设计

### 1. Layout 组件

#### MainLayout

- 顶部导航栏
- 左侧菜单栏
- 主内容区域
- 响应式布局

#### Header

- Logo
- 导航菜单（可选）
- 用户信息
- 退出按钮

#### Sidebar

- 菜单项：
  - 仪表盘
  - 组织管理
  - API Key 管理
  - 统计
  - 系统设置（可选）
- 菜单折叠/展开
- 当前路由高亮

### 2. Chart 组件

#### LineChart

- 折线图组件
- 支持时间序列数据
- 支持多系列数据
- 支持缩放和拖拽

#### BarChart

- 柱状图组件
- 支持横向/纵向
- 支持堆叠
- 支持分组

#### PieChart

- 饼图组件
- 支持环形图
- 支持图例
- 支持标签显示

### 3. Table 组件

#### DataTable

- 表格组件
- 支持排序
- 支持筛选
- 支持分页
- 支持选择
- 支持自定义列

## 状态管理设计

### Auth Store

```typescript
interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
}

interface AuthActions {
  login(credentials): Promise<void>;
  logout(): void;
  checkAuth(): Promise<void>;
}
```

### Organization Store

```typescript
interface OrganizationState {
  organizations: Organization[];
  currentOrganization: Organization | null;
  loading: boolean;
  pagination: Pagination;
}

interface OrganizationActions {
  fetchOrganizations(params): Promise<void>;
  fetchOrganization(id): Promise<void>;
  createOrganization(data): Promise<void>;
  updateOrganization(id, data): Promise<void>;
  deleteOrganization(id): Promise<void>;
}
```

### ApiKey Store

```typescript
interface ApiKeyState {
  apiKeys: ApiKey[];
  currentApiKey: ApiKey | null;
  loading: boolean;
  pagination: Pagination;
}

interface ApiKeyActions {
  fetchApiKeys(params): Promise<void>;
  fetchApiKey(id): Promise<void>;
  createApiKey(data): Promise<void>;
  updateApiKey(id, data): Promise<void>;
  deleteApiKey(id): Promise<void>;
}
```

### Stats Store

```typescript
interface StatsState {
  globalStats: GlobalStats | null;
  organizationStats: Record<string, OrganizationStats>;
  apiKeyStats: Record<string, ApiKeyStats>;
  loading: boolean;
}

interface StatsActions {
  fetchGlobalStats(params): Promise<void>;
  fetchOrganizationStats(id, params): Promise<void>;
  fetchApiKeyStats(id, params): Promise<void>;
}
```

## API 封装设计

### Request 封装

```typescript
// utils/request.ts
class ApiClient {
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 30000,
    });

    // 请求拦截器
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // 添加认证头
        const token = useAuthStore().token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      (response) => response.data,
      (error) => {
        // 统一错误处理
        if (error.response?.status === 401) {
          // 跳转到登录页
          router.push("/login");
        }
        return Promise.reject(error);
      }
    );
  }

  get<T>(url: string, params?: any): Promise<T>;
  post<T>(url: string, data?: any): Promise<T>;
  put<T>(url: string, data?: any): Promise<T>;
  patch<T>(url: string, data?: any): Promise<T>;
  delete<T>(url: string): Promise<T>;
}
```

### API 接口封装

```typescript
// api/organizations.ts
export const organizationsApi = {
  getList: (params: ListParams) =>
    apiClient.get<OrganizationListResponse>("/v1/organizations", { params }),

  getDetail: (id: string) =>
    apiClient.get<Organization>(`/v1/organizations/${id}`),

  create: (data: CreateOrganizationRequest) =>
    apiClient.post<Organization>("/v1/organizations", data),

  update: (id: string, data: UpdateOrganizationRequest) =>
    apiClient.patch<Organization>(`/v1/organizations/${id}`, data),

  delete: (id: string) => apiClient.delete(`/v1/organizations/${id}`),

  getStats: (id: string, params: StatsParams) =>
    apiClient.get<OrganizationStats>(`/v1/organizations/${id}/stats`, {
      params,
    }),
};
```

## 路由设计

```typescript
const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/",
    component: () => import("@/components/Layout/MainLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "Dashboard",
        component: () => import("@/views/Dashboard/index.vue"),
      },
      {
        path: "organizations",
        name: "Organizations",
        component: () => import("@/views/Organizations/List.vue"),
      },
      {
        path: "organizations/:id",
        name: "OrganizationDetail",
        component: () => import("@/views/Organizations/Detail.vue"),
      },
      {
        path: "organizations/:id/edit",
        name: "OrganizationEdit",
        component: () => import("@/views/Organizations/Form.vue"),
      },
      {
        path: "api-keys",
        name: "ApiKeys",
        component: () => import("@/views/ApiKeys/List.vue"),
      },
      {
        path: "api-keys/:id",
        name: "ApiKeyDetail",
        component: () => import("@/views/ApiKeys/Detail.vue"),
      },
      {
        path: "api-keys/:id/edit",
        name: "ApiKeyEdit",
        component: () => import("@/views/ApiKeys/Form.vue"),
      },
      {
        path: "stats",
        name: "Stats",
        component: () => import("@/views/Stats/Dashboard.vue"),
      },
      {
        path: "stats/organizations/:id",
        name: "OrganizationStats",
        component: () => import("@/views/Stats/OrganizationStats.vue"),
      },
      {
        path: "stats/api-keys/:id",
        name: "ApiKeyStats",
        component: () => import("@/views/Stats/ApiKeyStats.vue"),
      },
    ],
  },
];
```

## 性能优化

1. **代码分割**：使用动态导入，按需加载组件
2. **虚拟滚动**：大数据量列表使用虚拟滚动
3. **图表优化**：按需加载图表库，使用懒加载
4. **缓存策略**：合理使用 Pinia 缓存，减少 API 请求
5. **图片优化**：使用 WebP 格式，懒加载图片

## 安全考虑

1. **认证**：使用 JWT Token，存储在 localStorage
2. **XSS 防护**：使用 Vue 的内置 XSS 防护
3. **CSRF 防护**：使用 CSRF Token（如果需要）
4. **敏感信息**：不在前端存储敏感信息
5. **API 安全**：所有 API 请求都需要认证
6. **API Key 安全处理**（重要）：
   - **创建时**：显示完整 API Key（仅一次），使用 textarea 展示
   - **存储策略**：
     - ❌ **不要**在 localStorage/sessionStorage 中存储完整 API Key
     - ❌ **不要**在 Pinia store 中长期保存完整 API Key
     - ✅ **仅在**创建成功后临时保存用于展示
   - **查询时**：
     - 后端返回 `key: null`
     - 前端显示隐藏格式：`sk-****...****`（前4位 + 20个* + 后4位）
   - **复制功能**：
     - 列表和详情页：如果后端返回 `null`，复制按钮应禁用或提示无法复制
     - 创建页：复制完整 key
   - **用户提示**：
     - 创建时明确提示"仅显示一次，请妥善保存"
     - 列表/详情页明确说明"出于安全考虑，不显示完整 key"
7. **后端协同**：
   - 列表和详情 API 不返回完整 key（返回 `null`）
   - 仅创建 API 返回完整 key（一次性）
   - 实现多层防护：后端不返回 + 前端隐藏显示

## 响应式设计

- **桌面端**：>= 1200px，完整布局
- **平板端**：768px - 1199px，适配布局
- **移动端**：< 768px，移动端优化布局

## 浏览器支持

- Chrome（最新 2 个版本）
- Firefox（最新 2 个版本）
- Safari（最新 2 个版本）
- Edge（最新 2 个版本）
