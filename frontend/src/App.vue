<template>
  <div class="h-screen flex flex-col">
    <div class="bg-gray-900 border-b border-gray-800 px-4 py-2 flex items-center gap-4">
      <h1 class="text-lg font-bold text-amber-400">古籍 OCR 标注平台</h1>
      <div class="flex gap-1">
        <button @click="activeTab = 'ocr'"
          class="px-4 py-1.5 rounded text-sm font-medium transition-colors"
          :class="activeTab === 'ocr' ? 'bg-amber-500 text-black' : 'text-gray-400 hover:text-white'">
          OCR 标注
        </button>
        <button @click="activeTab = 'tasks'"
          class="px-4 py-1.5 rounded text-sm font-medium transition-colors"
          :class="activeTab === 'tasks' ? 'bg-amber-500 text-black' : 'text-gray-400 hover:text-white'">
          复核任务
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-hidden">
      <div v-show="activeTab === 'ocr'" class="h-full">
        <OCRView />
      </div>
      <div v-show="activeTab === 'tasks'" class="h-full">
        <TaskPanel />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import OCRView from './components/OCRView.vue'
import TaskPanel from './components/TaskPanel.vue'

const activeTab = ref<'ocr' | 'tasks'>('ocr')
</script>
