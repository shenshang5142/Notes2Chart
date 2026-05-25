<template>
  <div class="chat-container">
    <!-- 顶部操作区：上传 + 消息发送 -->
    <div class="top-panel">
      <!-- 文件上传区域 -->
      <div class="upload-section">
        <div
          class="upload-box"
          @click="triggerFileInput"
          @drop="handleDrop"
          @dragover.prevent
        >
          <input
            ref="fileInput"
            type="file"
            class="file-input"
            @change="handleFileChange"
          />
          <div v-if="!selectedFile" class="upload-placeholder">
            <svg class="upload-icon" viewBox="0 0 24 24">
              <path d="M19 13v6H5v-6H3v8h18v-8h-2zM12 2l8 8h-3v6h-2v-6H7v6H5V10H2l8-8z"/>
            </svg>
            <p>点击选择文件 或 拖拽文件到此处</p>
            <span class="tip">支持任意格式文件</span>
          </div>
          <div v-else class="file-info">
            <svg class="file-icon" viewBox="0 0 24 24">
              <path d="M13 9h5.5L13 3.5V9M6 2h8l6 6v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4c0-1.11.89-2 2-2z"/>
            </svg>
            <div class="file-details">
              <p class="file-name">{{ selectedFile.name }}</p>
              <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button class="remove-file" @click.stop="clearFile">×</button>
          </div>
        </div>

        <button
          class="upload-btn"
          :disabled="!selectedFile || uploading"
          @click="uploadFile"
        >
          <span v-if="!uploading">上传文件</span>
          <span v-else>上传中...</span>
        </button>
      </div>

      <!-- 消息发送区域 -->
      <div class="message-section">
        <textarea
          v-model="message"
          class="message-input"
          placeholder="请输入要发送的消息..."
          rows="2"
          @keyup.enter="sendMessage"
        ></textarea>
        <div class="send-row">
          <select v-model="chartType" class="chart-select">
            <option value="">-- 选择图表类型 --</option>
            <option value="line">折线图</option>
            <option value="bar">柱状图</option>
            <option value="pie">饼图</option>
            <option value="scatter">散点图</option>
            <option value="radar">数据雷达图</option>
            <option value="bar3d">3D柱状图</option>
            <option value="heatmap">矩阵热力图</option>
            <option value="comparison-table">二维对比表格（三线表）</option>
            <option value="tree">树图（思维导图）</option>
            <option value="graph">关系图（知识图谱）</option>
            <option value="flowchart">流程图（Mermaid）</option>
          </select>
          <button
            class="send-btn"
            :disabled="!message.trim() || sending"
            @click="sendMessage"
          >
            <span v-if="!sending">发送消息</span>
            <span v-else>发送中...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 回答展示区域 -->
    <div class="response-section">
      <div class="response-header">回答内容</div>
      <div class="response-box" ref="responseBox">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading">正在获取回答...</div>

        <!-- 正常内容区域 -->
        <div v-else>
          <!-- 如果有提取出的HTML，优先展示或并列展示 -->
          <div v-if="extractedHtml" class="html-preview-container">
            <div class="preview-label">HTML 页面预览</div>
            <iframe
              class="html-iframe"
              :srcdoc="extractedHtml"
              :style="{ height: iframeHeight + 'px' }"
              sandbox="allow-scripts allow-same-origin"
            ></iframe>
            <div
              class="resize-handle"
              @mousedown="startResize"
            ></div>
          </div>

          <!-- 原始文本内容，使用v-html以支持Mermaid等内嵌HTML -->
          <div v-if="response" ref="responseContent" class="response-content" v-html="response"></div>

          <!-- 空状态 -->
          <div v-else-if="!extractedHtml" class="empty-tip">等待发送消息/上传文件...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'FileMessageUploader',
  data() {
    return {
      // 文件上传
      selectedFile: null,
      uploading: false,

      // 消息
      message: '',
      sending: false,

      // 回答
      response: '',
      loading: false,

      extractedHtml: null,
      iframeHeight: 300,

      // 图表类型
      chartType: ''
    }
  },
  computed: {
    username() {
      return localStorage.getItem('username') || ''
    }
  },
  methods: {
    // 触发文件选择框
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    // 选择文件
    handleFileChange(e) {
      const file = e.target.files[0]
      if (file) this.selectedFile = file
    },
    
    // 拖拽文件
    handleDrop(e) {
      e.preventDefault()
      const file = e.dataTransfer.files[0]
      if (file) this.selectedFile = file
    },
    
    // 清空文件
    clearFile() {
      this.selectedFile = null
      this.$refs.fileInput.value = ''
    },
    
    // 文件大小格式化
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    // 上传文件到接口
    async uploadFile() {
      if (!this.selectedFile) return
      
      this.uploading = true
      const formData = new FormData()
      formData.append('file', this.selectedFile)
      formData.append('username', this.username)

      try {
        await axios.post('http://localhost:4567/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        alert('文件上传成功！')
        this.clearFile()
      } catch (err) {
        console.error('上传失败：', err)
        alert('文件上传失败，请检查后端服务')
      } finally {
        this.uploading = false
      }
    },
    
    // 发送消息
  async sendMessage() {
    const msg = this.message.trim()
    if (!msg) return
    
    this.sending = true
    this.loading = true
    this.response = ''
    this.extractedHtml = null // 重置之前的HTML预览
    
    try {
      const res = await axios.post('http://localhost:4567/sendmessage', {
        message: msg,
        chartType: this.chartType,
        username: this.username
      })
      
      let rawText = res.data

      // 检测并提取 ```html ... ``` 内容
      const htmlBlockRegex = /```html\s*([\s\S]*?)\s*```/i
      const match = rawText.match(htmlBlockRegex)

      if (match && match[1]) {
        let htmlContent = match[1]
        // 如果有实质HTML内容则提取到iframe，否则仅从文本中移除空壳
        if (htmlContent.trim()) {
          if (/class="mermaid"/i.test(htmlContent) || /<div\s+class=["']mermaid["']/i.test(htmlContent)) {
            htmlContent = `<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"><\/script>
<script>mermaid.initialize({ startOnLoad: true, securityLevel: 'loose' });<\/script>
${htmlContent}`
          }
          this.extractedHtml = htmlContent
        }
        // 从显示文本中移除整个 ```html ... ``` 块
        rawText = rawText.replace(match[0], '')
      }

      this.response = rawText

      // 检查原始response中是否有mermaid块，触发渲染
      if (/class="mermaid"/i.test(rawText)) {
        this.$nextTick(() => {
          this.renderMermaid()
        })
      }
      
    } catch (err) {
      console.error('发送失败：', err)
      this.response = '请求失败，请检查后端服务是否正常运行'
    } finally {
      this.sending = false
      this.loading = false
    }
  },

  // iframe 拖拽调整高度
  startResize(e) {
    e.preventDefault()
    const startY = e.clientY
    const startHeight = this.iframeHeight
    const onMove = (ev) => {
      const delta = ev.clientY - startY
      this.iframeHeight = Math.max(120, startHeight + delta)
    }
    const onUp = () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  },

  // 渲染Mermaid图表
  renderMermaid() {
    const container = this.$refs.responseContent
    if (!container) return
    const mermaidDivs = container.querySelectorAll('.mermaid')
    if (mermaidDivs.length > 0 && window.mermaid) {
      try {
        window.mermaid.run({ nodes: mermaidDivs })
      } catch (e) {
        console.warn('Mermaid渲染失败:', e)
      }
    }
  }
  },
  watch: {
    // 回答内容更新后滚动到底部并渲染Mermaid
    response() {
      this.$nextTick(() => {
        const box = this.$refs.responseBox
        if (box) box.scrollTop = box.scrollHeight
        this.renderMermaid()
      })
    }
  }
}
</script>

<style scoped>
/* 整体容器：铺满父级 */
.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* 顶部面板：上传 + 消息并排 */
.top-panel {
  display: flex;
  gap: 20px;
  flex-shrink: 0;
  margin-bottom: 16px;
}
.upload-section {
  flex: 1;
  min-width: 0;
}
.message-section {
  flex: 1;
  min-width: 0;
}

/* 上传区域 */
.upload-box {
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  padding: 18px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8fafc;
  position: relative;
}
.upload-box:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}
.file-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
}

