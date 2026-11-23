import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api.js'
import { useModules } from '../hooks.js'
import ArticleCard from '../components/ArticleCard.jsx'
import ModuleCard from '../components/ModuleCard.jsx'
import Loader from '../components/Loader.jsx'
import EmptyState from '../components/EmptyState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import { moduleVars } from '../utils.js'

const PAGE_SIZE = 20

export default function Module() {
  const { code } = useParams()
  const { modules } = useModules()

  const [searchParams, setSearchParams] = useSearchParams()
  const page = Math.max(1, parseInt(searchParams.get('page') || '1', 10) || 1)
  const difficulty = searchParams.get('difficulty') || ''
  const search = searchParams.get('search') || ''

  const [inputVal, setInputVal] = useState(search)
  const debounceRef = useRef(null)

  // 输入防抖同步到 URL（重置页码）
  function onSearchChange(e) {
    const v = e.target.value
    setInputVal(v)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      const next = new URLSearchParams(searchParams)
      if (v) next.set('search', v)
      else next.delete('search')
      next.delete('page')
      setSearchParams(next)
    }, 400)
  }

  function onDifficultyChange(e) {
    const next = new URLSearchParams(searchParams)
    const v = e.target.value
    if (v) next.set('difficulty', v)
    else next.delete('difficulty')
    next.delete('page')
    setSearchParams(next)
  }

  function goPage(p) {
    const next = new URLSearchParams(searchParams)
    if (p > 1) next.set('page', String(p))
    else next.delete('page')
    setSearchParams(next)
  }

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const qs = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) })
      if (difficulty) qs.set('difficulty', difficulty)
      if (search) qs.set('search', search)
      const d = await api.get(`/api/modules/${encodeURIComponent(code)}/articles?${qs.toString()}`)
      setData(d)
    } catch (e) {
      setError(e.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }, [code, page, difficulty, search])

  useEffect(() => {
    load()
  }, [load])

  // code 切换时重置搜索框
  useEffect(() => {
    setInputVal(searchParams.get('search') || '')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code])

  const info = useMemo(() => modules.find((m) => m.code === code), [modules, code])
  // 子模块（如 Python 编程 → 爬虫 / FastAPI）：父模块页只展示子模块入口
  const subModules = useMemo(
    () => modules.filter((m) => m.parent_code === code),
    [modules, code],
  )
  const subArticleTotal = useMemo(
    () => subModules.reduce((sum, m) => sum + (Number(m.article_count) || 0), 0),
    [subModules],
  )
  const total = data ? Number(data.total) || 0 : 0
  const totalPages = Math.max(1, Math.ceil(total / (data ? Number(data.page_size) || PAGE_SIZE : PAGE_SIZE)))

  // 课程型模块（全部标题形如「第 N 课」）按课号升序展示，其余保持接口顺序
  const items = useMemo(() => {
    if (!data || !data.items) return []
    const list = data.items.map((a, i) => {
      const m = /第\s*(\d+)\s*课/.exec(a.title || '')
      return { a, i, n: m ? Number(m[1]) : null }
    })
    if (list.every((x) => x.n != null)) list.sort((x, y) => x.n - y.n || x.i - y.i)
    return list.map((x) => x.a)
  }, [data])

  return (
    <div>
      {/* 模块头（读取模块专属颜色） */}
      <section className="module-hero" style={moduleVars(code, info && info.color)}>
        <div className="module-ico">{(info && info.icon) || '📚'}</div>
        <div>
          <h1>{(info && info.name) || code}</h1>
          <p>
            {(info && info.description) || '本模块文章列表'}
            {subModules.length > 0
              ? ` · ${subModules.length} 个子模块 · 共 ${subArticleTotal} 篇`
              : info && info.article_count != null
                ? ` · 共 ${info.article_count} 篇`
                : ''}
          </p>
        </div>
      </section>

      {subModules.length > 0 ? (
        <>
          <div className="section-head">
            <h2 className="section-title">选择学习方向</h2>
          </div>
          <div className="module-grid">
            {subModules.map((m) => (
              <ModuleCard key={m.code} module={m} />
            ))}
          </div>
        </>
      ) : (
        <>
          {/* 搜索 + 难度筛选 */}
          <div className="filter-bar">
            <div className="search-input">
              <span className="si-ico">🔍</span>
              <input
                type="search"
                placeholder="搜索文章标题 / 摘要…"
                value={inputVal}
                onChange={onSearchChange}
              />
            </div>
            <select className="diff-select" value={difficulty} onChange={onDifficultyChange}>
              <option value="">全部难度</option>
              <option value="1">入门</option>
              <option value="2">进阶</option>
              <option value="3">高级</option>
            </select>
          </div>

          {loading ? (
            <Loader />
          ) : error ? (
            <ErrorState message={error} onRetry={load} />
          ) : !data || !data.items || data.items.length === 0 ? (
            <EmptyState text="没有找到符合条件的文章，换个关键词试试" emoji="🔎" />
          ) : (
            <>
              <div className="article-grid">
                {items.map((a) => (
                  <ArticleCard key={a.id} article={{ ...a, module_code: code }} />
                ))}
              </div>

              {/* 分页 */}
              {totalPages > 1 && (
                <div className="pager">
                  <button
                    className="btn btn-ghost btn-sm"
                    disabled={page <= 1}
                    onClick={() => goPage(page - 1)}
                  >
                    ← 上一页
                  </button>
                  <span className="pager-info">
                    第 {data.page ?? page} / {totalPages} 页 · 共 {total} 篇
                  </span>
                  <button
                    className="btn btn-ghost btn-sm"
                    disabled={page >= totalPages}
                    onClick={() => goPage(page + 1)}
                  >
                    下一页 →
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}
