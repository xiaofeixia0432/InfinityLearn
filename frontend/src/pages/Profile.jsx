import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../AuthContext.jsx'
import Loader from '../components/Loader.jsx'
import EmptyState from '../components/EmptyState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import { moduleVars, shortDate } from '../utils.js'

export default function Profile() {
  const { user, ready, logout } = useAuth()
  const navigate = useNavigate()

  const [progress, setProgress] = useState(null)
  const [favorites, setFavorites] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setError('')
    try {
      const [p, f] = await Promise.all([api.authGet('/api/progress'), api.authGet('/api/favorites')])
      setProgress(Array.isArray(p.items) ? p.items : [])
      setFavorites(Array.isArray(f.items) ? f.items : [])
    } catch (e) {
      setError(e.message || '加载失败')
    }
  }, [])

  useEffect(() => {
    if (user) load()
  }, [user, load])

  const learning = useMemo(
    () => (progress || []).filter((x) => x.status === 'learning'),
    [progress],
  )
  const completed = useMemo(
    () => (progress || []).filter((x) => x.status === 'completed'),
    [progress],
  )

  if (!ready) return <Loader text="身份校验中…" />
  if (!user) return <Navigate to="/login?next=/profile" replace />

  const name = user.nickname || user.username || '学员'
  const initial = name.trim().charAt(0).toUpperCase() || '学'

  return (
    <div>
      <div className="profile-grid">
        {/* 左列：用户信息 */}
        <div>
          <div className="panel">
            <div className="profile-user">
              <span className="avatar">{initial}</span>
              <div>
                <div className="pu-name">{name}</div>
                <div className="pu-sub">@{user.username}</div>
              </div>
            </div>

            <div className="profile-stats">
              <div className="profile-stat">
                <div className="ps-num">{learning.length}</div>
                <div className="ps-label">进行中</div>
              </div>
              <div className="profile-stat">
                <div className="ps-num">{completed.length}</div>
                <div className="ps-label">已完成</div>
              </div>
              <div className="profile-stat">
                <div className="ps-num">{favorites ? favorites.length : '—'}</div>
                <div className="ps-label">收藏</div>
              </div>
            </div>

            {user.is_admin && (
              <Link to="/admin" className="btn btn-block" style={{ marginBottom: 10 }}>
                🛠 数据迁移与还原
              </Link>
            )}

            <button
              className="btn btn-danger-ghost btn-block"
              onClick={() => {
                logout()
                navigate('/')
              }}
            >
              退出登录
            </button>
          </div>
        </div>

        {/* 右列：学习进度 + 收藏 */}
        <div>
          {error ? (
            <div className="panel">
              <ErrorState message={error} onRetry={load} />
            </div>
          ) : progress === null ? (
            <Loader text="学习数据加载中…" />
          ) : (
            <>
              <div className="panel">
                <h2 className="panel-title">📖 学习进度</h2>

                <h3
                  className="section-title"
                  style={{ fontSize: 14.5, margin: '4px 0 10px', color: 'var(--text-dim)' }}
                >
                  进行中 · {learning.length}
                </h3>
                {learning.length === 0 ? (
                  <p className="muted" style={{ fontSize: 13.5, margin: '0 0 18px' }}>
                    还没有进行中的文章，去
                    <Link to="/daily" style={{ color: 'var(--brand)' }}>
                      每日学习
                    </Link>
                    挑一篇开始吧
                  </p>
                ) : (
                  learning.map((it) => (
                    <ProgressRow key={it.article_id} item={it} pill="learning" />
                  ))
                )}

                <h3
                  className="section-title"
                  style={{ fontSize: 14.5, margin: '18px 0 10px', color: 'var(--text-dim)' }}
                >
                  已完成 · {completed.length}
                </h3>
                {completed.length === 0 ? (
                  <p className="muted" style={{ fontSize: 13.5, margin: 0 }}>
                    完成的文章会出现在这里，坚持就是胜利 💪
                  </p>
                ) : (
                  completed.map((it) => (
                    <ProgressRow key={it.article_id} item={it} pill="completed" />
                  ))
                )}
              </div>

              <div className="panel">
                <h2 className="panel-title">⭐ 我的收藏</h2>
                {favorites === null ? (
                  <Loader />
                ) : favorites.length === 0 ? (
                  <EmptyState text="还没有收藏文章，阅读时点击“收藏”即可保存" emoji="⭐" />
                ) : (
                  favorites.map((it) => <ProgressRow key={it.article_id} item={it} meta={shortDate(it.created_at)} />)
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function ProgressRow({ item, pill, meta }) {
  return (
    <div className="list-row" style={moduleVars(item.module_code, item.module_color)}>
      <span className="lr-accent" />
      <div className="lr-body">
        <Link to={`/article/${item.article_id}`} className="lr-title">
          {item.title}
        </Link>
        <span className="lr-meta">
          {item.module_name || item.module_code}
          {meta ? ` · ${meta}` : item.updated_at ? ` · ${shortDate(item.updated_at)}` : ''}
        </span>
      </div>
      {pill === 'learning' && <span className="status-pill status-learning">学习中</span>}
      {pill === 'completed' && <span className="status-pill status-completed">已完成</span>}
    </div>
  )
}
