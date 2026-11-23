import { useEffect, useState } from 'react'

/* 动态指针时钟：SVG 表盘 + 时/分针，秒针 rAF 逐帧平滑扫动 */
export default function AnalogClock() {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    let raf
    const tick = () => {
      setNow(new Date())
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  const ms = now.getMilliseconds()
  const s = now.getSeconds() + ms / 1000
  const m = now.getMinutes() + s / 60
  const h = (now.getHours() % 12) + m / 60
  const secDeg = s * 6
  const minDeg = m * 6
  const hourDeg = h * 30

  return (
    <div className="clock-wrap" title={now.toLocaleTimeString('zh-CN')}>
      <svg className="clock-svg" viewBox="0 0 100 100" aria-label="当前时间">
        <defs>
          <linearGradient id="clockRim" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#4f8ef7" />
            <stop offset="35%" stopColor="#34d399" />
            <stop offset="70%" stopColor="#fbbf24" />
            <stop offset="100%" stopColor="#a78bfa" />
          </linearGradient>
          <linearGradient id="clockFace" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#eaf1ec" />
          </linearGradient>
          {/* userSpaceOnUse：垂直线 bbox 宽度为 0，objectBoundingBox 渐变会渲染失效 */}
          <linearGradient id="clockSec" gradientUnits="userSpaceOnUse" x1="50" y1="63" x2="50" y2="11">
            <stop offset="0%" stopColor="#ff4d5e" />
            <stop offset="100%" stopColor="#ffb347" />
          </linearGradient>
        </defs>

        <circle cx="50" cy="50" r="46.5" fill="url(#clockFace)" stroke="url(#clockRim)" strokeWidth="4" />

        {/* 刻度 */}
        {Array.from({ length: 12 }).map((_, i) => (
          <line
            key={i}
            x1="50"
            y1="9"
            x2="50"
            y2={i % 3 === 0 ? '15' : '12.5'}
            stroke={i % 3 === 0 ? '#5b6a61' : '#aebbb2'}
            strokeWidth={i % 3 === 0 ? 2.4 : 1.4}
            strokeLinecap="round"
            transform={`rotate(${i * 30} 50 50)`}
          />
        ))}

        {/* 时针 / 分针 / 秒针 */}
        <line
          x1="50" y1="52" x2="50" y2="29"
          stroke="#33403a" strokeWidth="4.6" strokeLinecap="round"
          transform={`rotate(${hourDeg} 50 50)`}
        />
        <line
          x1="50" y1="53" x2="50" y2="20"
          stroke="#5b6a61" strokeWidth="3.4" strokeLinecap="round"
          transform={`rotate(${minDeg} 50 50)`}
        />
        {/* 秒针：底层光晕线 + 主线（无针尾配重；垂直线不能用 SVG filter，bbox 为 0 会导致渲染发黑） */}
        <line
          x1="50" y1="52" x2="50" y2="11"
          stroke="rgba(255, 77, 94, 0.35)" strokeWidth="7.5" strokeLinecap="round"
          transform={`rotate(${secDeg} 50 50)`}
        />
        <line
          x1="50" y1="52" x2="50" y2="11"
          stroke="url(#clockSec)" strokeWidth="3.6" strokeLinecap="round"
          transform={`rotate(${secDeg} 50 50)`}
        />
        <circle cx="50" cy="11" r="2.8" fill="#ffd166" transform={`rotate(${secDeg} 50 50)`} />
        <circle cx="50" cy="50" r="3.4" fill="#ff4d5e" stroke="#ffffff" strokeWidth="1" />
      </svg>
    </div>
  )
}
