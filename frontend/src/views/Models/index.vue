<template>
  <div class="models-management">
    <a-page-header title="模型管理" subtitle="管理可用的 AI 模型" />

    <!-- 操作栏 -->
    <a-card class="toolbar-card" :bordered="false">
      <div class="toolbar-top">
        <a-space :size="12" wrap>
          <a-button type="primary" shape="round" :loading="syncing" @click="handleSync">
            <template #icon>
              <icon-sync />
            </template>
            同步模型
          </a-button>
          <a-button
            shape="round"
            :type="selectedIds.length ? 'primary' : 'outline'"
            :disabled="selectedIds.length === 0"
            @click="handleBatchEnable"
          >
            批量启用
          </a-button>
          <a-button
            shape="round"
            status="danger"
            :disabled="selectedIds.length === 0"
            @click="handleBatchDisable"
          >
            批量禁用
          </a-button>
        </a-space>
        <div v-if="models.length" class="toolbar-summary">
          已选 {{ selectedIds.length }} 个 / 当前页 {{ models.length }} 个
        </div>
      </div>

      <div class="toolbar-bottom">
        <a-space :size="12" wrap>
          <a-select
            v-model="filters.is_free"
            placeholder="筛选"
            allow-clear
            style="width: 140px"
            @change="loadModels"
          >
            <a-option :value="true"> 仅免费 </a-option>
            <a-option :value="false"> 付费 </a-option>
          </a-select>
          <a-select
            v-model="filters.enabled_only"
            placeholder="状态"
            allow-clear
            style="width: 140px"
            @change="loadModels"
          >
            <a-option :value="true"> 已启用 </a-option>
            <a-option :value="false"> 已禁用 </a-option>
          </a-select>
        </a-space>
      </div>
    </a-card>

    <!-- 模型列表 -->
    <a-card class="models-table-card" :bordered="false" style="margin-top: 16px">
      <a-table
        :columns="columns"
        :data="models"
        :loading="loading"
        :pagination="pagination"
        :row-selection="rowSelection"
        :scroll="{ y: tableScrollY }"
        row-key="id"
        @page-change="handlePageChange"
      >
        <template #name="{ record }">
          <div>
            <div style="font-weight: 500">
              {{ record.name }}
            </div>
            <div style="font-size: 12px; color: #86909c">
              {{ record.id }}
            </div>
          </div>
        </template>

        <template #pricing="{ record }">
          <div v-if="record.pricing_prompt || record.pricing_completion">
            <div v-if="record.pricing_prompt">
              输入: ${{ (record.pricing_prompt * 1000).toFixed(4) }}/1K
            </div>
            <div v-if="record.pricing_completion">
              输出: ${{ (record.pricing_completion * 1000).toFixed(4) }}/1K
            </div>
          </div>
          <span v-else>-</span>
        </template>

        <template #features="{ record }">
          <a-space>
            <a-tag v-if="record.is_free" color="green"> 免费 </a-tag>
            <a-tag v-if="record.supports_vision" color="blue"> 视觉 </a-tag>
            <a-tag v-if="record.supports_function_calling" color="purple"> 函数 </a-tag>
          </a-space>
        </template>

        <template #is_enabled="{ record }">
          <a-switch
            :model-value="record.is_enabled"
            @change="(value: boolean) => handleToggle(record, value)"
          />
        </template>

        <template #synced_at="{ record }">
          {{ record.synced_at ? new Date(record.synced_at).toLocaleString() : '-' }}
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconSync } from '@arco-design/web-vue/es/icon'
import {
  syncModels,
  getAdminModels,
  enableModel,
  disableModel,
  batchUpdateModels,
  type Model
} from '@/api/adminModels'

const loading = ref(false)
const syncing = ref(false)
const models = ref<Model[]>([])
const selectedIds = ref<string[]>([])

const filters = reactive({
  is_free: undefined as boolean | undefined,
  enabled_only: undefined as boolean | undefined
})

const pagination = reactive({
  current: 1,
  pageSize: 50,
  total: 0,
  showTotal: true
})

const columns = [
  { title: '模型名称', slotName: 'name', width: 300 },
  { title: '提供商', dataIndex: 'provider', width: 120 },
  { title: '上下文长度', dataIndex: 'context_length', width: 120 },
  { title: '定价', slotName: 'pricing', width: 180 },
  { title: '特性', slotName: 'features', width: 200 },
  { title: '启用', slotName: 'is_enabled', width: 100, align: 'center' },
  { title: '同步时间', slotName: 'synced_at', width: 180 }
]

// Row selection 配置
const rowSelection = reactive({
  type: 'checkbox',
  selectedRowKeys: [],
  onChange: (selectedRowKeys: string[]) => {
    selectedIds.value = selectedRowKeys
  }
})

const tableScrollY = 520

// 加载模型列表
const loadModels = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      limit: pagination.pageSize,
      is_free: filters.is_free,
      enabled_only: filters.enabled_only
    }

    const response: any = await getAdminModels(params)
    models.value = response.data
    pagination.total = response.pagination.total
  } catch (error) {
    console.error('Failed to load models:', error)
    Message.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

// 同步模型
const handleSync = async () => {
  syncing.value = true
  try {
    const response: any = await syncModels()
    Message.success(response.message || '同步成功')
    await loadModels()
  } catch (error: any) {
    console.error('Failed to sync models:', error)
    Message.error(error?.response?.data?.detail || '同步失败')
  } finally {
    syncing.value = false
  }
}

// 切换启用状态
const handleToggle = async (record: Model, enabled: boolean) => {
  try {
    if (enabled) {
      await enableModel(record.id)
      Message.success('已启用')
    } else {
      await disableModel(record.id)
      Message.success('已禁用')
    }
    await loadModels()
  } catch (error) {
    console.error('Failed to toggle model:', error)
    Message.error('操作失败')
  }
}

// 批量启用
const handleBatchEnable = async () => {
  try {
    const response: any = await batchUpdateModels(selectedIds.value, true)
    Message.success(response.message || '批量启用成功')
    selectedIds.value = []
    await loadModels()
  } catch (error) {
    console.error('Failed to batch enable:', error)
    Message.error('批量启用失败')
  }
}

// 批量禁用
const handleBatchDisable = async () => {
  try {
    const response: any = await batchUpdateModels(selectedIds.value, false)
    Message.success(response.message || '批量禁用成功')
    selectedIds.value = []
    await loadModels()
  } catch (error) {
    console.error('Failed to batch disable:', error)
    Message.error('批量禁用失败')
  }
}

// 分页变化
const handlePageChange = (page: number) => {
  pagination.current = page
  loadModels()
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.models-management {
  padding: 0;
}

.toolbar-card {
  margin-bottom: 16px;
}

.toolbar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toolbar-summary {
  font-size: 12px;
  color: var(--color-text-2);
}

.toolbar-bottom {
  margin-top: 16px;
}

.models-table-card {
  /* 通过表格的 scroll.y 控制列表高度统一 */
}
</style>
