<script>
import FHeader from "@/views/components/FHeader.vue";
import FFooter from "@/views/components/FFooter.vue";

export default {
  components: {
    FHeader,
    FFooter,
  },
};
</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <FHeader></FHeader>
      </el-header>
      <el-main class="app-main">
        <router-view></router-view>
      </el-main>
      <el-footer>
        <FFooter></FFooter>
      </el-footer>
    </el-container>
  </div>
</template>

<style scoped>
</style>