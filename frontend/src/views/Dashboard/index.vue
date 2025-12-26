<template>
  <div class="dashboard">
    <a-page-header title="仪表盘" />

    <!-- 顶部统计卡片（全局真实数据） -->
    <a-row :gutter="16" class="stats-cards">
      <a-col :span="6">
        <a-card size="small">
          <a-statistic title="总请求数" :value="totalRequests" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small">
          <a-statistic title="总 Token 数" :value="totalTokens" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small">
          <a-statistic title="总费用" :value="totalCost" :precision="2" prefix="¥" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small">
          <a-statistic title="活跃 API Key 数" :value="activeKeys" />
        </a-card>
      </a-col>
    </a-row>

    <!-- 常用操作（优先展示） -->
    <a-card title="常用操作" class="quick-actions" :bordered="false">
      <a-space class="quick-actions-list" wrap :size="16">
        <a-button type="primary" shape="round" @click="$router.push('/organizations/create')">
          <template #icon>
            <IconUserGroup />
          </template>
          创建组织
        </a-button>
        <a-button type="primary" shape="round" @click="$router.push('/api-keys/create')">
          <template #icon>
            <IconSettings />
          </template>
          创建 API Key
        </a-button>
        <a-button type="primary" shape="round" @click="$router.push('/chat/test')">
          <template #icon>
            <IconMessage />
          </template>
          对话测试
        </a-button>
        <a-button shape="round" @click="$router.push('/models')">
          <template #icon>
            <IconSettings />
          </template>
          模型管理
        </a-button>
        <a-button shape="round" @click="$router.push('/stats')">
          <template #icon>
            <IconBarChart />
          </template>
          查看统计
        </a-button>
      </a-space>
    </a-card>

    <!-- 图表区域（真实数据：按提供商统计） -->
    <a-row :gutter="16" class="charts-row">
      <a-col :span="16" :xs="24">
        <a-card title="按提供商请求数（最近 30 天）" :bordered="false" class="chart-card">
          <div class="chart-body">
            <VChart :option="requestsByProviderOption" autoresize />
          </div>
        </a-card>
      </a-col>
      <a-col :span="8" :xs="24">
        <a-card title="按提供商 Token / 费用" :bordered="false" class="chart-card">
          <div class="chart-body">
            <VChart :option="tokensByProviderOption" autoresize />
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useStatsStore } from '@/stores/stats'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import type { ProviderStats } from '@/types/stats'
import {
  IconUserGroup,
  IconMessage,
  IconSettings,
  IconBarChart
} from '@arco-design/web-vue/es/icon'

use([CanvasRenderer, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent])

const statsStore = useStatsStore()

const globalStats = computed(() => statsStore.globalStats)
const summary = computed(() => globalStats.value?.summary)
const providerStats = computed<ProviderStats[]>(() => globalStats.value?.by_provider || [])

const totalRequests = computed(() => summary.value?.total_requests ?? 0)
const totalTokens = computed(() => summary.value?.total_tokens ?? 0)
const totalCost = computed(() => summary.value?.total_cost ?? 0)
const activeKeys = computed(() => summary.value?.active_keys ?? 0)

const requestsByProviderOption = computed<any>(() => {
  const providers = providerStats.value.map(p => p.provider || '未知')
  const requests = providerStats.value.map(p => p.requests || 0)

  return {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: 24,
      right: 16,
      top: 40,
      bottom: 40
    },
    xAxis: {
      type: 'category',
      data: providers,
      axisLabel: {
        rotate: providers.length > 4 ? 30 : 0
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '请求数',
        type: 'bar',
        barWidth: 24,
        itemStyle: {
          color: '#165DFF'
        },
        data: requests
      }
    ]
  }
})

const tokensByProviderOption = computed<any>(() => {
  const providers = providerStats.value.map(p => p.provider || '未知')
  const tokens = providerStats.value.map(p => p.total_tokens || 0)
  const costs = providerStats.value.map(p => p.cost || 0)

  return {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['Token 数', '费用']
    },
    grid: {
      left: 24,
      right: 40,
      top: 40,
      bottom: 40
    },
    xAxis: {
      type: 'category',
      data: providers,
      axisLabel: {
        rotate: providers.length > 4 ? 30 : 0
      }
    },
    yAxis: [
      {
        type: 'value',
        name: 'Token 数'
      },
      {
        type: 'value',
        name: '费用',
        axisLabel: {
          formatter: '¥{value}'
        }
      }
    ],
    series: [
      {
        name: 'Token 数',
        type: 'bar',
        itemStyle: {
          color: '#00B96B'
        },
        data: tokens
      },
      {
        name: '费用',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        itemStyle: {
          color: '#F97316'
        },
        data: costs
      }
    ]
  }
})

onMounted(() => {
  // 默认拉取最近 30 天的全局统计（后端会设置默认时间范围）
  statsStore.fetchGlobalStats({ group_by: 'provider' })
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-cards {
  margin-top: 24px;
  margin-bottom: 16px;
}

.charts-row {
  margin-bottom: 16px;
}

.chart-card {
  height: 100%;
}

.chart-body {
  height: 320px;
}

.quick-actions {
  margin-top: 8px;
}

.quick-actions-list :deep(.arco-btn) {
  padding: 0 18px;
  font-size: 13px;
}

.quick-actions-list :deep(.arco-btn-primary) {
  box-shadow: 0 6px 16px rgba(22, 93, 255, 0.16);
}

@media (max-width: 768px) {
  .stats-cards {
    margin-top: 16px;
  }

  .chart-body {
    height: 260px;
  }
}
</style>