/* 上传占位 */
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #64748b;
}
.upload-icon {
  width: 36px;
  height: 36px;
  fill: #94a3b8;
}
.upload-placeholder p {
  margin: 4px 0;
  font-size: 13px;
}
.tip {
  font-size: 11px;
  color: #94a3b8;
}

/* 文件信息 */
.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1e293b;
}
.file-icon {
  width: 32px;
  height: 32px;
  fill: #3b82f6;
  flex-shrink: 0;
}
.file-details {
  flex: 1;
  text-align: left;
  min-width: 0;
}
.file-name {
  margin: 0;
  font-weight: 500;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-size {
  margin: 0;
  font-size: 11px;
  color: #64748b;
}
.remove-file {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: none;
  background: #fecdd3;
  color: #dc2626;
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
  flex-shrink: 0;
}
.remove-file:hover {
  background: #fda4af;
}

/* 按钮通用 */
.upload-btn, .send-btn {
  width: 100%;
  margin-top: 8px;
  padding: 10px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* 上传按钮 */
.upload-btn {
  background: #3b82f6;
  color: white;
}
.upload-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}
.upload-btn:hover:not(:disabled) {
  background: #2563eb;
}

/* 消息区域 */
.message-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  resize: none;
  outline: none;
  transition: 0.2s;
  box-sizing: border-box;
  font-family: inherit;
  background: #f8fafc;
}
.message-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.send-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.chart-select {
  flex: 0 0 180px;
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  background: white;
  color: #1e293b;
  outline: none;
  cursor: pointer;
  transition: 0.2s;
  font-family: inherit;
}
.chart-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.send-btn {
  flex: 1;
  margin-top: 0;
  background: #10b981;
  color: white;
}
.send-btn:disabled {
  background: #6ee7b7;
  cursor: not-allowed;
}
.send-btn:hover:not(:disabled) {
  background: #059669;
}

