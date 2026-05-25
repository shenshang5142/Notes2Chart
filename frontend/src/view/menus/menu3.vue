<template>
  <div class="learning-radar-container">
    <div class="page-header">
      <h2>学习成长雷达图</h2>
      <p class="subtitle">基于已上传文件的主题关键词分析</p>
    </div>

    <!-- 操作区域 -->
    <div class="action-section">
      <button
        class="analyze-btn"
        :disabled="analyzing"
        @click="fetchKeywordAnalysis"
      >
        <span v-if="!analyzing">开始分析主题关键词</span>
        <span v-else>分析中...</span>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="analyzing" class="loading-section">
      <div class="loading-spinner"></div>
      <p>正在分析已上传文件的主题关键词，请稍候...</p>
    </div>

    <!-- 分析结果 -->
    <div v-if="!analyzing && keywordData" class="result-section">
      <!-- 无数据提示 -->
      <div v-if="top6.length === 0 && otherKeywords.length === 0" class="empty-section">
        <p>未找到主题关键词，请先上传文件或发送聊天消息后再分析</p>
      </div>

      <!-- 雷达图 -->
      <div v-if="top6.length > 0" class="radar-section">
        <h3 class="section-title">主题关键词雷达图（Top 6）</h3>
        <div ref="radarChart" class="radar-chart"></div>
      </div>

      <!-- 关键词频率表格（全部关键词） -->
      <div v-if="allKeywords.length > 0" class="table-section">
        <h3 class="section-title">主题关键词明细（共 {{ allKeywords.length }} 个）</h3>
        <table class="keyword-table">
          <thead>
            <tr>
              <th>#</th>
              <th>关键词</th>
              <th>出现文件数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in allKeywords" :key="idx" :class="{ 'top-row': idx < 6 }">
              <td class="rank-cell">
                <span v-if="idx === 0" class="rank-badge gold">1</span>
                <span v-else-if="idx === 1" class="rank-badge silver">2</span>
                <span v-else-if="idx === 2" class="rank-badge bronze">3</span>
                <span v-else>{{ idx + 1 }}</span>
              </td>
              <td>{{ item.name }}</td>
              <td>{{ item.value }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!analyzing && !keywordData" class="empty-section">
      <p>点击上方按钮，开始分析已上传文件中的主题关键词</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'LearningRadar',
  data() {
    return {
      analyzing: false,
      keywordData: null
    }
  },
  computed: {
    username() {
      return localStorage.getItem('username') || ''
    },
    top6() {
      if (!this.keywordData) return []
      return this.keywordData.top6 || []
    },
    otherKeywords() {
      if (!this.keywordData) return []
      return this.keywordData.others || []
    },
    allKeywords() {
      const top = this.top6
      const rest = this.otherKeywords
      return [...top, ...rest]
    }
  },
  methods: {
    async fetchKeywordAnalysis() {
      this.analyzing = true
      this.keywordData = null
      try {
        const res = await axios.post('http://localhost:4567/analyze-keywords', {
          username: this.username
        })
        this.keywordData = res.data
      } catch (err) {
        console.error('关键词分析失败：', err)
        alert('分析失败，请检查后端服务是否正常运行')
      } finally {
        this.analyzing = false
      }
      // analyzing=false 之后 v-if 条件才满足，DOM 才会渲染雷达图容器
      if (this.keywordData) {
        this.$nextTick(() => {
          this.renderRadarChart()
        })
      }
    },

    renderRadarChart() {
      const chartDom = this.$refs.radarChart
      if (!chartDom || !this.top6.length) return

      if (this.chartInstance) {
        this.chartInstance.dispose()
      }

      this.chartInstance = echarts.init(chartDom)

      const maxVal = Math.max(...this.top6.map(i => i.value))
      const ceilMax = Math.ceil(maxVal * 1.3)

      const indicators = this.top6.map(item => ({
        name: item.name.length > 4 ? item.name.replace(/(.{4})/g, '$1\n') : item.name,
        max: ceilMax
      }))

      const values = this.top6.map(item => item.value)

      const option = {
        color: ['#3b82f6'],
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255,255,255,0.95)',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          textStyle: { color: '#1e293b', fontSize: 13 },
          formatter: (params) => {
            const idx = params.dataIndex ?? params.dimensionIndex
            if (idx !== undefined && this.top6[idx]) {
              const item = this.top6[idx]
              return `<b>${item.name}</b><br/>出现文件数：${item.value}`
            }
            return `${params.name}: ${params.value}`
          }
        },
        legend: {
          data: ['关键词频率'],
          bottom: 0,
          textStyle: { color: '#64748b', fontSize: 12 },
          itemWidth: 12,
          itemHeight: 12,
          itemGap: 20
        },
        radar: {
          center: ['50%', '50%'],
          radius: '62%',
          startAngle: 90,
          splitNumber: 4,
          shape: 'polygon',
          axisName: {
            color: '#334155',
            fontSize: 12,
            fontWeight: 500,
            overflow: 'truncate',
            width: 60
          },
          splitArea: {
            areaStyle: {
              color: ['rgba(59,130,246,0.03)', 'rgba(59,130,246,0.06)', 'rgba(59,130,246,0.03)', 'rgba(59,130,246,0.06)']
            }
          },
          splitLine: {
            lineStyle: { color: 'rgba(59,130,246,0.2)', width: 1 }
          },
          axisLine: {
            lineStyle: { color: 'rgba(59,130,246,0.35)', width: 1.5 }
          },
          indicator: indicators
        },
        series: [
          {
            type: 'radar',
            name: '关键词频率',
            data: [{ value: values, name: '关键词频率', symbol: 'circle' }],
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: {
              color: '#3b82f6',
              width: 2.5,
              shadowBlur: 8,
              shadowColor: 'rgba(59,130,246,0.5)'
            },
            itemStyle: {
              color: '#3b82f6',
              borderColor: '#fff',
              borderWidth: 2,
              shadowBlur: 6,
              shadowColor: 'rgba(59,130,246,0.4)'
            },
            areaStyle: {
              color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.7, [
                { offset: 0, color: 'rgba(59,130,246,0.35)' },
                { offset: 1, color: 'rgba(59,130,246,0.05)' }
              ])
            },
            emphasis: {
              lineStyle: { width: 3.5 },
              areaStyle: {
                color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.7, [
                  { offset: 0, color: 'rgba(59,130,246,0.45)' },
                  { offset: 1, color: 'rgba(59,130,246,0.1)' }
                ])
              },
              itemStyle: {
                shadowBlur: 12,
                shadowColor: 'rgba(59,130,246,0.6)'
              }
            }
          }
        ]
      }

      this.chartInstance.setOption(option)

      const handleResize = () => {
        this.chartInstance && this.chartInstance.resize()
      }
      window.addEventListener('resize', handleResize)
      this._resizeHandler = handleResize
    }
  },

  beforeUnmount() {
    if (this._resizeHandler) {
      window.removeEventListener('resize', this._resizeHandler)
    }
    if (this.chartInstance) {
      this.chartInstance.dispose()
    }
  }
}
</script>

