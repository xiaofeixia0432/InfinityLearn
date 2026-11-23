import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [nickname, setNickname] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    if (!username.trim() || !password) {
      setErr('请输入用户名和密码')
      return
    }
    if (password.length < 6) {
      setErr('密码至少 6 位')
      return
    }
    if (password !== confirm) {
      setErr('两次输入的密码不一致')
      return
    }
    setBusy(true)
    setErr('')
    try {
      await register(username.trim(), password, nickname.trim())
      navigate('/', { replace: true })
    } catch (e2) {
      setErr(e2.message || '注册失败')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <div className="auth-logo">
          <span className="al-mark">∞</span>
          <h1>加入无限学堂</h1>
          <p>每天进步一点点，无限知识等你学</p>
        </div>

        {err && <div className="form-error">{err}</div>}

        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="reg-username">用户名</label>
            <input
              id="reg-username"
              type="text"
              autoComplete="username"
              placeholder="用于登录，建议字母或数字"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="reg-nickname">昵称（选填）</label>
            <input
              id="reg-nickname"
              type="text"
              placeholder="展示名称，留空则使用用户名"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="reg-password">密码</label>
            <input
              id="reg-password"
              type="password"
              autoComplete="new-password"
              placeholder="至少 6 位"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="reg-confirm">确认密码</label>
            <input
              id="reg-confirm"
              type="password"
              autoComplete="new-password"
              placeholder="再输入一次密码"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
            />
          </div>
          <button className="btn btn-primary btn-block" type="submit" disabled={busy}>
            {busy ? '注册中…' : '注册并登录'}
          </button>
        </form>

        <p className="auth-switch">
          已有账号？<Link to="/login">直接登录</Link>
        </p>
      </div>
    </div>
  )
}
