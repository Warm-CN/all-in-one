<template>
  <div class="relative" ref="containerRef">
    <img
      ref="imgRef"
      :src="imageSrc"
      class="block max-w-full select-none"
      @load="onImageLoad"
      draggable="false"
    />
    <canvas
      ref="canvasRef"
      class="absolute top-0 left-0"
      :width="canvasWidth"
      :height="canvasHeight"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      :style="{ cursor: cursorStyle }"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  imageSrc: String,
  tool: { type: String, default: 'rect' },
  annotations: { type: Array, default: () => [] }
})
const emit = defineEmits(['add-annotation'])

const containerRef = ref(null)
const imgRef = ref(null)
const canvasRef = ref(null)
const canvasWidth = ref(0)
const canvasHeight = ref(0)
const isDrawing = ref(false)
const startPos = ref(null)
const currentPath = ref([])
const cursorStyle = ref('crosshair')

function onImageLoad() {
  nextTick(() => {
    const img = imgRef.value
    canvasWidth.value = img.clientWidth
    canvasHeight.value = img.clientHeight
    redraw()
  })
}

function getCtx() {
  return canvasRef.value.getContext('2d')
}

function redraw() {
  const ctx = getCtx()
  if (!ctx) return
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  for (const ann of props.annotations) {
    drawAnnotation(ctx, ann)
  }
  if (isDrawing.value) {
    if (props.tool === 'rect' && startPos.value) {
      ctx.strokeStyle = '#3B82F6'
      ctx.lineWidth = 2
      ctx.setLineDash([6, 4])
      const s = startPos.value
      ctx.strokeRect(s.x, s.y, currentPath.value[0] - s.x, currentPath.value[1] - s.y)
      ctx.setLineDash([])
    } else if (props.tool === 'freehand' && currentPath.value.length > 1) {
      ctx.strokeStyle = '#3B82F6'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(currentPath.value[0][0], currentPath.value[0][1])
      for (let i = 1; i < currentPath.value.length; i++) {
        ctx.lineTo(currentPath.value[i][0], currentPath.value[i][1])
      }
      ctx.stroke()
    }
  }
}

function drawAnnotation(ctx, ann) {
  ctx.strokeStyle = ann.color
  ctx.fillStyle = ann.color
  ctx.lineWidth = 2
  ctx.font = '14px sans-serif'
  if (ann.type === 'rect') {
    const c = ann.coords
    ctx.strokeRect(c.x, c.y, c.w, c.h)
    const label = ann._label || ''
    ctx.fillStyle = ann.color
    ctx.fillRect(c.x, c.y - 20, 24, 20)
    ctx.fillStyle = '#fff'
    ctx.fillText(label, c.x + 4, c.y - 6)
    ctx.fillStyle = ann.color
  } else if (ann.type === 'freehand') {
    const pts = ann.coords.points
    if (!pts || pts.length < 2) return
    ctx.beginPath()
    ctx.moveTo(pts[0][0], pts[0][1])
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1])
    ctx.closePath()
    ctx.stroke()
    const label = ann._label || ''
    ctx.fillStyle = ann.color
    ctx.fillRect(pts[0][0], pts[0][1] - 20, 24, 20)
    ctx.fillStyle = '#fff'
    ctx.fillText(label, pts[0][0] + 4, pts[0][1] - 6)
    ctx.fillStyle = ann.color
  } else if (ann.type === 'text') {
    const c = ann.coords
    ctx.fillStyle = 'rgba(255,255,255,0.85)'
    const w = ctx.measureText(ann.text).width + 12
    ctx.fillRect(c.x - 6, c.y - 14, w, 22)
    ctx.fillStyle = ann.color
    ctx.fillText(ann.text, c.x, c.y + 2)
  }
}

function getPos(e) {
  const rect = canvasRef.value.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

function onMouseDown(e) {
  const pos = getPos(e)
  if (props.tool === 'text') {
    emit('add-annotation', { type: 'text', coords: { x: pos.x, y: pos.y } })
    return
  }
  isDrawing.value = true
  startPos.value = pos
  if (props.tool === 'freehand') {
    currentPath.value = [[pos.x, pos.y]]
  } else {
    currentPath.value = [pos.x, pos.y]
  }
}

function onMouseMove(e) {
  if (!isDrawing.value) return
  const pos = getPos(e)
  if (props.tool === 'freehand') {
    currentPath.value.push([pos.x, pos.y])
  } else {
    currentPath.value = [pos.x, pos.y]
  }
  redraw()
}

function onMouseUp(e) {
  if (!isDrawing.value) return
  isDrawing.value = false
  const pos = getPos(e)
  if (props.tool === 'rect') {
    const s = startPos.value
    const w = pos.x - s.x
    const h = pos.y - s.y
    if (Math.abs(w) > 5 && Math.abs(h) > 5) {
      emit('add-annotation', {
        type: 'rect',
        coords: { x: Math.min(s.x, pos.x), y: Math.min(s.y, pos.y), w: Math.abs(w), h: Math.abs(h) }
      })
    }
  } else if (props.tool === 'freehand') {
    if (currentPath.value.length > 2) {
      emit('add-annotation', {
        type: 'freehand',
        coords: { points: [...currentPath.value] }
      })
    }
  }
  startPos.value = null
  currentPath.value = []
  redraw()
}

watch(() => props.annotations, () => {
  nextTick(redraw)
}, { deep: true })

onMounted(() => {
  nextTick(redraw)
})
</script>
