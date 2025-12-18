<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watchEffect } from 'vue'

// 原始数据
const tableData = ref([
    { resistances: '0', ticks: '25.0' },
    { resistances: '10', ticks: '23.0' },
    { resistances: '20', ticks: '21.2' },
    { resistances: '30', ticks: '19.7' },
    { resistances: '60', ticks: '16.1' },
    { resistances: '90', ticks: '13.8' },
    { resistances: '120', ticks: '12.0' },
    { resistances: '280', ticks: '7.0' },
    { resistances: '360', ticks: '5.9' },
    { resistances: '480', ticks: '4.9' },
    { resistances: '600', ticks: '4.0' },
    { resistances: '1000', ticks: '2.6' },
    { resistances: '2000', ticks: '1.4' },
    { resistances: '3000', ticks: '1.0' },
])

// 将数据拆分为两部分
const firstHalfTableData = computed(() => 
    tableData.value.slice(0, Math.ceil(tableData.value.length / 2))
)
const secondHalfTableData = computed(() => 
    tableData.value.slice(Math.ceil(tableData.value.length / 2))
)

// 计算用于绘图的数据
const resistancesList = computed(() => tableData.value.map(item => item.resistances))
const ticksList = computed(() => tableData.value.map(item => item.ticks))

// 画布相关
const canvasWidth = ref(700)
const canvasHeight = ref(700)
const dialCanvas = ref<HTMLCanvasElement | null>(null)
const isMobile = ref(false)

const updateCanvasSize = () => {
    if (window.innerWidth < 768) {
        canvasWidth.value = Math.min(400, window.innerWidth - 40)
        canvasHeight.value = canvasWidth.value + 100
        isMobile.value = true
    } else {
        canvasWidth.value = 700
        canvasHeight.value = 700
        isMobile.value = false
    }
}

const drawDial = () => {
    const canvas = dialCanvas.value
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

    const centerX = canvasWidth.value / 2
    const centerY = canvasHeight.value / 2
    const radius = Math.min(centerX, centerY) * 0.85

    const angles = ticksList.value.map(tick => 
        (parseFloat(tick) / 25) * (2 / 3) * Math.PI - (Math.PI * 5 / 6)
    )

    // 绘制主刻度线和电阻标签
    angles.forEach((angle, index) => {
        const resistance = resistancesList.value[index]
        const startX = centerX + radius * Math.cos(angle)
        const startY = centerY + radius * Math.sin(angle)
        const endX = centerX + (radius - 35) * Math.cos(angle)
        const endY = centerY + (radius - 35) * Math.sin(angle)

        ctx.beginPath()
        ctx.moveTo(startX, startY)
        ctx.lineTo(endX, endY)
        ctx.strokeStyle = '#e74c3c'
        ctx.lineWidth = 2
        ctx.stroke()

        const labelDistance = isMobile.value ? radius + 25 : radius - 45
        const labelX = centerX + labelDistance * Math.cos(angle)
        const labelY = centerY + labelDistance * Math.sin(angle)
        ctx.font = isMobile.value ? '11px Arial' : '13px Arial'
        ctx.fillStyle = '#2c3e50'
        ctx.textAlign = angle < -Math.PI / 3 ? 'left' : angle > -2 * Math.PI / 3 ? 'right' : 'center'
        ctx.fillText(`${resistance}Ω`, labelX, labelY)
    })

    // 绘制细分刻度
    for (let i = 0; i <= 100; i++) {
        const angle = (i / 100) * (2 / 3) * Math.PI - (Math.PI * 5 / 6)
        const startX = centerX + radius * Math.cos(angle)
        const startY = centerY + radius * Math.sin(angle)
        const tickLength = i % 10 === 0 ? 20 : 10
        const endX = centerX + (radius - tickLength) * Math.cos(angle)
        const endY = centerY + (radius - tickLength) * Math.sin(angle)

        ctx.beginPath()
        ctx.moveTo(startX, startY)
        ctx.lineTo(endX, endY)
        ctx.strokeStyle = i % 10 === 0 ? '#7f8c8d' : '#bdc3c7'
        ctx.lineWidth = i % 10 === 0 ? 1.5 : 1
        ctx.stroke()

        if (i % 10 === 0) {
            const labelX = centerX + (radius - 30) * Math.cos(angle)
            const labelY = centerY + (radius - 30) * Math.sin(angle)
            ctx.font = isMobile.value ? '9px Arial' : '11px Arial'
            ctx.fillStyle = '#7f8c8d'
            ctx.textAlign = 'center'
            ctx.fillText(`${i}μA`, labelX, labelY)

            if (i === 50) {
                ctx.font = isMobile.value ? '12px Arial' : '14px Arial'
                ctx.fillStyle = '#2c3e50'
                ctx.fillText('R中', labelX, labelY - 45)
            }
        }
    }
}

