<template>
    <div class="home-wrapper">
        <el-container class="home-container">
            <!-- header -->
            <el-header class="custom-header">
                <el-row class="header-row" align="middle">
                    <el-col :span="4">
                        <div class="system-name-wrapper">
                            <el-icon class="logo-icon"><House /></el-icon>
                            <p class="system-name">学习笔记图表生成系统</p>
                        </div>
                    </el-col>
                    <el-col :offset="12" :span="8" class="user-info-col">
                        <el-dropdown trigger="click" @command="handleCommand">
                            <span class="el-dropdown-link">
                                <el-avatar shape="square" :size="32" :src="avatar" class="user-avatar"></el-avatar>
                                <span class="username">{{ username }}</span>
                                <el-icon class="el-icon--right arrow-icon">
                                    <ArrowDown />
                                </el-icon>
                            </span>
                            <template #dropdown>
                                <el-dropdown-menu>
                                    <el-dropdown-item command="logout">
                                        <el-icon><SwitchButton /></el-icon>
                                        退出系统
                                    </el-dropdown-item>
                                </el-dropdown-menu>
                            </template>
                        </el-dropdown>
                    </el-col>
                </el-row>
            </el-header>

            <el-container class="main-body">
                <!-- 菜单 -->
                <el-aside :width="isCollapse ? '64px' : '200px'" class="custom-aside">
                    <div class="aside-top">
                         <div class="toggle-button" @click="isCollapse = !isCollapse">
                            <el-icon :size="18">
                                <Expand v-if="isCollapse" />
                                <Fold v-else />
                            </el-icon>
                        </div>
                    </div>
                   
                    <el-menu 
                        router 
                        :default-active="activePath" 
                        class="el-menu-vertical-demo" 
                        :collapse="isCollapse"
                        :collapse-transition="true"
                    >
                        <el-menu-item index="/index" @click="saveActiveNav('/index')">
                            <el-icon><House /></el-icon>
                            <template #title>首页</template>
                        </el-menu-item>
                        
                        <!-- 修复点：修正 el-sub-menu 的 title 插槽结构 -->
                        <el-sub-menu index="1">
                            <template #title>
                                <el-icon><Setting /></el-icon>
                                <span>学习笔记</span>
                            </template>
                            <el-menu-item index="/menus/menu1">图表生成</el-menu-item>
                            <el-menu-item index="/menus/menu2">学习笔记</el-menu-item>
                            <el-menu-item index="/menus/menu3">学习成长雷达图</el-menu-item>
                        </el-sub-menu>
                        
                        <el-menu-item index="/user/detail">
                            <el-icon><User /></el-icon>
                            <template #title>用户中心</template>
                        </el-menu-item>
                        
                        <el-menu-item index="/aboutp/aboutp" @click="saveActiveNav('/aboutp/aboutp')">
                            <el-icon><InfoFilled /></el-icon>
                            <template #title>关于项目</template>
                        </el-menu-item>
                    </el-menu>
                </el-aside>

                <el-container class="content-wrapper">
                    <el-main class="custom-main">
                        <!-- 面包屑 (可选) -->
                        <!-- <Breadcrumb /> -->
                        
                        <!-- 主要内容区域，增加一个容器以便更好地控制样式 -->
                        <div class="main-content-card">
                            <router-view></router-view>
                        </div>
                    </el-main>
                    
                    <el-footer class="custom-footer">
                        <span>Copyright © 2026 学习笔记图表生成系统</span>
                    </el-footer>
                </el-container>
            </el-container>
        </el-container>
    </div>
</template>

<script setup>
import { onBeforeMount, ref, computed } from 'vue';
import avatar from "../assets/img/avator.jpg";
import { useRouter } from 'vue-router';
// 引入需要的图标，确保已注册或全局可用
import { House, Setting, User, InfoFilled, Expand, Fold, ArrowDown, SwitchButton } from '@element-plus/icons-vue';

const router = useRouter();

