<template>
    <!-- 
      1. 根容器，实现了我们之前讨论的Flexbox布局方案。
      它会自适应父容器的高度。
    -->
    <div class="app-table-container">
      <el-table
        v-bind="$attrs" 
        style="width: 100%"
        height="100%" 
      >
        <!-- 
          2. 使用 <slot> 将父组件中定义的所有 <el-table-column> 
             “透传”进来。
        -->
        <slot></slot>
  
        <!-- 3. (可选) 可以在这里添加一些所有表格都共有的列，比如操作列 -->
        <slot name="actions"></slot>
  
      </el-table>
    </div>
  </template>
  
  <script>
  // 使用 Options API 风格
  export default {
    name: 'AppTable',
    // 4. inheritAttrs: false 是一个关键配置
    // 它能防止父组件传递的属性（如 data, loading）被错误地应用到
    // .app-table-container 这个 div 上。
    inheritAttrs: false,
  }
  </script>
  
  <style scoped>
  .app-table-container {
    /* 
      5. 这是解决 ResizeObserver 问题的核心CSS。
      它创建了一个高度稳定的Flex容器。
    */
    width: 100%;
    height: 100%; /* 默认情况下，它会尝试充满父容器 */
    flex-grow: 1; /* 在Flex布局中，它会占据所有可用空间 */
    overflow: hidden; /* 防止内部表格溢出 */
    position: relative; /* 为内部元素提供定位上下文 */
    display: flex; /* 确保在某些布局下表现一致 */
  }
  
  /* (可选) 在这里添加一些全局的、你想让所有表格都拥有的样式 */
  :deep(.el-table th.el-table__cell) {
    background-color: #f9fafb;
    color: #6b7280;
  }
  </style>