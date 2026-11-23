import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { marked } from 'marked'
import { api } from '../api.js'
import { useAuth } from '../AuthContext.jsx'
import Loader from '../components/Loader.jsx'
import ErrorState from '../components/ErrorState.jsx'
import {
  moduleVars,
  difficultyText,
  difficultyBadgeClass,
  fmtViews,
  shortDate,
} from '../utils.js'
import { cleanTextForSpeech, useSpeech } from '../hooks/useSpeech.js'

marked.setOptions({ gfm: true, breaks: true })

export default function Article() {
  const { id } = useParams()
  const { user } = useAuth()

  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [related, setRelated] = useState([])

  // 登录态相关：进度状态 / 收藏状态 / 操作提示
  const [progressStatus, setProgressStatus] = useState(null) // null | 'learning' | 'completed'
  const [fav, setFav] = useState(false)
  const [actionMsg, setActionMsg] = useState('')
  const [busy, setBusy] = useState(false)

  // 朗读：分句队列播放，支持暂停/停止/循环/倍速
  const sp = useSpeech()

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const d = await api.get(`/api/articles/${encodeURIComponent(id)}`)
      setArticle(d)
    } catch (e) {
      setError(e.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  // 同模块推荐：文章加载后拉取同模块最新文章（排除当前），填充右侧栏
  useEffect(() => {
    if (!article?.module_code) return
    let cancelled = false
    api
      .get(`/api/modules/${article.module_code}/articles?page=1&page_size=8`)
      .then((d) => {
        if (cancelled) return
        setRelated(
          (d.items || []).filter((a) => a.id !== Number(article.id)).slice(0, 6),
        )
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [article?.id, article?.module_code])

  // 切换文章时停止朗读
  useEffect(() => {
    sp.stop()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  function startSpeak() {
    if (!article) return
    sp.speak(
      cleanTextForSpeech(
        `${article.title}。${article.summary ? article.summary + '。' : ''}\n${article.content || ''}`,
      ),
    )
  }

  // 已登录：查询当前文章的进度与收藏状态
  useEffect(() => {
    if (!user || !article) return
    let cancelled = false
    const aid = Number(article.id)
    async function loadStatus() {
      try {
        const [p, f] = await Promise.all([api.authGet('/api/progress'), api.authGet('/api/favorites')])
        if (cancelled) return
        const pItem = (p.items || []).find((x) => Number(x.article_id) === aid)
        setProgressStatus(pItem ? pItem.status : null)
        setFav((f.items || []).some((x) => Number(x.article_id) === aid))
      } catch {
        /* 状态查询失败不影响阅读 */
      }
    }
    loadStatus()
    return () => {
      cancelled = true
    }
  }, [user, article])

  const { html, toc } = useMemo(() => {
    if (!article) return { html: '', toc: [] }
    // 渲染 Markdown 并给 h2/h3 注入顺序 id，同步生成目录
    let idx = 0
    const raw = marked.parse(article.content || '')
    const withIds = raw.replace(/<h([23])>/g, (m, lvl) => `<h${lvl} id="toc-${idx++}">`)
    const nodes = withIds.match(/<h([23]) id="toc-\d+">[\s\S]*?<\/h\1>/g) || []
    const items = nodes.map((s) => {
      const level = Number(s.charAt(2))
      const id = (s.match(/id="(toc-\d+)"/) || [])[1]
      const text = s
        .replace(/^<h[23] id="toc-\d+">/, '')
        .replace(/<\/h[23]>\s*$/, '')
        .replace(/<[^>]+>/g, '')
        .trim()
      return { id, level, text }
    })
    return { html: withIds, toc: items }
  }, [article])

  // 目录当前章节高亮：取视口顶部已越过的最后一个标题（上下滚动都精确），rAF 节流
  const [activeToc, setActiveToc] = useState('')
  const [tocOpen, setTocOpen] = useState(false)

  const jumpToc = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setTocOpen(false)
  }
  const activeTocText = toc.find((t) => t.id === activeToc)?.text || '点击章节直达'
  useEffect(() => {
    if (toc.length === 0) return
    const heads = Array.from(document.querySelectorAll('.article-body h2[id], .article-body h3[id]'))
    if (heads.length === 0) return
    let ticking = false
    const update = () => {
      ticking = false
      let current = ''
      for (const h of heads) {
        if (h.getBoundingClientRect().top <= 96) current = h.id
        else break
      }
      setActiveToc(current || heads[0].id)
    }
    const onScroll = () => {
      if (!ticking) {
        ticking = true
        requestAnimationFrame(update)
      }
    }
    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [html])

  // 目录很长时，让高亮项保持可见——手动改目录内部 scrollTop，绝不波及页面滚动
  useEffect(() => {
    if (!activeToc) return
    const list = document.querySelector('.toc-list')
    const item = list?.querySelector('.toc-item.active')
    if (!list || !item || list.scrollHeight <= list.clientHeight + 4) return
    const target = item.offsetTop - list.offsetTop - list.clientHeight / 2 + item.offsetHeight / 2
    list.scrollTo({ top: Math.max(0, target), behavior: 'smooth' })
  }, [activeToc])

  async function markProgress(status) {
    if (!article || busy) return
    setBusy(true)
    setActionMsg('')
    try {
      await api.authPost(`/api/progress/${article.id}`, { status })
      setProgressStatus(status)
      setActionMsg(status === 'completed' ? '🎉 已标记完成，继续加油！' : '📌 已加入学习中')
    } catch (e) {
      setActionMsg(e.message || '操作失败')
    } finally {
      setBusy(false)
    }
  }

  async function toggleFavorite() {
    if (!article || busy) return
    setBusy(true)
    setActionMsg('')
    try {
      const r = await api.authPost(`/api/favorites/${article.id}`)
      setFav(!!r.favorited)
      setActionMsg(r.favorited ? '⭐ 已加入收藏' : '已取消收藏')
    } catch (e) {
      setActionMsg(e.message || '操作失败')
    } finally {
      setBusy(false)
    }
  }

  if (loading) return <Loader text="文章加载中…" />
  if (error) return <ErrorState message={error} onRetry={load} />
  if (!article) return <ErrorState message="文章不存在" />

  const vars = moduleVars(article.module_code, article.module_color)
  const name = user ? user.nickname || user.username : ''

  return (
    <div className="article-layout">
      {/* 左侧栏：文章信息 + 标签 */}
      <aside className="article-aside left">
        <div className="aside-card">
          <div className="aside-title">📄 文章信息</div>
          <div className="info-rows">
            <div className="info-row">
              <span>所属模块</span>
              <Link to={`/module/${article.module_code}`} style={{ color: 'var(--mc, var(--brand))', fontWeight: 700 }}>
                {article.module_name}
              </Link>
            </div>
            <div className="info-row">
              <span>难度</span>
              <span className={difficultyBadgeClass(article.difficulty)}>{difficultyText(article.difficulty)}</span>
            </div>
            <div className="info-row">
              <span>预计时长</span>
              <b>{article.duration_minutes != null ? `约 ${article.duration_minutes} 分钟` : '—'}</b>
            </div>
            <div className="info-row">
              <span>阅读次数</span>
              <b>{fmtViews(article.views)}</b>
            </div>
            <div className="info-row">
              <span>发布日期</span>
              <b>{article.published_at ? shortDate(article.published_at) : '—'}</b>
            </div>
          </div>
        </div>
        {Array.isArray(article.tags) && article.tags.length > 0 && (
          <div className="aside-card">
            <div className="aside-title">🏷 标签</div>
            <div className="tag-row">
              {article.tags.map((t) => (
                <span className="tag" key={t}>
                  #{t}
                </span>
              ))}
            </div>
          </div>
        )}
        <div className="aside-card tip-card">
          <div className="aside-title">💡 小贴士</div>
          <p>点击「朗读本文」可以听文章，支持循环与倍速，适合跟读练习。</p>
        </div>
      </aside>

      {/* 中栏：标头 + 正文 + 翻页 */}
      <div className="article-center">
      {/* 模块色标头 */}
      <header className="article-head" style={vars}>
        <Link to={`/module/${article.module_code}`} className="article-crumb">
          <span>{article.icon || '📚'}</span>
          <span>{article.module_name}</span>
          <span>›</span>
        </Link>
        <h1>{article.title}</h1>
        {article.summary && <p className="ah-summary">{article.summary}</p>}
        <div className="article-head-meta">
          <span className={difficultyBadgeClass(article.difficulty)}>
            {difficultyText(article.difficulty)}
          </span>
          {article.duration_minutes != null && <span>⏱ 约 {article.duration_minutes} 分钟</span>}
          <span>👀 {fmtViews(article.views)} 次阅读</span>
          {article.published_at && <span>🗓 {shortDate(article.published_at)}</span>}
        </div>
        {/* 朗读控件 */}
        {sp.supported && (
          <div className="speak-bar">
            <button
              className={`spk-btn main${sp.speaking ? ' active' : ''}`}
              onClick={() => (sp.speaking ? (sp.paused ? sp.resume() : sp.pause()) : startSpeak())}
            >
              {sp.speaking ? (sp.paused ? '▶ 继续朗读' : '⏸ 暂停朗读') : '🔊 朗读本文'}
            </button>
            {sp.speaking && (
              <button className="spk-btn" onClick={sp.stop}>
                ⏹ 停止
              </button>
            )}
            <button
              className={`spk-btn${sp.loop ? ' on' : ''}`}
              onClick={() => sp.setLoop((v) => !v)}
              title="循环朗读"
            >
              🔁 {sp.loop ? '循环中' : '循环'}
            </button>
            <select
              className="spk-rate"
              value={sp.rate}
              onChange={(e) => sp.setRate(Number(e.target.value))}
              title="朗读速度"
            >
              <option value={0.8}>0.8 倍</option>
              <option value={1}>1 倍</option>
              <option value={1.25}>1.25 倍</option>
              <option value={1.5}>1.5 倍</option>
              <option value={2}>2 倍</option>
            </select>
            {sp.speaking && sp.progress.total > 0 && (
              <span className="spk-prog">
                第 {sp.progress.cur}/{sp.progress.total} 句
              </span>
            )}
          </div>
        )}

        {/* 已登录：标记完成 / 继续学习 / 收藏 */}
        {user && (
          <div className="article-actions">
            {progressStatus === 'completed' ? (
              <>
                <span className="status-pill status-completed">✓ 已完成</span>
                <button
                  className="btn btn-ghost btn-sm"
                  disabled={busy}
                  onClick={() => markProgress('learning')}
                >
                  重新学习
                </button>
              </>
            ) : progressStatus === 'learning' ? (
              <>
                <span className="status-pill status-learning">📖 学习中</span>
                <button
                  className="btn btn-primary btn-sm"
                  disabled={busy}
                  onClick={() => markProgress('completed')}
                >
                  标记完成
                </button>
              </>
            ) : (
              <button
                className="btn btn-primary btn-sm"
                disabled={busy}
                onClick={() => markProgress('learning')}
              >
                ▶ 开始学习
              </button>
            )}
            <button
              className={`btn btn-sm ${fav ? 'btn-ghost' : 'btn-ghost'}`}
              disabled={busy}
              onClick={toggleFavorite}
            >
              {fav ? '★ 已收藏' : '☆ 收藏'}
            </button>
            {name && progressStatus === null && !fav && (
              <span className="muted" style={{ fontSize: 12.5, alignSelf: 'center' }}>
                Hi {name}，记下你的学习足迹吧
              </span>
            )}
          </div>
        )}
        {user && actionMsg && (
          <p className="muted" style={{ fontSize: 13, margin: '10px 0 0' }}>
            {actionMsg}
          </p>
        )}
      </header>

      {/* 窄屏折叠式目录条：吸顶，点开即选章 */}
      {toc.length >= 2 && (
        <div className="m-toc-wrap">
          <button className="m-toc-bar" onClick={() => setTocOpen((o) => !o)}>
            <span className="m-toc-ico">📑</span>
            <span className="m-toc-label">目录</span>
            <span className="m-toc-cur">{activeTocText}</span>
            <span className={`m-toc-arrow${tocOpen ? ' open' : ''}`}>▾</span>
          </button>
          <div className={`m-toc-panel${tocOpen ? ' open' : ''}`}>
            <ul className="toc-list">
              {toc.map((t) => (
                <li key={t.id}>
                  <button
                    className={`toc-item l${t.level}${activeToc === t.id ? ' active' : ''}`}
                    onClick={() => jumpToc(t.id)}
                  >
                    {t.text}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <article className="article-body" dangerouslySetInnerHTML={{ __html: html }} />

      {/* 上一篇 / 下一篇 */}
      <nav className="article-nav">
        {article.prev_id ? (
          <Link to={`/article/${article.prev_id}`}>
            <span className="an-label">← 上一篇</span>
            <span className="an-title">上一篇</span>
          </Link>
        ) : (
          <a style={{ opacity: 0.5, pointerEvents: 'none' }}>
            <span className="an-label">← 上一篇</span>
            <span className="an-title">已经是第一篇了</span>
          </a>
        )}
        {article.next_id ? (
          <Link to={`/article/${article.next_id}`} className="an-next">
            <span className="an-label">下一篇 →</span>
            <span className="an-title">下一篇</span>
          </Link>
        ) : (
          <a className="an-next" style={{ opacity: 0.5, pointerEvents: 'none' }}>
            <span className="an-label">下一篇 →</span>
            <span className="an-title">已经是最后一篇了</span>
          </a>
        )}
      </nav>
      </div>

      {/* 右侧栏：目录 + 同模块推荐 */}
      <aside className="article-aside right">
        {toc.length >= 2 && (
          <div className="aside-card toc-card">
            <div className="aside-title">📑 文章目录</div>
            <ul className="toc-list">
              {toc.map((t) => (
                <li key={t.id}>
                  <button
                    className={`toc-item l${t.level}${activeToc === t.id ? ' active' : ''}`}
                    onClick={() => jumpToc(t.id)}
                  >
                    {t.text}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="aside-card">
          <div className="aside-title">🔥 同模块推荐</div>
          {related.length === 0 ? (
            <p className="aside-empty">暂无其他文章</p>
          ) : (
            <ul className="rel-list">
              {related.map((a) => (
                <li key={a.id}>
                  <Link to={`/article/${a.id}`} className="rel-item">
                    <span className="rel-title">{a.title}</span>
                    <span className="rel-meta">
                      <span className={difficultyBadgeClass(a.difficulty)}>{difficultyText(a.difficulty)}</span>
                      {a.duration_minutes != null && <span>⏱ {a.duration_minutes} 分</span>}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
        <Link to={`/module/${article.module_code}`} className="aside-card back-module" style={vars}>
          <span className="bm-ico">📚</span>
          <span>
            进入「{article.module_name}」
            <i>查看模块全部文章 →</i>
          </span>
        </Link>
      </aside>
    </div>
  )
}
