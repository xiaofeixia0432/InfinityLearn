import { useCallback, useEffect, useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../AuthContext.jsx'
import { useModules } from '../hooks.js'
import ModuleCard from '../components/ModuleCard.jsx'
import ArticleCard from '../components/ArticleCard.jsx'
import Loader from '../components/Loader.jsx'
import EmptyState from '../components/EmptyState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import Icon from '../components/Icon.jsx'
import { greeting, fullDate, todayStr } from '../utils.js'

const STAT_STYLES = [
  { ico: 'book', bg: 'rgba(79, 142, 247, 0.14)' },
  { ico: 'home', bg: 'rgba(52, 211, 153, 0.14)' },
  { ico: 'daily', bg: 'rgba(251, 146, 60, 0.14)' },
  { ico: 'user', bg: 'rgba(167, 139, 250, 0.14)' },
]

export default function Home() {
  const { user } = useAuth()
  const { modules, loading, error, reload } = useModules()
  const [stats, setStats] = useState(null)
  const [dailyItems, setDailyItems] = useState(null)
  const [statsErr, setStatsErr] = useState('')

  const loadStats = useCallback(async () => {
    setStatsErr('')
    try {
      const d = await api.get('/api/stats/overview')
      setStats(d)
    } catch (e) {
      setStatsErr(e.message || '统计加载失败')
    }
  }, [])

  const loadDaily = useCallback(async () => {
    try {
      const d = await api.get(`/api/daily?date=${todayStr()}`)
      setDailyItems(Array.isArray(d.items) ? d.items : [])
    } catch {
      setDailyItems([])
    }
  }, [])

  useEffect(() => {
    loadStats()
    loadDaily()
  }, [loadStats, loadDaily])

  const name = user ? user.nickname || user.username : ''

  return (
    <div>
      {/* Hero 渐变区 */}
      <section className="hero">
        <div className="hero-greet">
          ✦ {greeting()}
          {name ? `，${name}` : ''}
        </div>
        <h1 className="hero-title">每天进步一点点，无限知识等你学</h1>
        <p className="hero-sub">
          {fullDate()} · 英语 / 嵌入式 / 电商 / 科学 / 金融 / Python / AI / Agent，多模块每日更新，陪你把学习变成习惯。
        </p>
        <span className="hero-emoji">🌱</span>
      </section>

      {/* 统计条 */}
      {statsErr ? (
        <ErrorState message={statsErr} onRetry={loadStats} />
      ) : (
        <div className="stats-bar">
          <StatCell
            ico={STAT_STYLES[0].ico}
            bg={STAT_STYLES[0].bg}
            num={stats ? stats.total_articles : '—'}
            label="总文章数"
          />
          <StatCell
            ico={STAT_STYLES[1].ico}
            bg={STAT_STYLES[1].bg}
            num={stats ? stats.total_modules : '—'}
            label="学习模块"
          />
          <StatCell
            ico={STAT_STYLES[2].ico}
            bg={STAT_STYLES[2].bg}
            num={stats ? stats.today_articles : '—'}
            label="今日更新"
          />
          <StatCell
            ico={STAT_STYLES[3].ico}
            bg={STAT_STYLES[3].bg}
            num={stats ? stats.total_users : '—'}
            label="学习人数"
          />
        </div>
      )}

      {/* 模块卡片网格 */}
      <div className="section-head">
        <h2 className="section-title">学习模块</h2>
      </div>
      {loading ? (
        <Loader />
      ) : error ? (
        <ErrorState message={error} onRetry={reload} />
      ) : (
        <div className="module-grid">
          {modules
            .filter((m) => !m.parent_code)
            .map((m) => (
              <ModuleCard
                key={m.code}
                module={m}
                subModules={modules.filter((x) => x.parent_code === m.code)}
              />
            ))}
        </div>
      )}

      {/* 今日推荐横滑 */}
      <div className="section-head">
        <h2 className="section-title">今日推荐</h2>
      </div>
      {dailyItems === null ? (
        <Loader />
      ) : dailyItems.length === 0 ? (
        <EmptyState text="今天还没有推荐内容，去看看往期吧" emoji="🌤" />
      ) : (
        <div className="hscroll">
          {dailyItems.map((it) => (
            <ArticleCard key={`${it.module_code}-${it.article_id}`} article={it} />
          ))}
        </div>
      )}
    </div>
  )
}

function StatCell({ ico, bg, num, label }) {
  return (
    <div className="stat-cell">
      <span className="stat-ico" style={{ background: bg, color: 'var(--text-dim)' }}>
        <Icon name={ico} size={20} />
      </span>
      <div>
        <div className="stat-num">{num}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  )
}
