<!-- src/components/AnimatedNumber.vue -->
<template>
  <span>{{ formattedValue }}</span>
</template>

<script setup>
  import { ref, watch, onMounted } from 'vue';
  import { gsap } from 'gsap';

  // 1. 定义 props，与你原来的保持一致
  const props = defineProps({
    value: {
      type: Number,
      required: true
    },
    duration: {
      type: Number,
      default: 0.1 // 将默认持续时间改为1秒
    },
    format: {
      type: String,
      // 我们将格式化的逻辑做得更完善
      default: '{value}'
    },
    fractionDigits: {
      type: Number,
      default: 1
    }
  });

  // 2. 响应式变量
  const displayValue = ref(0);
  const formattedValue = ref('');

  // 3. 更完善的格式化函数
  const formatNumber = (val) => {
    // 增加一个整数判断，如果格式化字符串里没有小数点，就不显示小数
    // return val;
    const formatted = val.toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    });
    return props.format.replace('{value}', formatted);
  };


  // 4. 动画函数，这是核心改动
  const animateValue = (newValue, oldValue ) => {
    // 确保旧值是数字
    const startValue = typeof oldValue === 'number' ? oldValue : 0;

    // 使用一个临时对象来驱动动画
    let proxy = { val: newValue };
    
    gsap.to(proxy, {
      duration: props.duration,
      val: newValue,
      // =======================================================
      // 关键所在：添加 ease 属性，使用缓动函数
      // "power2.out" 是一种常见的“缓出”效果，开始快，然后平滑地减速到终点
      // 其他推荐: "expo.out", "circ.out", "back.out(1.7)"
      ease: "power2.out", 
      // =======================================================
      onUpdate: () => {
        formattedValue.value = formatNumber(proxy.val);
      },
      // 确保动画结束时显示的是精确的目标值
      onComplete: () => {
          formattedValue.value = formatNumber(newValue);
      }
    });
  };

  // 5. 监听 props.value 的变化
  watch(() => props.value, (newValue, oldValue) => {
    animateValue(newValue, oldValue);
  });

  // 6. 组件挂载时，立即执行一次动画
  onMounted(() => {
      // 立即显示初始值，然后从初始值开始动画
      formattedValue.value = formatNumber(props.value > 0 ? 0 : props.value);
      animateValue(props.value);
  });
</script>
