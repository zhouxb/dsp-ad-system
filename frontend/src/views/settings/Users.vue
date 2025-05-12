<template>
  <div class="users-manage">
    <!-- 搜索和操作栏 -->
    <div class="table-operations">
      <a-space>
        <a-input-search
          v-model:value="searchForm.keyword"
          placeholder="搜索用户名/邮箱"
          style="width: 200px"
          @search="handleSearch"
        />
        <a-select
          v-model:value="searchForm.status"
          style="width: 120px"
          placeholder="状态"
          @change="handleSearch"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="active">正常</a-select-option>
          <a-select-option value="inactive">禁用</a-select-option>
        </a-select>
        <a-button type="primary" @click="handleAdd">
          <template #icon><plus-outlined /></template>
          新增用户
        </a-button>
      </a-space>
    </div>

    <!-- 用户列表 -->
    <a-table
      :columns="columns"
      :data-source="tableData"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="record.status === 'active' ? 'success' : 'error'">
            {{ record.status === 'active' ? '正常' : '禁用' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a @click="handleResetPassword(record)">重置密码</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除该用户吗？"
              @confirm="handleDelete(record)"
            >
              <a class="danger-link">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 用户表单对话框 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="用户名" name="username">
          <a-input v-model:value="form.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="邮箱" name="email">
          <a-input v-model:value="form.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="手机号" name="phone">
          <a-input v-model:value="form.phone" placeholder="请输入手机号" />
        </a-form-item>
        <a-form-item label="角色" name="roles">
          <a-select
            v-model:value="form.roles"
            mode="multiple"
            placeholder="请选择角色"
          >
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="operator">运营</a-select-option>
            <a-select-option value="advertiser">广告主</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-radio-group v-model:value="form.status">
            <a-radio value="active">正常</a-radio>
            <a-radio value="inactive">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item
          v-if="!form.id"
          label="密码"
          name="password"
        >
          <a-input-password
            v-model:value="form.password"
            placeholder="请输入密码"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 重置密码对话框 -->
    <a-modal
      v-model:visible="resetPasswordVisible"
      title="重置密码"
      @ok="handleResetPasswordConfirm"
      @cancel="handleResetPasswordCancel"
    >
      <a-form
        ref="resetPasswordFormRef"
        :model="resetPasswordForm"
        :rules="resetPasswordRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="新密码" name="password">
          <a-input-password
            v-model:value="resetPasswordForm.password"
            placeholder="请输入新密码"
          />
        </a-form-item>
        <a-form-item label="确认密码" name="confirmPassword">
          <a-input-password
            v-model:value="resetPasswordForm.confirmPassword"
            placeholder="请再次输入新密码"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import type { FormInstance } from 'ant-design-vue'

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: ''
})

// 表格列定义
const columns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username'
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email'
  },
  {
    title: '手机号',
    dataIndex: 'phone',
    key: 'phone'
  },
  {
    title: '角色',
    dataIndex: 'roles',
    key: 'roles'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status'
  },
  {
    title: '创建时间',
    dataIndex: 'createdAt',
    key: 'createdAt'
  },
  {
    title: '操作',
    key: 'action'
  }
]

// 表格数据
const tableData = ref([
  {
    id: '1',
    username: 'admin',
    email: 'admin@example.com',
    phone: '13800138000',
    roles: ['管理员'],
    status: 'active',
    createdAt: '2024-04-17 10:00:00'
  },
  {
    id: '2',
    username: 'operator',
    email: 'operator@example.com',
    phone: '13800138001',
    roles: ['运营'],
    status: 'active',
    createdAt: '2024-04-17 11:00:00'
  }
])

const loading = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 100
})

// 表单对话框
const modalVisible = ref(false)
const modalTitle = computed(() => (form.id ? '编辑用户' : '新增用户'))
const formRef = ref<FormInstance>()
const form = reactive({
  id: '',
  username: '',
  email: '',
  phone: '',
  roles: [],
  status: 'active',
  password: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  roles: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ]
}

// 重置密码对话框
const resetPasswordVisible = ref(false)
const resetPasswordFormRef = ref<FormInstance>()
const resetPasswordForm = reactive({
  userId: '',
  password: '',
  confirmPassword: ''
})

// 重置密码验证规则
const resetPasswordRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: async (_rule: any, value: string) => {
        if (value !== resetPasswordForm.password) {
          throw new Error('两次输入的密码不一致')
        }
      },
      trigger: 'blur'
    }
  ]
}

// 处理搜索
const handleSearch = () => {
  console.log('搜索条件：', searchForm)
  // TODO: 实现搜索逻辑
}

// 处理新增
const handleAdd = () => {
  form.id = ''
  form.username = ''
  form.email = ''
  form.phone = ''
  form.roles = []
  form.status = 'active'
  form.password = ''
  modalVisible.value = true
}

// 处理编辑
const handleEdit = (record: any) => {
  form.id = record.id
  form.username = record.username
  form.email = record.email
  form.phone = record.phone
  form.roles = record.roles
  form.status = record.status
  modalVisible.value = true
}

// 处理删除
const handleDelete = (record: any) => {
  console.log('删除用户：', record)
  message.success('删除成功')
}

// 处理重置密码
const handleResetPassword = (record: any) => {
  resetPasswordForm.userId = record.id
  resetPasswordForm.password = ''
  resetPasswordForm.confirmPassword = ''
  resetPasswordVisible.value = true
}

// 处理表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  // TODO: 重新加载数据
}

// 处理表单提交
const handleModalOk = async () => {
  try {
    await formRef.value?.validate()
    console.log('表单数据：', form)
    message.success(form.id ? '编辑成功' : '新增成功')
    modalVisible.value = false
  } catch (error) {
    console.error('表单验证失败：', error)
  }
}

// 处理表单取消
const handleModalCancel = () => {
  modalVisible.value = false
}

// 处理重置密码确认
const handleResetPasswordConfirm = async () => {
  try {
    await resetPasswordFormRef.value?.validate()
    console.log('重置密码：', resetPasswordForm)
    message.success('密码重置成功')
    resetPasswordVisible.value = false
  } catch (error) {
    console.error('表单验证失败：', error)
  }
}

// 处理重置密码取消
const handleResetPasswordCancel = () => {
  resetPasswordVisible.value = false
}
</script>

<style lang="less" scoped>
.users-manage {
  .table-operations {
    margin-bottom: 16px;
  }

  .danger-link {
    color: #ff4d4f;
  }
}
</style>
