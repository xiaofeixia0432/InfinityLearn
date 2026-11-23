import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../AuthContext.jsx'
import { cleanTextForSpeech, useSpeech } from '../hooks/useSpeech.js'
import Loader from '../components/Loader.jsx'
import EmptyState from '../components/EmptyState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import {
  todayStr,
  daysAgoStr,
  weekdayOf,
  dayOfMonth,
  moduleVars,
  difficultyText,
  difficultyBadgeClass,
} from '../utils.js'

export default function Daily() {
  const { user } = useAuth()

  const [dates, setDates] = useState(null) // 近 30 天（历史永久保留，可回看）
  const [date, setDate] = useState(todayStr())
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busyId, setBusyId] = useState(null)

  /* 日期列表：接口返回 + 兜底今天，降序（最新在前） */
  const loadDates = useCallback(async () => {
    try {
      const d = await api.get('/api/dates?limit=30')
      const list = Array.isArray(d.dates) ? d.dates.filter(Boolean) : []
      const t = todayStr()
      const all = list.includes(t) ? list : [t, ...list]
      all.sort()
      all.reverse()
      setDates(all)
    } catch {
      setDates([todayStr()])
    }
  }, [])

  const loadDaily = useCallback(async (d) => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get(`/api/daily?date=${d}`)
      setData(res)
    } catch (e) {
      setError(e.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDates()
  }, [loadDates])

  useEffect(() => {
    loadDaily(date)
  }, [date, loadDaily])

  /* 按模块分组（保持返回顺序） */
  const groups = useMemo(() => {
    if (!data || !Array.isArray(data.items)) return []
    const map = new Map()
    for (const it of data.items) {
      if (!map.has(it.module_code)) map.set(it.module_code, [])
      map.get(it.module_code).push(it)
    }
    return Array.from(map.entries()).map(([mc, items]) => ({
      module_code: mc,
      module_name: items[0].module_name,
      module_color: items[0].module_color,
      icon: items[0].icon,
      items,
    }))
  }, [data])

  async function mark(articleId, status) {
    if (busyId) return
    setBusyId(articleId)
    try {
      await api.authPost(`/api/progress/${articleId}`, { status })
      setData((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          items: prev.items.map((it) =>
            Number(it.article_id) === Number(articleId) ? { ...it, status } : it,
          ),
        }
      })
    } catch {
      /* 失败静默，状态保持 */
    } finally {
      setBusyId(null)
    }
  }

  const selected = date
  const itemCount = data && Array.isArray(data.items) ? data.items.length : 0

  return (
    <div>
      <div className="daily-head">
        <h1 className="section-title" style={{ margin: 0 }}>
          每日学习
        </h1>
        <span className="muted" style={{ fontSize: 13.5 }}>
          {selected === todayStr() ? '今天' : selected} · 共 {itemCount} 篇
        </span>
      </div>

      {/* 日期选择：近 30 天快捷条（横向滚动）+ 一年内任意日期跳转 */}
      {dates === null ? (
        <Loader text="日期加载中…" />
      ) : (
        <div className="date-toolbar">
          <div className="date-strip">
            {dates.map((d) => (
              <button
                key={d}
                className={`date-chip${d === selected ? ' active' : ''}`}
                onClick={() => setDate(d)}
              >
                <span className="dc-dow">周{weekdayOf(d)}</span>
                <span className="dc-day">{dayOfMonth(d)}</span>
                <span className="dc-dow">{d === todayStr() ? '今天' : d.slice(5, 7) + '月'}</span>
              </button>
            ))}
          </div>
          <input
            type="date"
            className="date-jump"
            title="跳转到一年内的任意日期"
            min={daysAgoStr(364)}
            max={todayStr()}
            value={selected}
            onChange={(e) => e.target.value && setDate(e.target.value)}
          />
        </div>
      )}

      {!user && (
        <p className="muted" style={{ fontSize: 13.5, marginBottom: 16 }}>
          💡 <Link to="/login" style={{ color: 'var(--brand)' }}>登录</Link>
          后可记录学习进度
        </p>
      )}

      {/* 按模块分组的彩色清单 */}
      {loading ? (
        <Loader />
      ) : error ? (
        <ErrorState message={error} onRetry={() => loadDaily(selected)} />
      ) : groups.length === 0 ? (
        <EmptyState text="这一天没有安排学习内容，挑个别的日期看看吧" emoji="🗓" />
      ) : (
        groups.map((g) => (
          <section key={g.module_code} className="daily-group" style={moduleVars(g.module_code, g.module_color)}>
            <div className="daily-group-head">
              <span className="dg-ico">{g.icon || '📚'}</span>
              <span>{g.module_name}</span>
              <span className="dg-count">{g.items.length} 篇</span>
            </div>
            {g.items.map((it) => (
              <DailyItem
                key={`${g.module_code}-${it.article_id}`}
                item={it}
                loggedIn={!!user}
                busy={busyId === Number(it.article_id)}
                onMark={mark}
              />
            ))}
          </section>
        ))
      )}
    </div>
  )
}

function DailyItem({ item, loggedIn, busy, onMark }) {
  const status = item.status
  const sp = useSpeech()

  function toggleSpeak() {
    if (sp.speaking) sp.stop()
    else sp.speak(cleanTextForSpeech(`${item.title}。${item.summary || ''}`))
  }

  return (
    <div className="daily-item">
      <span className="di-accent" />
      <div className="di-body">
        <Link to={`/article/${item.article_id}`} className="di-title">
          {item.title}
        </Link>
        <div className="di-meta">
          <span className={difficultyBadgeClass(item.difficulty)}>
            {difficultyText(item.difficulty)}
          </span>
          {item.duration_minutes != null && <span>⏱ {item.duration_minutes} 分钟</span>}
        </div>
      </div>
      <div className="di-actions" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {sp.supported && (
          <button
            className={`spk-mini${sp.speaking ? ' on' : ''}`}
            onClick={toggleSpeak}
            title={sp.speaking ? '停止朗读' : '朗读标题和摘要'}
          >
            {sp.speaking ? '⏹' : '🔊'}
          </button>
        )}
        {status === 'completed' ? (
          <>
            <span className="status-pill status-completed">✓ 已完成</span>
            {loggedIn && (
              <button
                className="btn btn-ghost btn-sm"
                disabled={busy}
                onClick={() => onMark(item.article_id, 'learning')}
              >
                重新学习
              </button>
            )}
          </>
        ) : status === 'learning' ? (
          <>
            <span className="status-pill status-learning">学习中</span>
            {loggedIn && (
              <button
                className="btn btn-primary btn-sm"
                disabled={busy}
                onClick={() => onMark(item.article_id, 'completed')}
              >
                标记完成
              </button>
            )}
          </>
        ) : (
          <>
            <span className="muted" style={{ fontSize: 12 }}>
              未开始
            </span>
            {loggedIn && (
              <button
                className="btn btn-ghost btn-sm"
                disabled={busy}
                onClick={() => onMark(item.article_id, 'learning')}
              >
                开始学习
              </button>
            )}
          </>
        )}
      </div>
    </div>
  )
}