<style scoped>
.learning-radar-container {
  width: 80vw;
  margin: 0 auto;
  padding: 10px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.page-header {
  text-align: center;
  margin-bottom: 24px;
}
.page-header h2 {
  margin: 0 0 6px 0;
  color: #1e293b;
  font-weight: 600;
}
.subtitle {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

/* 操作区域 */
.action-section {
  text-align: center;
  margin-bottom: 28px;
}
.analyze-btn {
  padding: 12px 36px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  background: #3b82f6;
  color: white;
  transition: all 0.2s ease;
}
.analyze-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}
.analyze-btn:hover:not(:disabled) {
  background: #2563eb;
}

/* 加载 */
.loading-section {
  text-align: center;
  padding: 40px;
  color: #64748b;
}
.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px auto;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 雷达图 */
.radar-section {
  margin-bottom: 32px;
}
.section-title {
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  padding-left: 12px;
  border-left: 3px solid #3b82f6;
}
.radar-chart {
  width: 100%;
  height: 450px;
  background: #fafbfc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

/* 关键词表格 */
.table-section {
  margin-bottom: 20px;
}
.keyword-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.keyword-table thead {
  border-top: 2px solid #1e293b;
  border-bottom: 1px solid #1e293b;
}
.keyword-table th {
  padding: 10px 16px;
  text-align: left;
  color: #1e293b;
  font-weight: 600;
  background: #f8fafc;
}
.keyword-table td {
  padding: 10px 16px;
  color: #334155;
  border-bottom: 1px solid #e2e8f0;
}
.keyword-table tbody tr:hover {
  background: #f1f5f9;
}
.keyword-table tbody {
  border-bottom: 2px solid #1e293b;
}
.top-row td {
  font-weight: 600;
  color: #1e293b;
  background: #fafbfc;
}
.rank-cell {
  text-align: center;
  width: 48px;
}
.rank-badge {
  display: inline-block;
  width: 22px;
  height: 22px;
  line-height: 22px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  text-align: center;
}
.rank-badge.gold {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
}
.rank-badge.silver {
  background: linear-gradient(135deg, #94a3b8, #64748b);
  box-shadow: 0 2px 4px rgba(100, 116, 139, 0.3);
}
.rank-badge.bronze {
  background: linear-gradient(135deg, #d97706, #b45309);
  box-shadow: 0 2px 4px rgba(217, 119, 6, 0.3);
}

/* 空状态 */
.empty-section {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}
</style>
