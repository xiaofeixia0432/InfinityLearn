import { Fragment, useEffect, useRef, useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext.jsx'
import { useModules } from '../hooks.js'
import Icon from './Icon.jsx'

const MODULE_ICON = {
  english: 'english',
  embedded: 'embedded',
  ecommerce: 'ecommerce',
  science: 'science',
  finance: 'finance',
  python: 'python',
  python_crawler: 'crawler',
  python_fastapi: 'fastapi',
  ai: 'ai',
  agent: 'agent',
}

/* 左侧多彩导航栏（PC 端） */
export default function Sidebar() {
  const { user, logout } = useAuth()
  const { modules } = useModules()

  return (
    <aside className="sidebar">
      <Link to="/" className="side-logo">
        <span className="side-logo-mark">∞</span>
        <span className="side-logo-text">
          无限学堂
          <i>InfinityLearn</i>
        </span>
      </Link>

      <nav className="side-nav">
        <SideLink to="/" end icon="home" label="首页" tone="#3fbf8f" />
        <SideLink to="/daily" icon="daily" label="每日学习" tone="#4f8ef7" />
        <SideLink to="/plans" icon="plan" label="学习计划" tone="#f472b6" />
        <div className="side-sep">知识模块</div>
        {modules
          .filter((m) => !m.parent_code)
          .map((m) => {
            const kids = modules.filter((x) => x.parent_code === m.code)
            if (kids.length === 0) {
              return (
                <SideLink
                  key={m.code}
                  to={`/module/${m.code}`}
                  icon={MODULE_ICON[m.code] || 'book'}
                  label={m.name}
                  tone={m.color || '#3fbf8f'}
                />
              )
            }
            return (
              <Fragment key={m.code}>
                <SideLink
                  to={`/module/${m.code}`}
                  icon={MODULE_ICON[m.code] || 'book'}
                  label={m.name}
                  tone={m.color || '#3fbf8f'}
                />
                {kids.map((c) => (
                  <SideLink
                    key={c.code}
                    to={`/module/${c.code}`}
                    icon={MODULE_ICON[c.code] || 'book'}
                    label={c.name}
                    tone={c.color || '#3fbf8f'}
                    sub
                  />
                ))}
              </Fragment>
            )
          })}
      </nav>

      <div className="side-foot">
        {user && <UserMenu user={user} onLogout={logout} />}
      </div>
    </aside>
  )
}

function SideLink({ to, end, icon, label, tone, sub }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => `side-link${isActive ? ' active' : ''}${sub ? ' is-sub' : ''}`}
      style={{ '--tone': tone }}
    >
      <span className="sl-ico">
        <Icon name={icon} size={sub ? 15 : 17} />
      </span>
      <span className="sl-label">{label}</span>
    </NavLink>
  )
}

function UserMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false)
  const boxRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    function onDoc(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const name = user.nickname || user.username || '学员'
  const initial = name.trim().charAt(0).toUpperCase() || '学'

  return (
    <div className="side-user" ref={boxRef}>
      <button className="avatar-btn" onClick={() => setOpen((v) => !v)}>
        <span className="avatar">{initial}</span>
        <span>{name}</span>
        <span style={{ fontSize: 10, color: 'var(--text-faint)' }}>▾</span>
      </button>
      {open && (
        <div className="dropdown side-drop">
          <div className="dropdown-meta">
            <div className="dm-name">{name}</div>
            <div className="dm-id">@{user.username}</div>
          </div>
          <button
            className="dropdown-item"
            onClick={() => {
              setOpen(false)
              navigate('/profile')
            }}
          >
            <Icon name="book" size={15} /> 我的学习
          </button>
          <button
            className="dropdown-item"
            onClick={() => {
              setOpen(false)
              onLogout()
              navigate('/')
            }}
          >
            <Icon name="logout" size={15} /> 退出登录
          </button>
        </div>
      )}
    </div>
  )
}
