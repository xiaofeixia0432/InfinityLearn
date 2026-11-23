/* 学习模块默认配色兜底（接口 color 字段缺失时使用） */
export const FALLBACK_MODULES = [
  { code: 'english', name: '英语学习', icon: '💬', color: '#4f8ef7', parent_code: null },
  { code: 'embedded', name: '嵌入式开发', icon: '🔧', color: '#34d399', parent_code: null },
  { code: 'ecommerce', name: '电商实战', icon: '🛒', color: '#fb923c', parent_code: null },
  { code: 'science', name: '科学探索', icon: '🔬', color: '#a78bfa', parent_code: null },
  { code: 'finance', name: '金融理财', icon: '💰', color: '#fbbf24', parent_code: null },
  { code: 'python', name: 'Python 编程', icon: '🐍', color: '#facc15', parent_code: null },
  { code: 'python_crawler', name: 'Python 爬虫', icon: '🕷️', color: '#38bdf8', parent_code: 'python' },
  { code: 'python_fastapi', name: 'FastAPI 后端开发', icon: '⚡', color: '#14b8a6', parent_code: 'python' },
  { code: 'ai', name: '人工智能', icon: '🤖', color: '#a78bfa', parent_code: null },
  { code: 'agent', name: '大模型 Agent', icon: '🧠', color: '#34d399', parent_code: null },
]

export function moduleColorOf(code, color) {
  if (color && typeof color === 'string' && color.trim()) return color.trim()
  const m = FALLBACK_MODULES.find((x) => x.code === code)
  return m ? m.color : '#3fbf8f'
}

export function hexToRgba(hex, alpha) {
  let h = String(hex || '').replace('#', '')
  if (h.length === 3) h = h.split('').map((c) => c + c).join('')
  const n = parseInt(h, 16)
  if (Number.isNaN(n) || h.length !== 6) return `rgba(63,191,143,${alpha})`
  const r = (n >> 16) & 255
  const g = (n >> 8) & 255
  const b = n & 255
  return `rgba(${r},${g},${b},${alpha})`
}

/* 注入模块色 CSS 变量（顶条 / 图标底色 / 悬停光效 / 徽章底） */
export function moduleVars(code, color) {
  const c = moduleColorOf(code, color)
  return {
    '--mc': c,
    '--mc-glow': hexToRgba(c, 0.18),
    '--mc-ico-bg': hexToRgba(c, 0.14),
    '--mc-ico-bd': hexToRgba(c, 0.35),
    '--mc-chip-bg': hexToRgba(c, 0.13),
  }
}

/* 难度映射：1=入门 2=进阶 3=高级 */
export const DIFFICULTY_TEXT = { 1: '入门', 2: '进阶', 3: '高级' }

export function difficultyText(d) {
  return DIFFICULTY_TEXT[d] || '入门'
}

export function difficultyBadgeClass(d) {
  return `badge badge-d${d >= 1 && d <= 3 ? d : 1}`
}

/* ---------- 日期工具 ---------- */
export function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(
    d.getDate(),
  ).padStart(2, '0')}`
}

/* n 天前的日期字符串（用于日期选择器的可选范围） */
export function daysAgoStr(n) {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(
    d.getDate(),
  ).padStart(2, '0')}`
}

const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

export function weekdayOf(dateStr) {
  const d = new Date(`${dateStr}T00:00:00`)
  if (Number.isNaN(d.getTime())) return ''
  return WEEKDAYS[d.getDay()]
}

export function dayOfMonth(dateStr) {
  const parts = String(dateStr || '').split('-')
  return parts[2] ? String(Number(parts[2])) : dateStr
}

export function greeting() {
  const h = new Date().getHours()
  if (h < 5) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
}

export function fullDate() {
  const d = new Date()
  return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月 ${d.getDate()} 日 · 星期${WEEKDAYS[d.getDay()]}`
}

/* ISO 时间 → YYYY-MM-DD */
export function shortDate(iso) {
  if (!iso) return ''
  return String(iso).slice(0, 10)
}

export function fmtViews(n) {
  const v = Number(n) || 0
  if (v >= 10000) return `${(v / 10000).toFixed(1)}w`
  return String(v)
}
