<template>
  <div class="dashboard">
    <!-- 数据概览卡片 -->
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card>
          <template #title>
            <span>
              <fund-outlined />
              今日消耗
            </span>
          </template>
          <div class="card-content">
            <div class="amount">¥{{ formatNumber(todaySpend) }}</div>
            <div class="trend" :class="{ 'up': todaySpendTrend > 0, 'down': todaySpendTrend < 0 }">
              {{ Math.abs(todaySpendTrend) }}% {{ todaySpendTrend > 0 ? '↑' : '↓' }}
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <template #title>
            <span>
              <eye-outlined />
              今日展示
            </span>
          </template>
          <div class="card-content">
            <div class="amount">{{ formatNumber(todayImpressions) }}</div>
            <div class="trend" :class="{ 'up': todayImpressionsTrend > 0, 'down': todayImpressionsTrend < 0 }">
              {{ Math.abs(todayImpressionsTrend) }}% {{ todayImpressionsTrend > 0 ? '↑' : '↓' }}
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <template #title>
            <span>
              <click-outlined />
              今日点击
            </span>
          </template>
          <div class="card-content">
            <div class="amount">{{ formatNumber(todayClicks) }}</div>
            <div class="trend" :class="{ 'up': todayClicksTrend > 0, 'down': todayClicksTrend < 0 }">
              {{ Math.abs(todayClicksTrend) }}% {{ todayClicksTrend > 0 ? '↑' : '↓' }}
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <template #title>
            <span>
              <rise-outlined />
              今日转化
            </span>
          </template>
          <div class="card-content">
            <div class="amount">{{ formatNumber(todayConversions) }}</div>
            <div class="trend" :class="{ 'up': todayConversionsTrend > 0, 'down': todayConversionsTrend < 0 }">
              {{ Math.abs(todayConversionsTrend) }}% {{ todayConversionsTrend > 0 ? '↑' : '↓' }}
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 图表区域 -->
    <a-row :gutter="16" class="charts-row">
      <a-col :span="16">
        <a-card title="数据趋势">
          <div ref="trendChartRef" class="chart"></div>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card title="投放分布">
          <div ref="pieChartRef" class="chart"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 最近活动 -->
    <a-card title="最近活动" class="recent-activities">
      <a-list :data-source="recentActivities" :pagination="false">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #avatar>
                <a-avatar :style="{ backgroundColor: item.color }">
                  {{ item.icon }}
                </a-avatar>
              </template>
              <template #title>
                {{ item.title }}
              </template>
              <template #description>
                {{ item.time }}
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { 
  FundOutlined, 
  EyeOutlined, 
  ClickOutlined, 
  RiseOutlined 
} from '@ant-design/icons-vue'
import * as echarts from 'echarts'

export default defineComponent({
  name: 'Dashboard',
  components: {
    FundOutlined,
    EyeOutlined,
    ClickOutlined,
    RiseOutlined
  },
  setup() {
    // 数据概览
    const todaySpend = ref(12345.67)
    const todaySpendTrend = ref(5.2)
    const todayImpressions = ref(123456)
    const todayImpressionsTrend = ref(-2.1)
    const todayClicks = ref(1234)
    const todayClicksTrend = ref(3.5)
    const todayConversions = ref(123)
    const todayConversionsTrend = ref(7.8)

    // 图表引用
    const trendChartRef = ref<HTMLElement>()
    const pieChartRef = ref<HTMLElement>()

    // 最近活动
    const recentActivities = ref([
      {
        icon: '新',
        color: '#1890ff',
        title: '新建广告活动 "夏季促销"',
        time: '10分钟前'
      },
      {
        icon: '审',
        color: '#52c41a',
        title: '广告主 "ABC公司" 审核通过',
        time: '30分钟前'
      },
      {
        icon: '更',
        color: '#faad14',
        title: '更新创意 "新品上市"',
        time: '1小时前'
      },
      {
        icon: '停',
        color: '#f5222d',
        title: '暂停广告活动 "节日特惠"',
        time: '2小时前'
      }
    ])

    // 格式化数字
    const formatNumber = (num: number) => {
      return new Intl.NumberFormat('zh-CN').format(num)
    }

    // 初始化趋势图表
    const initTrendChart = () => {
      if (!trendChartRef.value) return

      const chart = echarts.init(trendChartRef.value)
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['展示量', '点击量', '转化量', '消耗']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '展示量',
            type: 'line',
            data: [120, 132, 101, 134, 90, 230, 210]
          },
          {
            name: '点击量',
            type: 'line',
            data: [220, 182, 191, 234, 290, 330, 310]
          },
          {
            name: '转化量',
            type: 'line',
            data: [150, 232, 201, 154, 190, 330, 410]
          },
          {
            name: '消耗',
            type: 'line',
            data: [320, 332, 301, 334, 390, 330, 320]
          }
        ]
      }
      chart.setOption(option)
    }

    // 初始化饼图
    const initPieChart = () => {
      if (!pieChartRef.value) return

      const chart = echarts.init(pieChartRef.value)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            name: '投放分布',
            type: 'pie',
            radius: '50%',
            data: [
              { value: 1048, name: '搜索广告' },
              { value: 735, name: '展示广告' },
              { value: 580, name: '视频广告' },
              { value: 484, name: '原生广告' }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      chart.setOption(option)
    }

    onMounted(() => {
      initTrendChart()
      initPieChart()
    })

    return {
      todaySpend,
      todaySpendTrend,
      todayImpressions,
      todayImpressionsTrend,
      todayClicks,
      todayClicksTrend,
      todayConversions,
      todayConversionsTrend,
      recentActivities,
      trendChartRef,
      pieChartRef,
      formatNumber
    }
  }
})
</script>

<style lang="less" scoped>
.dashboard {
  .card-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .amount {
      font-size: 24px;
      font-weight: bold;
    }
    
    .trend {
      font-size: 14px;
      
      &.up {
        color: @success-color;
      }
      
      &.down {
        color: @error-color;
      }
    }
  }
  
  .charts-row {
    margin-top: 16px;
    
    .chart {
      height: 300px;
    }
  }
  
  .recent-activities {
    margin-top: 16px;
  }
}
</style> 