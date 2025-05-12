<template>
  <div class="campaign-list">
    <a-card>
      <template #title>
        <div class="card-title">
          <span>广告活动列表</span>
          <a-button type="primary" @click="handleCreate">
            <template #icon><plus-outlined /></template>
            新建活动
          </a-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <a-form layout="inline" :model="searchForm" class="search-form">
        <a-form-item label="活动名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入活动名称" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchForm.status" style="width: 120px">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="active">进行中</a-select-option>
            <a-select-option value="paused">已暂停</a-select-option>
            <a-select-option value="ended">已结束</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">
            <template #icon><search-outlined /></template>
            搜索
          </a-button>
          <a-button style="margin-left: 8px" @click="handleReset">
            <template #icon><reload-outlined /></template>
            重置
          </a-button>
        </a-form-item>
      </a-form>

      <!-- 数据表格 -->
      <a-table
        :columns="columns"
        :data-source="campaigns"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a @click="handleEdit(record)">编辑</a>
              <a-divider type="vertical" />
              <a @click="handleView(record)">查看</a>
              <a-divider type="vertical" />
              <a-popconfirm
                title="确定要删除这个活动吗？"
                @confirm="handleDelete(record)"
              >
                <a class="danger-link">删除</a>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'

const router = useRouter()

// 搜索表单数据
const searchForm = reactive({
  name: '',
  status: ''
})

// 表格列定义
const columns = [
  {
    title: '活动名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '广告主',
    dataIndex: 'advertiser',
    key: 'advertiser'
  },
  {
    title: '预算',
    dataIndex: 'budget',
    key: 'budget'
  },
  {
    title: '消耗',
    dataIndex: 'spend',
    key: 'spend'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status'
  },
  {
    title: '开始时间',
    dataIndex: 'startDate',
    key: 'startDate'
  },
  {
    title: '结束时间',
    dataIndex: 'endDate',
    key: 'endDate'
  },
  {
    title: '操作',
    key: 'action',
    width: 200
  }
]

// 模拟数据
const campaigns = ref([
  {
    id: 1,
    name: '夏季促销活动',
    advertiser: 'ABC公司',
    budget: 10000,
    spend: 5000,
    status: 'active',
    startDate: '2024-05-01',
    endDate: '2024-08-31'
  },
  {
    id: 2,
    name: '新品上市推广',
    advertiser: 'XYZ品牌',
    budget: 20000,
    spend: 15000,
    status: 'paused',
    startDate: '2024-04-01',
    endDate: '2024-07-31'
  }
])

const loading = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 100
})

// 获取状态颜色
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    active: 'green',
    paused: 'orange',
    ended: 'red'
  }
  return colors[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    active: '进行中',
    paused: '已暂停',
    ended: '已结束'
  }
  return texts[status] || status
}

// 处理搜索
const handleSearch = () => {
  console.log('搜索条件：', searchForm)
  // TODO: 实现搜索逻辑
}

// 处理重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.status = ''
  handleSearch()
}

// 处理表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  // TODO: 重新加载数据
}

// 处理新建
const handleCreate = () => {
  router.push('/campaigns/create')
}

// 处理编辑
const handleEdit = (record: any) => {
  router.push(`/campaigns/${record.id}/edit`)
}

// 处理查看
const handleView = (record: any) => {
  router.push(`/campaigns/${record.id}`)
}

// 处理删除
const handleDelete = (record: any) => {
  console.log('删除活动：', record)
  // TODO: 实现删除逻辑
}
</script>

<style lang="less" scoped>
.campaign-list {
  .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 24px;
  }

  .danger-link {
    color: #ff4d4f;
  }
}
</style> 