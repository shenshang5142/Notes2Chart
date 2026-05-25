<template>
  <div class="about-container">
    <!-- 背景层 -->
    <div class="background-layer"></div>
    
    <!-- 内容卡片 -->
    <div class="content-card">
      <h1 class="title">关于本项目</h1>
      
      <div class="divider"></div>
      
      <p class="description">
        在信息化与数字化学习深度融合的时代，知识管理已从单纯的信息存储转向复杂的认知结构重组，这对学生和科研人员提出了新的挑战。
        <br /><br />
        随着学习过程中产生的 Markdown 和纯文本笔记数量呈指数级增长，传统的线性记录方式虽然便于快速输入，但在展现复杂知识体系的拓扑结构、逻辑推演及多维数据对比方面存在显著局限。
        <br /><br />
        面对大规模的学习资料，如何突破扁平化文本的束缚，通过可视化技术辅助学习者构建宏观的知识图谱，已成为教育技术领域亟待解决的关键问题。
      </p>

      <div class="footer-info">
        <span class="year-badge">Est. 2026</span>
      </div>
    </div>
  </div>
</template>

<script setup>
// 如果后续需要逻辑可以在此添加
</script>

<style scoped>
/* 容器：全屏居中 */
.about-container {
  position: relative;
  width: 100%;
  height: 100vh; /* 或者 100% 取决于父容器 */
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 背景层：处理原有背景图 */
.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("../assets/img/index.gif");
  background-repeat: no-repeat;
  background-size: cover; /* 改为 cover 以填充屏幕 */
  background-position: center bottom;
  z-index: 0;
  filter: blur(2px); /* 轻微模糊背景，突出前景 */
}

/* 内容卡片：磨砂玻璃效果 */
.content-card {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.85); /* 半透明白色 */
  backdrop-filter: blur(10px); /* 磨砂效果 */
  -webkit-backdrop-filter: blur(10px);
  padding: 40px 50px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  width: 90%;
  text-align: center;
  animation: fadeInUp 0.8s ease-out;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* 标题样式 */
.title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
  font-weight: 700;
  letter-spacing: 1px;
}

/* 分割线 */
.divider {
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #66b1ff);
  margin: 0 auto 30px auto;
  border-radius: 2px;
}

/* 正文样式 */
.description {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #555;
  text-align: justify; /* 两端对齐更整齐 */
  margin-bottom: 40px;
}

/* 底部信息 */
.footer-info {
  margin-top: 20px;
}

/* 年份徽章 */
.year-badge {
  display: inline-block;
  padding: 8px 20px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
  border: 1px solid #d9ecff;
  transition: all 0.3s ease;
}

.year-badge:hover {
  background-color: #409eff;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

/* 简单入场动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .content-card {
    padding: 30px 20px;
    width: 95%;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .description {
    font-size: 1rem;
    text-align: left; /* 移动端左对齐更易读 */
  }
}
</style>