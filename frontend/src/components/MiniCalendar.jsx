import { useEffect, useRef, useState } from 'react'

const WEEK = ['日', '一', '二', '三', '四', '五', '六']

/* 迷你日历：顶栏按钮 + 展开月历（今天多彩高亮） */
export default function MiniCalendar() {
  const [open, setOpen] = useState(false)
  const [cursor, setCursor] = useState(() => {
    const d = new Date()
    return { y: d.getFullYear(), m: d.getMonth() }
  })
  const boxRef = useRef(null)

  useEffect(() => {
    function onDoc(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const today = new Date()
  const isThisMonth = cursor.y === today.getFullYear() && cursor.m === today.getMonth()
  const firstWeekday = new Date(cursor.y, cursor.m, 1).getDay()
  const daysInMonth = new Date(cursor.y, cursor.m + 1, 0).getDate()

  const cells = []
  for (let i = 0; i < firstWeekday; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)

  const btnDate = `${today.getMonth() + 1}月${today.getDate()}日`
  const btnDow = `周${WEEK[today.getDay()]}`

  return (
    <div className="cal-wrap" ref={boxRef}>
      <button
        className={`cal-btn${open ? ' open' : ''}`}
        onClick={() => setOpen((v) => !v)}
        title="日历"
      >
        <span className="cal-btn-ico">📅</span>
        <span className="cal-btn-text">
          <b>{btnDate}</b>
          <i>{btnDow}</i>
        </span>
      </button>

      {open && (
        <div className="cal-pop">
          <div className="cal-head">
            <button className="cal-nav" onClick={() => setCursor(shift(cursor, -1))} aria-label="上个月">
              ‹
            </button>
            <span className="cal-title">
              {cursor.y} 年 {cursor.m + 1} 月
            </span>
            <button className="cal-nav" onClick={() => setCursor(shift(cursor, 1))} aria-label="下个月">
              ›
            </button>
          </div>
          <div className="cal-grid cal-week">
            {WEEK.map((w, i) => (
              <span key={w} className={`cal-w cal-w${i}`}>
                {w}
              </span>
            ))}
          </div>
          <div className="cal-grid">
            {cells.map((d, i) =>
              d === null ? (
                <span key={`empty-${i}`} />
              ) : (
                <span key={d} className={`cal-d${isThisMonth && d === today.getDate() ? ' today' : ''}`}>
                  {d}
                </span>
              ),
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function shift(c, delta) {
  const m = c.m + delta
  return { y: c.y + Math.floor(m / 12), m: ((m % 12) + 12) % 12 }
}
