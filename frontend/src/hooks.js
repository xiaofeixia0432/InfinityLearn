import { useCallback, useEffect, useState } from 'react'
import { api } from './api.js'
import { FALLBACK_MODULES } from './utils.js'

/* 拉取模块列表；失败时使用默认配色兜底并保留 error 供页面提示 */
export function useModules() {
  const [modules, setModules] = useState(FALLBACK_MODULES)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.get('/api/modules')
      const items = data && Array.isArray(data.items) && data.items.length ? data.items : FALLBACK_MODULES
      setModules(items)
    } catch (e) {
      setError(e.message || '模块加载失败')
      setModules(FALLBACK_MODULES)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { modules, loading, error, reload: load }
}
