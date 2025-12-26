<template>
  <div class="api-key-stats">
    <a-page-header title="API Key 统计" @back="$router.push('/stats')" />

    <a-card>
      <a-space direction="vertical" :size="16" style="width: 100%">
        <a-space>
          <a-range-picker v-model="dateRange" style="width: 300px" @change="handleDateChange" />
          <a-select
            v-model="groupBy"
            placeholder="分组方式"
            style="width: 150px"
            @change="handleSearch"
          >
            <a-option value="day"> 按日 </a-option>
            <a-option value="week"> 按周 </a-option>
            <a-option value="month"> 按月 </a-option>
          </a-select>
          <a-button type="primary" @click="handleSearch"> 查询 </a-button>
        </a-space>

        <div v-if="stats">
          <a-row :gutter="16">
            <a-col :span="6">
              <a-statistic title="总请求数" :value="stats.summary.total_requests" />
            </a-col>
            <a-col :span="6">
              <a-statistic title="总 Token 数" :value="stats.summary.total_tokens" />
            </a-col>
            <a-col :span="6">
              <a-statistic
                title="总费用"
                :value="stats.summary.total_cost"
                :precision="2"
                prefix="¥"
              />
            </a-col>
          </a-row>

          <div v-if="stats.by_date" style="margin-top: 24px">
            <h3>按日期统计</h3>
            <a-table :columns="dateColumns" :data="stats.by_date" :pagination="false" />
          </div>
        </div>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useStatsStore } from '@/stores/stats'
import dayjs from 'dayjs'

const route = useRoute()
const statsStore = useStatsStore()

const apiKeyId = computed(() => route.params.id as string)
const stats = computed(() => statsStore.apiKeyStats[apiKeyId.value])

const dateRange = ref<[Date, Date] | null>(null)
const groupBy = ref('day')

const dateColumns = [
  { title: '日期', dataIndex: 'date' },
  { title: '请求数', dataIndex: 'requests' },
  { title: 'Token 数', dataIndex: 'total_tokens' },
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

  await statsStore.fetchApiKeyStats(apiKeyId.value, params)
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.api-key-stats {
  padding: 0;
}
</style>
