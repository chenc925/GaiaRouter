<template>
  <div class="stats-dashboard">
    <a-page-header title="数据统计" />

    <a-card>
      <a-space
        direction="vertical"
        :size="16"
        style="width: 100%"
      >
        <a-space>
          <a-range-picker
            v-model="dateRange"
            style="width: 300px"
            @change="handleDateChange"
          />
          <a-select
            v-model="groupBy"
            placeholder="分组方式"
            style="width: 150px"
            @change="handleSearch"
          >
            <a-option value="day">
              按日
            </a-option>
            <a-option value="week">
              按周
            </a-option>
            <a-option value="month">
              按月
            </a-option>
          </a-select>
          <a-button
            type="primary"
            @click="handleSearch"
          >
            查询
          </a-button>
        </a-space>

        <a-row
          v-if="statsStore.globalStats"
          :gutter="16"
        >
          <a-col :span="6">
            <a-statistic
              title="总请求数"
              :value="statsStore.globalStats.summary.total_requests"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="总 Token 数"
              :value="statsStore.globalStats.summary.total_tokens"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="总费用"
              :value="statsStore.globalStats.summary.total_cost"
              :precision="2"
              prefix="¥"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="活跃 API Key 数"
              :value="statsStore.globalStats.summary.active_keys"
            />
          </a-col>
        </a-row>

        <div
          v-if="statsStore.globalStats?.by_provider"
          style="margin-top: 24px"
        >
          <h3>按提供商统计</h3>
          <a-table
            :columns="providerColumns"
            :data="statsStore.globalStats.by_provider"
            :pagination="false"
          />
        </div>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStatsStore } from '@/stores/stats'
import dayjs from 'dayjs'

const statsStore = useStatsStore()

const dateRange = ref<[Date, Date] | null>(null)
const groupBy = ref('day')

const providerColumns = [
  { title: '提供商', dataIndex: 'provider' },
  { title: '请求数', dataIndex: 'requests' },
  { title: 'Token 数', dataIndex: 'tokens' },
  { title: '费用', dataIndex: 'cost', slotName: 'cost' }
]

const handleDateChange = () => {
  handleSearch()
}

const handleSearch = async () => {
  const params: any = {
    group_by: groupBy.value
  }

  if (dateRange.value) {
    params.start_date = dayjs(dateRange.value[0]).toISOString()
    params.end_date = dayjs(dateRange.value[1]).toISOString()
  }

  await statsStore.fetchGlobalStats(params)
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.stats-dashboard {
  padding: 0;
}
</style>

