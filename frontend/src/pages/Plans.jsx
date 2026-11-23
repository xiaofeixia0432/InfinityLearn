import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../AuthContext.jsx'
import { useModules } from '../hooks.js'
import Loader from '../components/Loader.jsx'
import EmptyState from '../components/EmptyState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import { moduleColorOf, difficultyText, difficultyBadgeClass } from '../utils.js'

const DAY_OPTIONS = [7, 14, 21, 30]
const COUNT_OPTIONS = [1, 2, 3, 5]

export default function Plans() {
  const { user } = useAuth()
  const { modules } = useModules()

  const [plans, setPlans] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // 创建表单
  const [name, setName] = useState('')
  const [picked, setPicked] = useState([])
  const [days, setDays] = useState(14)
  const [dailyCount, setDailyCount] = useState(2)
  const [creating, setCreating] = useState(false)
  const [formError, setFormError] = useState('')

  const [openId, setOpenId] = useState(null)
  const [detail, setDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [busyItem, setBusyItem] = useState(null)

  const loadPlans = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.authGet('/api/plans')
      setPlans(Array.isArray(res.items) ? res.items : [])
    } catch (e) {
      setError(e.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (user) loadPlans()
    else setLoading(false)
  }, [user, loadPlans])

  function togglePick(code) {
    setPicked((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code],
    )
  }

  async function createPlan(e) {
    e.preventDefault()
    setFormError('')
    if (!name.trim()) return setFormError('请给计划起个名字')
    if (picked.length === 0) return setFormError('请至少选择一个学习模块')
    setCreating(true)
    try {
      const created = await api.authPost('/api/plans', {
        name: name.trim(),
        module_codes: picked,
        days,
        daily_count: dailyCount,
      })
      setOpenId(created.id)
      setDetail(created)
      setName('')
      setPicked([])
      await loadPlans()
    } catch (err) {
      setFormError(err.message || '创建失败')
    } finally {
      setCreating(false)
    }
  }

  async function openPlan(id) {
    if (openId === id) {
      setOpenId(null)
      setDetail(null)
      return
    }
    setOpenId(id)
    setDetail(null)
    setDetailLoading(true)
    try {
      setDetail(await api.authGet(`/api/plans/${id}`))
    } catch {
      setOpenId(null)
    } finally {
      setDetailLoading(false)
    }
  }

  async function toggleItem(itemId) {
    if (busyItem || !detail || openId == null) return
    setBusyItem(itemId)
    try {
      const res = await api.authPost(`/api/plans/${openId}/items/${itemId}/complete`, {})
      setDetail((prev) =>
        prev
          ? {
              ...prev,
              done_count: res.done_count,
              total_count: res.total_count,
              items: prev.items.map((it) =>
                it.id === res.item_id ? { ...it, completed: res.completed } : it,
              ),
            }
          : prev,
      )
      setPlans((prev) =>
        prev
          ? prev.map((p) =>
              p.id === openId ? { ...p, done_count: res.done_count, total_count: res.total_count } : p,
            )
          : prev,
      )
    } catch {
      /* 静默 */
    } finally {
      setBusyItem(null)
    }
  }

  async function removePlan(id) {
    if (!window.confirm('确定删除该计划吗？打卡记录将一并删除')) return
    try {
      await api.post(`/api/plans/${id}`, undefined, { auth: true })
      if (openId === id) {
        setOpenId(null)
        setDetail(null)
      }
      await loadPlans()
    } catch {
      /* 静默 */
    }
  }

  const dayGroups = useMemo(() => {
    if (!detail || !Array.isArray(detail.items)) return []
    const map = new Map()
    for (const it of detail.items) {
      if (!map.has(it.day_index)) map.set(it.day_index, [])
      map.get(it.day_index).push(it)
    }
    return Array.from(map.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([day, items]) => ({ day, items }))
  }, [detail])

  if (!user) {
    return (
      <div>
        <h1 className="section-title">学习计划</h1>
        <EmptyState
          emoji="🗓"
          text={
            <>
              登录后即可定制专属学习计划：
              <Link to="/login" style={{ color: 'var(--brand)' }}>
                去登录
              </Link>
              或
              <Link to="/register" style={{ color: 'var(--brand)' }}>
                免费注册
              </Link>
            </>
          }
        />
      </div>
    )
  }

  return (
    <div>
      <h1 className="section-title">学习计划</h1>
      <p className="muted" style={{ marginTop: -6, fontSize: 13.5 }}>
        选模块、定周期，系统自动排好每天学什么，逐日打卡直到完成
      </p>

      {/* 创建计划 */}
      <form className="card plan-form" onSubmit={createPlan}>
        <div className="pf-row">
          <input
            className="pf-name"
            placeholder="计划名称，如：两周入门嵌入式"
            maxLength={60}
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <div className="pf-row">
          <span className="pf-label">学习模块</span>
          <div className="pf-modules">
            {modules
              .filter((m) => (Number(m.article_count) || 0) > 0)
              .map((m) => {
              const on = picked.includes(m.code)
              const color = moduleColorOf(m.code, m.color)
              return (
                <button
                  type="button"
                  key={m.code}
                  className={`pf-chip${on ? ' on' : ''}`}
                  style={on ? { borderColor: color, color, background: `${color}1f` } : undefined}
                  onClick={() => togglePick(m.code)}
                >
                  {m.icon} {m.name}
                </button>
              )
            })}
          </div>
        </div>
        <div className="pf-row">
          <span className="pf-label">计划周期</span>
          <div className="pf-opts">
            {DAY_OPTIONS.map((d) => (
              <button
                type="button"
                key={d}
                className={`pf-chip${days === d ? ' on' : ''}`}
                onClick={() => setDays(d)}
              >
                {d} 天
              </button>
            ))}
          </div>
        </div>
        <div className="pf-row">
          <span className="pf-label">每天篇数</span>
          <div className="pf-opts">
            {COUNT_OPTIONS.map((c) => (
              <button
                type="button"
                key={c}
                className={`pf-chip${dailyCount === c ? ' on' : ''}`}
                onClick={() => setDailyCount(c)}
              >
                {c} 篇
              </button>
            ))}
          </div>
        </div>
        {formError && <p className="pf-error">⚠ {formError}</p>}
        <button className="btn btn-primary" disabled={creating}>
          {creating ? '正在生成计划…' : `生成计划（${days} 天 × ${dailyCount} 篇 = ${days * dailyCount} 篇）`}
        </button>
      </form>

      {/* 计划列表 */}
      {loading ? (
        <Loader />
      ) : error ? (
        <ErrorState message={error} onRetry={loadPlans} />
      ) : !plans || plans.length === 0 ? (
        <EmptyState text="还没有学习计划，用上面的表单创建一个吧" emoji="📋" />
      ) : (
        plans.map((p) => {
          const pct = p.total_count ? Math.round((p.done_count / p.total_count) * 100) : 0
          const open = openId === p.id
          return (
            <section key={p.id} className="card plan-card">
              <div className="pc-head" onClick={() => openPlan(p.id)} role="button">
                <div className="pc-info">
                  <div className="pc-name">
                    {p.name}
                    <span className="pc-meta">
                      {p.days} 天 · 每天 {p.daily_count} 篇
                    </span>
                  </div>
                  <div className="pc-modules">
                    {(p.module_codes || []).map((c) => (
                      <span
                        key={c}
                        className="pc-dot"
                        style={{ background: moduleColorOf(c) }}
                      />
                    ))}
                    <span className="muted" style={{ fontSize: 12.5 }}>
                      {p.done_count}/{p.total_count} 篇 · {pct}%
                    </span>
                  </div>
                  <div className="pc-bar">
                    <span className="pc-bar-fill" style={{ width: `${pct}%` }} />
                  </div>
                </div>
                <span className="pc-arrow">{open ? '▾' : '▸'}</span>
              </div>

              {open && (
                <div className="pc-body">
                  {detailLoading || (detail && detail.id !== p.id) ? (
                    <Loader text="清单加载中…" />
                  ) : detail ? (
                    dayGroups.map((g) => {
                      const dayDone = g.items.filter((it) => it.completed).length
                      return (
                        <div key={g.day} className="pc-day">
                          <div className="pc-day-head">
                            <span className="pc-day-tag">第 {g.day} 天</span>
                            <span className="muted" style={{ fontSize: 12 }}>
                              {dayDone}/{g.items.length} 完成
                            </span>
                          </div>
                          {g.items.map((it) => (
                            <div key={it.id} className={`pc-item${it.completed ? ' done' : ''}`}>
                              <button
                                className={`pc-check${it.completed ? ' on' : ''}`}
                                disabled={busyItem === it.id}
                                onClick={() => toggleItem(it.id)}
                                title={it.completed ? '取消完成' : '标记完成'}
                              >
                                {it.completed ? '✓' : ''}
                              </button>
                              <span className="pc-accent" style={{ background: moduleColorOf(it.module_code, it.module_color) }} />
                              <Link to={`/article/${it.article_id}`} className="pc-item-title">
                                {it.title}
                              </Link>
                              <span className={difficultyBadgeClass(it.difficulty)}>
                                {difficultyText(it.difficulty)}
                              </span>
                            </div>
                          ))}
                        </div>
                      )
                    })
                  ) : null}
                  <div className="pc-foot">
                    <button className="btn btn-ghost btn-sm" onClick={() => removePlan(p.id)}>
                      🗑 删除计划
                    </button>
                  </div>
                </div>
              )}
            </section>
          )
        })
      )}
    </div>
  )
}