/* 回答区域：填充剩余空间 */
.response-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.response-header {
  padding: 10px 16px;
  background: #f1f5f9;
  border-radius: 10px 10px 0 0;
  font-weight: 500;
  font-size: 14px;
  color: #334155;
  border: 1px solid #e2e8f0;
  border-bottom: none;
  flex-shrink: 0;
}
.response-box {
  flex: 1;
  padding: 16px;
  background: white;
  border-radius: 0 0 10px 10px;
  border: 1px solid #e2e8f0;
  overflow-y: auto;
  color: #1e293b;
  line-height: 1.6;
}
.loading {
  color: #64748b;
  text-align: center;
  padding: 20px;
}
.empty-tip {
  color: #94a3b8;
  text-align: center;
  padding: 20px;
}
.response-content {
  white-space: pre-wrap;
  padding: 8px;
}
.response-content :deep(.mermaid) {
  display: flex;
  justify-content: center;
  margin: 16px 0;
  overflow-x: auto;
}
.response-content :deep(.mermaid svg) {
  max-width: 100%;
  height: auto;
}

/* 滚动条美化 */
.response-box::-webkit-scrollbar {
  width: 6px;
}
.response-box::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

/* HTML预览 */
.html-preview-container {
  margin-bottom: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.preview-label {
  padding: 8px 12px;
  background: #f1f5f9;
  font-size: 12px;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 500;
}
.html-iframe {
  width: 100%;
  border: none;
  display: block;
}

.resize-handle {
  height: 6px;
  background: #e2e8f0;
  cursor: ns-resize;
  transition: background 0.2s;
  border-radius: 0 0 8px 8px;
}
.resize-handle:hover {
  background: #3b82f6;
}
</style>