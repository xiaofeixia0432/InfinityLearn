import { NavLink } from 'react-router-dom'
import Icon from './Icon.jsx'

const TABS = [
  { to: '/', label: '首页', icon: 'home' },
  { to: '/daily', label: '每日', icon: 'daily' },
  { to: '/plans', label: '计划', icon: 'plan' },
  { to: '/profile', label: '我的', icon: 'book' },
]

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      <div className="bottom-nav-inner">
        {TABS.map((t) => (
          <NavLink
            key={t.to}
            to={t.to}
            end={t.to === '/'}
            className={({ isActive }) => `tab-item${isActive ? ' active' : ''}`}
          >
            <span className="tab-ico">
              <Icon name={t.icon} size={19} />
            </span>
            <span>{t.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