onMounted(() => {
    updateCanvasSize()
    drawDial()
    window.addEventListener('resize', updateCanvasSize)
    window.addEventListener('resize', drawDial)
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', updateCanvasSize)
    window.removeEventListener('resize', drawDial)
})

watchEffect(() => {
    drawDial()
})
</script>

<template>
    <div class="ohmmeter-tool">
        <div class="tool-header">
            <h2>电表改装——欧姆表表头自动绘制工具</h2>
            <p class="subtitle">修改表格数据，表盘将实时更新。完成后可将页面另存为 PDF 打印。</p>
        </div>

        <div class="tool-content">
            <!-- 数据输入区 -->
            <div class="data-section">
                <h3>数据输入</h3>
                <div class="tables-container">
                    <div class="table-wrapper">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Rx / Ω</th>
                                    <th>刻度</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(row, index) in firstHalfTableData" :key="'first-' + index">
                                    <td>
                                        <input 
                                            v-model="row.resistances" 
                                            type="text" 
                                            class="data-input"
                                            placeholder="电阻值"
                                        />
                                    </td>
                                    <td>
                                        <input 
                                            v-model="row.ticks" 
                                            type="text" 
                                            class="data-input"
                                            placeholder="刻度值"
                                        />
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="table-wrapper">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Rx / Ω</th>
                                    <th>刻度</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(row, index) in secondHalfTableData" :key="'second-' + index">
                                    <td>
                                        <input 
                                            v-model="row.resistances" 
                                            type="text" 
                                            class="data-input"
                                            placeholder="电阻值"
                                        />
                                    </td>
                                    <td>
                                        <input 
                                            v-model="row.ticks" 
                                            type="text" 
                                            class="data-input"
                                            placeholder="刻度值"
                                        />
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 表盘预览区 -->
            <div class="preview-section">
                <h3>表盘预览</h3>
                <div class="canvas-container">
                    <canvas ref="dialCanvas" :width="canvasWidth" :height="canvasHeight"></canvas>
                </div>
            </div>
        </div>

        <div class="tool-footer">
            <div class="info-box">
                <p>💡 <strong>使用提示：</strong></p>
                <ul>
                    <li>在表格中填写实验测得的电阻值和对应刻度</li>
                    <li>表盘会实时更新显示</li>
                    <li>完成后使用浏览器"打印"功能，选择"另存为 PDF"即可保存</li>
                </ul>
            </div>
        </div>
    </div>
</template>

<style scoped>
.ohmmeter-tool {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.tool-header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid #e8e8e8;
}

.tool-header h2 {
    color: #2c3e50;
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.subtitle {
    color: #7f8c8d;
    font-size: 0.95rem;
    margin: 0;
}

.tool-content {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
}

.data-section,
.preview-section {
    background: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.data-section h3,
.preview-section h3 {
    color: #34495e;
    font-size: 1.2rem;
    margin: 0 0 1rem 0;
    font-weight: 600;
}

.tables-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.table-wrapper {
    overflow-x: auto;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    background: #fafafa;
    border-radius: 6px;
    overflow: hidden;
}

.data-table thead {
    background: #f5f5f5;
}

.data-table th {
    padding: 0.75rem;
    text-align: center;
    color: #1976d2 !important;
    font-weight: 600;
    font-size: 0.9rem;
    border-bottom: 2px solid #90caf9 !important;
    /* background: #e3f2fd ; */
}

.data-table td {
    padding: 0.5rem;
    text-align: center;
    border-bottom: 1px solid #eeeeee;
}

.data-table tbody tr:last-child td {
    border-bottom: none;
}

.data-table tbody tr:hover {
    background: #f9f9f9;
}

.data-input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
    text-align: center;
    transition: all 0.2s;
    background: white ;
    color: #2c3e50;
}

.data-input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.canvas-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
    background: #fafafa;
    border-radius: 6px;
}

canvas {
    max-width: 100%;
    height: auto;
}

.tool-footer {
    margin-top: 2rem;
}

.info-box {
    background: #f8f9fa;
    border-left: 4px solid #3498db;
    padding: 1rem 1.5rem;
    border-radius: 4px;
}

.info-box p {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
    font-size: 0.95rem;
}

.info-box ul {
    margin: 0.5rem 0 0 0;
    padding-left: 1.5rem;
}

.info-box li {
    color: #555;
    font-size: 0.9rem;
    line-height: 1.6;
    margin-bottom: 0.3rem;
}

@media (max-width: 768px) {
    .tool-header h2 {
        font-size: 1.4rem;
    }

    .subtitle {
        font-size: 0.85rem;
    }

    .tables-container {
        grid-template-columns: 1fr;
    }

    .data-section,
    .preview-section {
        padding: 1rem;
    }
    
    .info-box {
        padding: 0.75rem 1rem;
    }
}

@media print {
    .data-section {
        display: none;
    }

    .tool-footer {
        display: none;
    }

    .preview-section {
        border: none;
        box-shadow: none;
    }
}
</style>
