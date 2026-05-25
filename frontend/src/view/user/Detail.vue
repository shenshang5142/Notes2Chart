<template>
    <div>
        <el-card class="box-card">
            <template #header>
                <div class="card-header">
                    <span>后台管理</span>
                    <el-button size="mini" style="float:right" @click="router.go(-1)">返回</el-button>
                </div>
            </template>
        <div>
         <a href="http://localhost:4567/admin/" class="button">点击跳转</a>
        </div>
        </el-card>
    </div>
</template>

<script setup>

</script>

<style lang="scss" scoped>

</style>
<style>
.button {
  display: inline-block;
  padding: 10px 20px;
  margin: 5px;
  background-color: #4CAF50; /* Green */
  color: white;
  text-align: center;
  text-decoration: none;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>