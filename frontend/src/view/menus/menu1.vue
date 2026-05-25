<template>
  <div class="graph-upload-container" style="margin: 20px auto; padding: 20px;">
    <h2 style="text-align: center; margin-bottom: 30px; color: #333;">知识图谱展示</h2>

    <div class="knowledge-container">
    <!-- 多行文本输入框 -->
    <textarea
      v-model="content"
      placeholder="请输入要构建知识图谱的文本内容"
      rows="6"
      class="knowledge-textarea"
    ></textarea>

    <!-- 发送按钮 -->
    <button 
      @click="sendContent" 
      :disabled="loading"
      class="send-btn"
    >
      {{ loading ? '发送中...' : '发送' }}
    </button>

    <!-- 提示信息 -->
    <div v-if="message" class="message" :class="{ success: isSuccess, error: !isSuccess }">
      {{ message }}
    </div>
  </div>

    <!-- 知识图谱展示框 -->
    <div class="graph-container" style="height: 600px; width: 80vw; border: 1px solid #eee; border-radius: 8px;">
      <div id="knowledge-graph" style="width: 100%; height: 100%"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElUpload, ElButton, ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'
import neo4j from 'neo4j-driver'



// 绑定文本框内容
const content = ref('')
// 加载状态
const loading = ref(false)
// 提示信息
const message = ref('')
const isSuccess = ref(false)

// 发送请求
const sendContent = async () => {
  // 非空校验
  if (!content.value.trim()) {
    message.value = '请输入内容'
    isSuccess.value = false
    return
  }

  try {
    loading.value = true
    message.value = ''

    // 发送 POST 请求
    const res = await fetch('http://localhost:8718/build-knowledge-graph', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // 严格按照你要求的格式传参
      body: JSON.stringify({
        content: content.value
      })
    })

    if (res.ok) {
      message.value = '发送成功！'
      isSuccess.value = true
      // 可选：发送成功后清空输入框
      // content.value = ''
    } else {
      message.value = `请求失败，状态码：${res.status}`
      isSuccess.value = false
    }
  } catch (err) {
    message.value = '请求异常：' + err.message
    isSuccess.value = false
    console.error('请求错误：', err)
  } finally {
    loading.value = false
  }
}

const fileList = ref([])
let graphChart = null
let neo4jDriver = null

// ==============================================
// 1. 初始化 Neo4j 连接（你的配置：localhost:7687）
// ==============================================
async function initNeo4j() {
  try {
    const URI = 'bolt://localhost:7687'
    const USER = 'neo4j'
    const PASSWORD = '12345678'

    neo4jDriver = neo4j.driver(URI, neo4j.auth.basic(USER, PASSWORD))
    await neo4jDriver.verifyConnectivity()
    ElMessage.success('✅ Neo4j 连接成功！')
  } catch (err) {
    ElMessage.error('❌ Neo4j 连接失败：' + err.message)
    console.error(err)
  }
}
async function loadGraphFromNeo4j() {
  if (!neo4jDriver) return

  const session = neo4jDriver.session()
  try {
    // 直接查询出 节点名 + 关系名
    const result = await session.run(`
      MATCH (n)-[r]->(m)
      RETURN
        n.name AS fromName,
        m.name AS toName,
        TYPE(r) AS relationType,
        r.name AS relationName
    `)

    const nodes = []
    const links = []
    const nodeMap = new Map()

    result.records.forEach(record => {
      const fromName = record.get('fromName') || '未知节点'
      const toName = record.get('toName') || '未知节点'
      const relationType = record.get('relationType')
      const relationName = record.get('relationName')

      // 优先用关系属性 name，没有则用关系类型
      const realRelationName = relationName || relationType || '关联'

      if (!nodeMap.has(fromName)) {
        nodeMap.set(fromName, { name: fromName, category: 0 })
      }
      if (!nodeMap.has(toName)) {
        nodeMap.set(toName, { name: toName, category: 0 })
      }

      links.push({
        source: fromName,
        target: toName,
        value: realRelationName  // 真实关系名称
      })
    })

    graphChart.setOption({
      series: [{ data: Array.from(nodeMap.values()), links }]
    })

    ElMessage.success('✅ 图谱加载成功')
  } catch (err) {
    ElMessage.error('❌ 加载失败：' + err.message)
  } finally {
    await session.close()
  }
}

// ==============================================
// 3. 文件上传到后端：127.0.0.1:4567/upload
// ==============================================
async function uploadToBackend() {
  if (!fileList.value.length) {
    ElMessage.warning('请先选择文件')
    return
  }

  const file = fileList.value[0].raw
  const formData = new FormData()
  formData.append('file', file)

  try {
    await axios.post('http://127.0.0.1:4567/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('✅ 文件上传成功！')

    // 上传完成 → 自动加载 Neo4j 图谱

  } catch (err) {
    ElMessage.error('❌ 上传失败：' + err.message)
  }
}

// ==============================================
// 4. 初始化 ECharts 图谱画布
// ==============================================
function initGraph() {
  const dom = document.getElementById('knowledge-graph')
  graphChart = echarts.init(dom)
  graphChart.setOption({
    tooltip: {},
    legend: [{ data: ['实体'], bottom: 10 }],
    series: [{
      type: 'graph',
      layout: 'force',
      symbolSize: 50,
      roam: true,
      label: { show: true },
      edgeLabel: { show: true, formatter: '{c}' },
      force: { repulsion: 300 },
      data: [],
      links: [],
      categories: [{ name: '实体' }]
    }]
  })
}

// 文件选择
function handleFileChange(uploadFile) {
  fileList.value = [uploadFile]
}

// 页面加载
onMounted(async () => {
  initGraph()
  await initNeo4j()
  loadGraphFromNeo4j()
  window.addEventListener('resize', () => graphChart?.resize())
})
</script>


<style scoped>
.knowledge-container {
  width: 600px;
  margin: 40px auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.knowledge-textarea {
  padding: 12px;
  font-size: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
  outline: none;
}

.knowledge-textarea:focus {
  border-color: #409eff;
}

.send-btn {
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.send-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.message {
  font-size: 13px;
  padding: 8px;
  border-radius: 4px;
}

.success {
  color: #67c23a;
  background-color: #f0f9ff;
}

.error {
  color: #f56c6c;
  background-color: #fef0f0;
}
</style>