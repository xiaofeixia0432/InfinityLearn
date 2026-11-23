import { useCallback, useEffect, useRef, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../AuthContext.jsx'
import Loader from '../components/Loader.jsx'

const TABLE_LABELS = {
  users: '用户',
  modules: '模块',
  articles: '文章',
  daily_plans: '每日推荐',
  user_progress: '学习进度',
  favorites: '收藏',
  study_plans: '学习计划',
  study_plan_items: '计划条目',
  custom_quotes: '自定义名言',
}

export default function Admin() {
  const { user, ready } = useAuth()
  const [info, setInfo] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState('')
  const fileRef = useRef(null)

  const load = useCallback(async () => {
    setError('')
    try {
      setInfo(await api.authGet('/api/admin/backup/info'))
    } catch (e) {
      setError(e.message || '读取失败')
    }
  }, [])

  useEffect(() => {
    if (user?.is_admin) load()
  }, [user, load])

  if (!ready) return <Loader text="身份校验中…" />
  if (!user) return <Navigate to="/login?next=/admin" replace />
  if (!user.is_admin) return <Navigate to="/" replace />

  async function handleExport() {
    setBusy('export')
    setMessage('')
    setError('')
    try {
      const { blob, filename } = await api.authDownload('/api/admin/backup/export')
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
      setMessage(`已导出 ${filename}（${(blob.size / 1024 / 1024).toFixed(1)} MB）`)
    } catch (e) {
      setError(e.message || '导出失败')
    } finally {
      setBusy('')
    }
  }

  async function handleImport(event) {
    const file = event.target.files && event.target.files[0]
    if (!file) return
    if (!window.confirm('导入会用备份数据覆盖当前全部数据，且不可撤销。确定继续吗？')) {
      if (fileRef.current) fileRef.current.value = ''
      return
    }
    setBusy('import')
    setMessage('')
    setError('')
    try {
      const res = await api.authUpload('/api/admin/backup/import', file)
      const summary = Object.entries(res.tables || {})
        .map(([key, value]) => `${TABLE_LABELS[key] || key} ${value}`)
        .join('，')
      setMessage(`还原完成：${summary || '无数据'}`)
      load()
    } catch (e) {
      setError(e.message || '还原失败')
    } finally {
      setBusy('')
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  return (
    <div>
      <div className="panel">
        <h2 className="panel-title">🛠 数据迁移与还原</h2>
        <p className="muted" style={{ fontSize: 13.5, marginTop: -4 }}>
          导出的迁移包包含代码、配置与数据库全部数据，可直接拷到另一台机器还原部署。
        </p>
      </div>

      <div className="panel">
        <h2 className="panel-title">📊 当前数据规模</h2>
        {error && <p style={{ color: 'var(--danger, #e5484d)', fontSize: 13.5 }}>{error}</p>}
        {info === null ? (
          <Loader text="加载中…" />
        ) : (
          <>
            <p className="muted" style={{ fontSize: 13.5 }}>
              数据库：{info.database} · 共 {info.total_rows} 行
            </p>
            <div className="profile-stats" style={{ flexWrap: 'wrap' }}>
              {Object.entries(info.tables || {}).map(([key, value]) => (
                <div className="profile-stat" key={key}>
                  <div className="ps-num">{value}</div>
                  <div className="ps-label">{TABLE_LABELS[key] || key}</div>
                </div>
              ))}
            </div>
            <button className="btn btn-primary" onClick={load} disabled={!!busy}>
              刷新
            </button>
          </>
        )}
      </div>

      <div className="panel">
        <h2 className="panel-title">⬇️ 导出迁移包</h2>
        <p className="muted" style={{ fontSize: 13.5 }}>
          生成一个 zip，内含 backend / frontend 代码、.env 配置和数据库数据。
          解压后运行 restore.sh（macOS）或 restore.bat（Windows）即可在新机器还原。
        </p>
        <button className="btn btn-primary" onClick={handleExport} disabled={!!busy}>
          {busy === 'export' ? '正在打包…' : '下载迁移包'}
        </button>
      </div>

      <div className="panel">
        <h2 className="panel-title">⬆️ 从备份还原</h2>
        <p className="muted" style={{ fontSize: 13.5 }}>
          支持 .zip 迁移包或 .json 数据文件。还原会<strong>清空并覆盖</strong>当前全部数据，请先导出备份。
          单个文件上限 100MB；更大的数据请用命令行 <code>deploy/migrate.py</code> 还原。
        </p>
        <input
          ref={fileRef}
          type="file"
          accept=".zip,.json"
          onChange={handleImport}
          disabled={!!busy}
        />
        {busy === 'import' && <p className="muted" style={{ fontSize: 13.5 }}>正在还原，请勿关闭页面…</p>}
      </div>

      {message && (
        <div className="panel" style={{ borderColor: 'var(--brand)' }}>
          <p style={{ margin: 0, fontSize: 13.5 }}>✅ {message}</p>
        </div>
      )}
    </div>
  )
}
