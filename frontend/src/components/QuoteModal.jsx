import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../AuthContext.jsx'

/* 名言管理弹窗：添加自定义名言 + 管理我的名言 */
export default function QuoteModal({ onClose }) {
  const { user } = useAuth()
  const [text, setText] = useState('')
  const [author, setAuthor] = useState('')
  const [mine, setMine] = useState([])
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    function onKey(e) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  useEffect(() => {
    if (!user) return
    api
      .get('/api/quotes')
      .then((data) => setMine((data.items || []).filter((q) => q.mine)))
      .catch(() => {})
  }, [user])

  async function submit(e) {
    e.preventDefault()
    if (!text.trim() || busy) return
    setBusy(true)
    setMsg('')
    try {
      await api.authPost('/api/quotes', { text: text.trim(), author: author.trim() || '佚名' })
      setText('')
      setAuthor('')
      setMsg('已添加，马上就能在轮播里看到它了')
      const data = await api.get('/api/quotes')
      setMine((data.items || []).filter((q) => q.mine))
    } catch (err) {
      setMsg(err.message || '添加失败')
    } finally {
      setBusy(false)
    }
  }

  async function remove(id) {
    if (busy) return
    setBusy(true)
    setMsg('')
    try {
      await api.authDelete(`/api/quotes/${id}`)
      setMine((list) => list.filter((q) => q.id !== id))
    } catch (err) {
      setMsg(err.message || '删除失败')
    } finally {
      setBusy(false)
    }
  }

  // Portal 到 body：顶栏的 backdrop-filter 会劫持 fixed 定位，导致弹窗被裁
  return createPortal(
    <div className="qm-mask" onClick={onClose}>
      <div className="qm-box" onClick={(e) => e.stopPropagation()}>
        <div className="qm-head">
          <span className="qm-title">✍ 我的名言</span>
          <button className="qm-close" onClick={onClose} aria-label="关闭">
            ✕
          </button>
        </div>

        {!user ? (
          <div className="qm-login">
            <p>登录后即可添加自己的名言，并展示在顶部轮播里。</p>
            <Link to="/login" className="side-btn primary" onClick={onClose}>
              去登录
            </Link>
          </div>
        ) : (
          <>
            <form className="qm-form" onSubmit={submit}>
              <textarea
                className="qm-text"
                rows={2}
                maxLength={120}
                placeholder="写下你的金融名言（必填，120 字以内）"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
              <div className="qm-row">
                <input
                  className="qm-input"
                  maxLength={40}
                  placeholder="作者（选填，默认佚名）"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                />
                <button className="qm-submit" disabled={busy || !text.trim()}>
                  添加
                </button>
              </div>
            </form>
            {msg && <div className="qm-msg">{msg}</div>}

            <div className="qm-list-wrap">
              <div className="qm-sub">我添加的（{mine.length}）</div>
              {mine.length === 0 ? (
                <div className="qm-empty">还没有添加过名言，来写下第一条吧。</div>
              ) : (
                <ul className="qm-list">
                  {mine.map((q) => (
                    <li key={q.id} className="qm-item">
                      <span className="qm-item-text">
                        {q.text}
                        <i>—— {q.author}</i>
                      </span>
                      <button className="qm-del" onClick={() => remove(q.id)} disabled={busy}>
                        删除
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </>
        )}
      </div>
    </div>,
    document.body,
  )
}
