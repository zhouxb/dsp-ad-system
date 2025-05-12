<template>
  <div>
    <div class="page-header">
      <h2>广告主管理</h2>
      
      <div class="page-header-actions">
        <a-button type="primary" @click="showCreateModal">
          <plus-outlined /> 新建广告主
        </a-button>
      </div>
    </div>
    
    <!-- 搜索区域 -->
    <a-card class="search-card" :bordered="false">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="广告主名称">
          <a-input v-model:value="searchForm.name" placeholder="广告主名称" allow-clear />
        </a-form-item>
        
        <a-form-item label="状态">
          <a-select
            v-model:value="searchForm.status"
            style="width: 160px"
            placeholder="选择状态"
            allow-clear
          >
            <a-select-option value="pending">待审核</a-select-option>
            <a-select-option value="approved">已通过</a-select-option>
            <a-select-option value="rejected">已驳回</a-select-option>
            <a-select-option value="suspended">已暂停</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item>
          <a-button type="primary" @click="fetchAdvertiserList">
            <search-outlined /> 搜索
          </a-button>
          <a-button style="margin-left: 8px" @click="resetSearch">
            重置
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
    
    <!-- 数据表格 -->
    <a-card class="table-card" :bordered="false">
      <a-table
        :dataSource="advertiserList"
        :columns="columns"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        rowKey="id"
      >
        <!-- 状态列自定义渲染 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          
          <!-- 账户余额自定义渲染 -->
          <template v-if="column.key === 'balance'">
            <span class="balance">{{ record.balance.toFixed(2) }}</span>
          </template>
          
          <!-- 操作列 -->
          <template v-if="column.key === 'action'">
            <a-space>
              <router-link :to="`/advertisers/${record.id}`">
                <a-button type="link" size="small">详情</a-button>
              </router-link>
              
              <a-dropdown>
                <template #overlay>
                  <a-menu>
                    <a-menu-item key="edit" @click="showEditModal(record)">
                      <edit-outlined /> 编辑
                    </a-menu-item>
                    
                    <a-menu-item 
                      v-if="record.status === 'pending'"
                      key="approve" 
                      @click="showStatusChangeModal(record, 'approved')"
                    >
                      <check-outlined /> 审核通过
                    </a-menu-item>
                    
                    <a-menu-item 
                      v-if="record.status === 'pending'"
                      key="reject" 
                      @click="showStatusChangeModal(record, 'rejected')"
                    >
                      <close-outlined /> 审核驳回
                    </a-menu-item>
                    
                    <a-menu-item 
                      v-if="record.status === 'approved'"
                      key="suspend" 
                      @click="showStatusChangeModal(record, 'suspended')"
                    >
                      <pause-outlined /> 暂停账户
                    </a-menu-item>
                    
                    <a-menu-item 
                      v-if="record.status === 'suspended' || record.status === 'rejected'"
                      key="activate" 
                      @click="showStatusChangeModal(record, 'approved')"
                    >
                      <play-outlined /> 激活账户
                    </a-menu-item>
                    
                    <a-menu-divider />
                    
                    <a-menu-item key="deposit" @click="showDepositModal(record)">
                      <wallet-outlined /> 充值
                    </a-menu-item>
                  </a-menu>
                </template>
                <a-button type="link" size="small">
                  更多 <down-outlined />
                </a-button>
              </a-dropdown>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
    
    <!-- 创建/编辑广告主模态框 -->
    <a-modal
      :title="isEdit ? '编辑广告主' : '创建广告主'"
      :visible="modalVisible"
      @cancel="modalVisible = false"
      @ok="handleModalSubmit"
      :confirmLoading="modalLoading"
      width="700px"
    >
      <a-form
        :model="advertiserForm"
        :rules="formRules"
        ref="formRef"
        :labelCol="{ span: 6 }"
        :wrapperCol="{ span: 16 }"
      >
        <a-form-item label="广告主名称" name="name">
          <a-input v-model:value="advertiserForm.name" />
        </a-form-item>
        
        <a-form-item label="公司名称" name="company_name">
          <a-input v-model:value="advertiserForm.company_name" />
        </a-form-item>
        
        <a-form-item label="统一社会信用代码" name="credit_code">
          <a-input v-model:value="advertiserForm.credit_code" />
        </a-form-item>
        
        <a-form-item label="联系人" name="contact_person">
          <a-input v-model:value="advertiserForm.contact_person" />
        </a-form-item>
        
        <a-form-item label="联系电话" name="contact_phone">
          <a-input v-model:value="advertiserForm.contact_phone" />
        </a-form-item>
        
        <a-form-item label="联系邮箱" name="contact_email">
          <a-input v-model:value="advertiserForm.contact_email" />
        </a-form-item>
        
        <a-form-item label="地址" name="address">
          <a-input v-model:value="advertiserForm.address" />
        </a-form-item>
        
        <a-form-item label="行业" name="industry">
          <a-select v-model:value="advertiserForm.industry">
            <a-select-option value="电商">电商</a-select-option>
            <a-select-option value="游戏">游戏</a-select-option>
            <a-select-option value="金融">金融</a-select-option>
            <a-select-option value="教育">教育</a-select-option>
            <a-select-option value="旅游">旅游</a-select-option>
            <a-select-option value="生活服务">生活服务</a-select-option>
            <a-select-option value="其他">其他</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="业务类型" name="business_type">
          <a-select v-model:value="advertiserForm.business_type">
            <a-select-option value="B2B">B2B</a-select-option>
            <a-select-option value="B2C">B2C</a-select-option>
            <a-select-option value="C2C">C2C</a-select-option>
            <a-select-option value="O2O">O2O</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 状态变更模态框 -->
    <a-modal
      :title="getStatusChangeTitle()"
      :visible="statusModalVisible"
      @cancel="statusModalVisible = false"
      @ok="handleStatusChange"
      :confirmLoading="statusModalLoading"
    >
      <a-form
        :model="statusForm"
        ref="statusFormRef"
        :labelCol="{ span: 6 }"
        :wrapperCol="{ span: 16 }"
      >
        <p>确定要将 <strong>{{ selectedAdvertiser?.name }}</strong> 的状态修改为 <strong>{{ getStatusText(targetStatus) }}</strong> 吗？</p>
        
        <a-form-item 
          v-if="targetStatus === 'rejected'"
          label="驳回原因" 
          name="reason"
          :rules="[{ required: true, message: '请输入驳回原因' }]"
        >
          <a-textarea v-model:value="statusForm.reason" :rows="4" />
        </a-form-item>
        
        <a-form-item 
          v-if="targetStatus === 'suspended'"
          label="暂停原因" 
          name="reason"
          :rules="[{ required: true, message: '请输入暂停原因' }]"
        >
          <a-textarea v-model:value="statusForm.reason" :rows="4" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 充值模态框 -->
    <a-modal
      title="账户充值"
      :visible="depositModalVisible"
      @cancel="depositModalVisible = false"
      @ok="handleDeposit"
      :confirmLoading="depositModalLoading"
    >
      <a-form
        :model="depositForm"
        ref="depositFormRef"
        :labelCol="{ span: 6 }"
        :wrapperCol="{ span: 16 }"
        :rules="depositRules"
      >
        <p>为广告主 <strong>{{ selectedAdvertiser?.name }}</strong> 充值</p>
        <p>当前余额: <strong>{{ selectedAdvertiser?.balance.toFixed(2) }} 元</strong></p>
        
        <a-form-item label="充值金额" name="amount">
          <a-input-number
            v-model:value="depositForm.amount"
            :min="0.01"
            :precision="2"
            style="width: 100%"
            placeholder="请输入充值金额"
          />
        </a-form-item>
        
        <a-form-item label="交易单号" name="transaction_id">
          <a-input v-model:value="depositForm.transaction_id" placeholder="请输入交易单号" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import type { TablePaginationConfig } from 'ant-design-vue'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined,
  PauseOutlined,
  PlayOutlined,
  DownOutlined,
  WalletOutlined
} from '@ant-design/icons-vue'
import { api } from '@/api'
import { useUserStore } from '@/store/user'

