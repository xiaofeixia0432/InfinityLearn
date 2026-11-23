const TOKEN_KEY = 'il_token'
const USER_KEY = 'il_user'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function setStoredUser(user) {
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
  else localStorage.removeItem(USER_KEY)
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

function handle401() {
  setToken('')
  setStoredUser(null)
  if (!window.location.pathname.startsWith('/login')) {
    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`
  }
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  let res
  try {
    res = await fetch(path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError('网络请求失败，请检查网络连接', 0)
  }

  if (res.status === 401 && auth) {
    // 登录态失效：清理本地凭据并跳转登录页
    handle401()
    throw new ApiError('登录已过期，请重新登录', 401)
  }

  let data = null
  try {
    data = await res.json()
  } catch {
    data = null
  }

  if (!res.ok) {
    const detail =
      (data && (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))) ||
      `请求失败（${res.status}）`
    throw new ApiError(detail, res.status)
  }

  return data
}

/** 带登录态下载文件，返回 { blob, filename } */
async function download(path) {
  let res
  try {
    res = await fetch(path, { headers: authHeaders() })
  } catch {
    throw new ApiError('网络请求失败，请检查网络连接', 0)
  }
  if (res.status === 401) {
    handle401()
    throw new ApiError('登录已过期，请重新登录', 401)
  }
  if (!res.ok) {
    let data = null
    try {
      data = await res.json()
    } catch {
      data = null
    }
    const detail =
      (data && (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))) ||
      `下载失败（${res.status}）`
    throw new ApiError(detail, res.status)
  }
  const blob = await res.blob()
  const disposition = res.headers.get('Content-Disposition') || ''
  const match = /filename="?([^";]+)"?/.exec(disposition)
  return { blob, filename: match ? match[1] : 'backup.zip' }
}

/** 带登录态上传文件（multipart） */
async function upload(path, file) {
  const form = new FormData()
  form.append('file', file)
  let res
  try {
    res = await fetch(path, { method: 'POST', headers: authHeaders(), body: form })
  } catch {
    throw new ApiError('网络请求失败，请检查网络连接', 0)
  }
  if (res.status === 401) {
    handle401()
    throw new ApiError('登录已过期，请重新登录', 401)
  }
  let data = null
  try {
    data = await res.json()
  } catch {
    data = null
  }
  if (!res.ok) {
    const detail =
      (data && (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))) ||
      `上传失败（${res.status}）`
    throw new ApiError(detail, res.status)
  }
  return data
}

export const api = {
  get: (path) => request(path),
  post: (path, body, opts = {}) => request(path, { method: 'POST', body, ...opts }),
  authPost: (path, body) => request(path, { method: 'POST', body, auth: true }),
  authGet: (path) => request(path, { auth: true }),
  authDelete: (path) => request(path, { method: 'DELETE', auth: true }),
  authDownload: (path) => download(path),
  authUpload: (path, file) => upload(path, file),
}
