<template>
  <div class="organizations-list">
    <a-page-header title="组织管理">
      <template #extra>
        <a-button
          type="primary"
          @click="$router.push('/organizations/create')"
        >
          <template #icon>
            <IconPlus />
          </template>
          创建组织
        </a-button>
      </template>
    </a-page-header>

    <a-card>
      <a-space
        direction="vertical"
        :size="16"
        style="width: 100%"
      >
        <a-space>
          <a-input
            v-model="searchText"
            placeholder="搜索组织名称"
            allow-clear
            style="width: 300px"
            @press-enter="handleSearch"
          />
          <a-select
            v-model="statusFilter"
            placeholder="状态筛选"
            allow-clear
            style="width: 150px"
            @change="handleSearch"
          >
            <a-option value="active">
              活跃
            </a-option>
            <a-option value="inactive">
              停用
            </a-option>
          </a-select>
          <a-button
            type="primary"
            @click="handleSearch"
          >
            搜索
          </a-button>
        </a-space>

        <a-table
          :columns="columns"
          :data="organizationStore.organizations"
          :loading="organizationStore.loading"
          :pagination="paginationConfig"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        >
          <template #status="{ record }">
            <a-tag :color="record.status === 'active' ? 'green' : 'red'">
              {{ record.status === 'active' ? '活跃' : '停用' }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button
                type="text"
                size="small"
                @click="handleView(record.id)"
              >
                查看
              </a-button>
              <a-button
                type="text"
                size="small"
                @click="handleEdit(record.id)"
              >
                编辑
              </a-button>
              <a-popconfirm
                content="确定要删除这个组织吗？"
                @ok="handleDelete(record.id)"
              >
                <a-button
                  type="text"
                  size="small"
                  status="danger"
                >
                  删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </a-table>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useOrganizationStore } from '@/stores/organizations'
import { Message } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'

const router = useRouter()
const organizationStore = useOrganizationStore()

const searchText = ref('')
const statusFilter = ref<string>()

const columns = [
  { title: 'ID', dataIndex: 'id', width: 200 },
  { title: '名称', dataIndex: 'name' },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', width: 180 },
  { title: '操作', slotName: 'operations', width: 200, fixed: 'right' }
]

const paginationConfig = computed(() => ({
  current: organizationStore.pagination.page,
  pageSize: organizationStore.pagination.limit,
  total: organizationStore.pagination.total,
  showTotal: true,
  showPageSize: true
}))

const handleSearch = () => {
  organizationStore.fetchOrganizations({
    page: 1,
    limit: organizationStore.pagination.limit,
    search: searchText.value || undefined,
    status: statusFilter.value
  })
}

const handlePageChange = (page: number) => {
  organizationStore.fetchOrganizations({
    page,
    limit: organizationStore.pagination.limit,
    search: searchText.value || undefined,
    status: statusFilter.value
  })
}

const handlePageSizeChange = (size: number) => {
  organizationStore.fetchOrganizations({
    page: 1,
    limit: size,
    search: searchText.value || undefined,
    status: statusFilter.value
  })
}

const handleView = (id: string) => {
  router.push(`/organizations/${id}`)
}

const handleEdit = (id: string) => {
  router.push(`/organizations/${id}/edit`)
}

const handleDelete = async (id: string) => {
  try {
    await organizationStore.deleteOrganization(id)
    Message.success('删除成功')
    handleSearch()
  } catch (error) {
    Message.error('删除失败')
  }
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.organizations-list {
  padding: 0;
}
</style>