export default defineComponent({
  name: 'AdvertiserList',
  components: {
    PlusOutlined,
    SearchOutlined,
    EditOutlined,
    CheckOutlined,
    CloseOutlined,
    PauseOutlined,
    PlayOutlined,
    DownOutlined,
    WalletOutlined
  },
  setup() {
    const userStore = useUserStore()
    
    // 表单引用
    const formRef = ref()
    const statusFormRef = ref()
    const depositFormRef = ref()
    
    // 列表数据
    const loading = ref(false)
    const advertiserList = ref<any[]>([])
    
    // 分页配置
    const pagination = reactive<TablePaginationConfig>({
      current: 1,
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showTotal: (total) => `共 ${total} 条`
    })
    
    // 搜索表单
    const searchForm = reactive({
      name: '',
      status: undefined
    })
    
    // 表格列定义
    const columns = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 80
      },
      {
        title: '广告主名称',
        dataIndex: 'name',
        key: 'name'
      },
      {
        title: '公司名称',
        dataIndex: 'company_name',
        key: 'company_name'
      },
      {
        title: '联系人',
        dataIndex: 'contact_person',
        key: 'contact_person'
      },
      {
        title: '联系电话',
        dataIndex: 'contact_phone',
        key: 'contact_phone'
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status'
      },
      {
        title: '账户余额',
        dataIndex: 'balance',
        key: 'balance'
      },
      {
        title: '操作',
        key: 'action',
        width: 200
      }
    ]
    
    // 广告主表单
    const modalVisible = ref(false)
    const modalLoading = ref(false)
    const isEdit = ref(false)
    
    const advertiserForm = reactive({
      id: undefined,
      name: '',
      company_name: '',
      credit_code: '',
      contact_person: '',
      contact_phone: '',
      contact_email: '',
      address: '',
      industry: undefined,
      business_type: undefined
    })
    
    // 表单验证规则
    const formRules = {
      name: [
        { required: true, message: '请输入广告主名称', trigger: 'blur' },
        { min: 2, max: 100, message: '长度必须在2-100个字符之间', trigger: 'blur' }
      ],
      company_name: [
        { required: true, message: '请输入公司名称', trigger: 'blur' },
        { min: 2, max: 200, message: '长度必须在2-200个字符之间', trigger: 'blur' }
      ],
      contact_person: [
        { required: true, message: '请输入联系人', trigger: 'blur' }
      ],
      contact_phone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
      ],
      contact_email: [
        { required: true, message: '请输入联系邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }
    
    // 状态变更相关
    const statusModalVisible = ref(false)
    const statusModalLoading = ref(false)
    const selectedAdvertiser = ref<any>(null)
    const targetStatus = ref('')
    
    const statusForm = reactive({
      reason: ''
    })
    
    // 充值相关
    const depositModalVisible = ref(false)
    const depositModalLoading = ref(false)
    
    const depositForm = reactive({
      amount: 0,
      transaction_id: ''
    })
    
    const depositRules = {
      amount: [
        { required: true, message: '请输入充值金额', trigger: 'blur' },
        { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
      ],
      transaction_id: [
        { required: true, message: '请输入交易单号', trigger: 'blur' }
      ]
    }
    
    // 获取广告主列表
    const fetchAdvertiserList = async () => {
      loading.value = true
      
      try {
        const params = {
          page: pagination.current,
          per_page: pagination.pageSize,
          name: searchForm.name,
          status: searchForm.status
        }
        
        const response = await api.advertisers.list(params)
        advertiserList.value = response.data.items
        pagination.total = response.data.total
      } catch (error) {
        console.error('Failed to fetch advertisers:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 表格变化处理
    const handleTableChange = (pag: TablePaginationConfig) => {
      pagination.current = pag.current || 1
      pagination.pageSize = pag.pageSize || 10
      fetchAdvertiserList()
    }
    
    // 重置搜索条件
    const resetSearch = () => {
      searchForm.name = ''
      searchForm.status = undefined
      pagination.current = 1
      fetchAdvertiserList()
    }
    
    // 显示创建模态框
    const showCreateModal = () => {
      isEdit.value = false
      
      // 重置表单
      Object.keys(advertiserForm).forEach(key => {
        advertiserForm[key] = key === 'id' ? undefined : ''
      })
      
      modalVisible.value = true
    }
    
    // 显示编辑模态框
    const showEditModal = (record: any) => {
      isEdit.value = true
      
      // 填充表单数据
      Object.keys(advertiserForm).forEach(key => {
        advertiserForm[key] = record[key]
      })
      
      modalVisible.value = true
    }
    
    // 提交模态框
    const handleModalSubmit = () => {
      formRef.value.validate().then(async () => {
        modalLoading.value = true
        
        try {
          if (isEdit.value) {
            // 编辑模式
            await api.advertisers.update(advertiserForm.id, advertiserForm)
            message.success('广告主更新成功')
          } else {
            // 创建模式
            await api.advertisers.create(advertiserForm)
            message.success('广告主创建成功')
          }
          
          modalVisible.value = false
          fetchAdvertiserList()
        } catch (error) {
          console.error('Failed to save advertiser:', error)
        } finally {
          modalLoading.value = false
        }
      })
    }
    
    // 显示状态变更模态框
    const showStatusChangeModal = (record: any, status: string) => {
      selectedAdvertiser.value = record
      targetStatus.value = status
      statusForm.reason = ''
      statusModalVisible.value = true
    }
    
    // 获取状态变更模态框标题
    const getStatusChangeTitle = () => {
      switch (targetStatus.value) {
        case 'approved':
          return '审核通过'
        case 'rejected':
          return '审核驳回'
        case 'suspended':
          return '暂停账户'
        default:
          return '状态变更'
      }
    }
    
    // 处理状态变更
    const handleStatusChange = () => {
      const validateForm = targetStatus.value === 'rejected' || targetStatus.value === 'suspended'
      
      const doStatusChange = async () => {
        statusModalLoading.value = true
        
        try {
          const params = {
            status: targetStatus.value,
            reason: statusForm.reason
          }
          
          await api.advertisers.changeStatus(selectedAdvertiser.value.id, params)
          message.success('状态更新成功')
          statusModalVisible.value = false
          fetchAdvertiserList()
        } catch (error) {
          console.error('Failed to update status:', error)
        } finally {
          statusModalLoading.value = false
        }
      }
      
      if (validateForm) {
        statusFormRef.value.validate().then(doStatusChange)
      } else {
        doStatusChange()
      }
    }
    
    // 显示充值模态框
    const showDepositModal = (record: any) => {
      selectedAdvertiser.value = record
      depositForm.amount = 0
      depositForm.transaction_id = `TX${Date.now()}`  // 生成示例交易ID
      depositModalVisible.value = true
    }
    
    // 处理充值
    const handleDeposit = () => {
      depositFormRef.value.validate().then(async () => {
        depositModalLoading.value = true
        
        try {
          await api.advertisers.deposit(
            selectedAdvertiser.value.id, 
            {
              amount: depositForm.amount,
              transaction_id: depositForm.transaction_id
            }
          )
          
          message.success(`充值 ${depositForm.amount} 元成功`)
          depositModalVisible.value = false
          fetchAdvertiserList()
        } catch (error) {
          console.error('Failed to deposit:', error)
        } finally {
          depositModalLoading.value = false
        }
      })
    }
    
    // 获取状态文本
    const getStatusText = (status: string) => {
      const statusMap: Record<string, string> = {
        pending: '待审核',
        approved: '已通过',
        rejected: '已驳回',
        suspended: '已暂停'
      }
      
      return statusMap[status] || status
    }
    
    // 获取状态颜色
    const getStatusColor = (status: string) => {
      const colorMap: Record<string, string> = {
        pending: 'orange',
        approved: 'green',
        rejected: 'red',
        suspended: 'gray'
      }
      
      return colorMap[status] || 'blue'
    }
    
    // 权限控制
    const canCreate = computed(() => userStore.hasPermission('advertisers.create'))
    const canReview = computed(() => userStore.hasPermission('advertisers.review'))
    const canFinance = computed(() => userStore.hasPermission('advertisers.finance'))
    
    onMounted(() => {
      fetchAdvertiserList()
    })
    
    return {
      loading,
      advertiserList,
      columns,
      pagination,
      searchForm,
      fetchAdvertiserList,
      handleTableChange,
      resetSearch,
      
      modalVisible,
      modalLoading,
      isEdit,
      advertiserForm,
      formRules,
      formRef,
      showCreateModal,
      showEditModal,
      handleModalSubmit,
      
      statusModalVisible,
      statusModalLoading,
      statusForm,
      statusFormRef,
      selectedAdvertiser,
      targetStatus,
      showStatusChangeModal,
      getStatusChangeTitle,
      handleStatusChange,
      
      depositModalVisible,
      depositModalLoading,
      depositForm,
      depositFormRef,
      depositRules,
      showDepositModal,
      handleDeposit,
      
      getStatusText,
      getStatusColor,
      
      canCreate,
      canReview,
      canFinance
    }
  }
})
</script>

<style lang="less" scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  h2 {
    margin: 0;
  }
  
  .page-header-actions {
    display: flex;
    align-items: center;
  }
}

.search-card {
  margin-bottom: 24px;
}

.table-card {
  margin-bottom: 24px;
}

.balance {
  font-weight: bold;
  color: #1890ff;
}
</style> 