// 挂载 DOM 之前
onBeforeMount(() => {
    activePath.value = sessionStorage.getItem("activePath")
        ? sessionStorage.getItem("activePath")
        : "/index";
});

let isCollapse = ref(false);
let activePath = ref("");
const username = computed(() => localStorage.getItem("username") || "用户");

// 保存链接的激活状态
const saveActiveNav = (path) => {
    sessionStorage.setItem("activePath", path);
    activePath.value = path;
};

const handleCommand = (command) => {
    if (command === 'logout') {
        logout();
    }
};

const logout = () => {
    // 清除缓存
    sessionStorage.clear();
    localStorage.removeItem("username");
    router.push("/login");
};
</script>

<style scoped>
/* 全局包裹器，确保全屏 */
.home-wrapper {
    height: 100vh;
    width: 100vw;
    overflow: hidden;
}

.home-container {
    height: 100%;
    width: 100%;
    background-color: #f0f2f5; /* 更柔和的背景灰 */
}

/* --- Header 样式优化 --- */
.custom-header {
    background: linear-gradient(90deg, #274079 0%, #274079 100%); /* 渐变背景 */
    padding: 0 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    z-index: 10;
    display: flex;
    align-items: center;
    height: 60px !important; /* 固定高度 */
}

.header-row {
    width: 100%;
}

.system-name-wrapper {
    display: flex;
    align-items: center;
    color: #fff;
}

.logo-icon {
    margin-right: 10px;
    font-size: 20px;
}

.system-name {
    font-size: 18px;
    font-weight: 600;
    margin: 0;
    letter-spacing: 1px;
}

.user-info-col {
    display: flex;
    justify-content: flex-end;
    align-items: center;
}

.el-dropdown-link {
    display: flex;
    align-items: center;
    cursor: pointer;
    color: #fff;
    outline: none;
}

.user-avatar {
    margin-right: 8px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    transition: all 0.3s;
}

.user-avatar:hover {
    border-color: #fff;
    transform: scale(1.05);
}

.username {
    margin-right: 5px;
    font-size: 14px;
}

.arrow-icon {
    font-size: 12px;
}

/* --- Body 布局 --- */
.main-body {
    height: calc(100% - 60px); /* 减去 header 高度 */
}

/* --- Aside 侧边栏优化 --- */
.custom-aside {
    background: #fff;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
    transition: width 0.3s ease;
    display: flex;
    flex-direction: column;
}

.aside-top {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid #ebeef5;
}

.toggle-button {
    width: 30px;
    height: 30px;
    background-color: #f0f2f5;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #606266;
    transition: all 0.3s;
}

.toggle-button:hover {
    background-color: #e6e8eb;
    color: #274079;
}

/* 菜单样式 */
.el-menu-vertical-demo {
    border-right: none;
    height: calc(100% - 50px);
    overflow-y: auto;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
    width: 200px;
}

/* 自定义菜单项激活状态 */
:deep(.el-menu-item.is-active) {
    color: #274079 !important;
    background-color: #ecf5ff !important;
    border-right: 3px solid #274079;
}

:deep(.el-menu-item:hover) {
    background-color: #f5f7fa !important;
    color: #274079 !important;
}

:deep(.el-sub-menu__title:hover) {
    background-color: #f5f7fa !important;
    color: #274079 !important;
}

/* --- Main 内容区优化 --- */
.content-wrapper {
    background-color: #f0f2f5;
    display: flex;
    flex-direction: column;
}

.custom-main {
    padding: 20px;
    flex: 1;
    overflow-y: auto;
}

.main-content-card {
    background: #fff;
    min-height: 100%;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    padding: 20px;
    display: flex;
    flex-direction: column;
}

/* --- Footer 样式优化 --- */
.custom-footer {
    background-color: transparent;
    color: #909399;
    text-align: center;
    line-height: 40px;
    font-size: 12px;
    padding: 0;
}

/* 滚动条美化 (Webkit) */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-thumb {
    background: #dcdfe6;
    border-radius: 3px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
</style>