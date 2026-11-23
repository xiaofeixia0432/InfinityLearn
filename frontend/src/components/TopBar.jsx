import { Link } from 'react-router-dom'
import { useAuth } from '../AuthContext.jsx'
import QuoteBar from './QuoteBar.jsx'
import AnalogClock from './AnalogClock.jsx'
import MiniCalendar from './MiniCalendar.jsx'

/* 顶部栏：金融名言轮播 + 指针时钟 + 日历 + 登录/注册（日历右侧） */
export default function TopBar() {
  const { user } = useAuth()

  return (
    <header className="topbar">
      <QuoteBar />
      <AnalogClock />
      <MiniCalendar />
      {!user && (
        <div className="top-auth">
          <Link to="/login" className="ta-btn ghost">
            登录
          </Link>
          <Link to="/register" className="ta-btn primary">
            注册
          </Link>
        </div>
      )}
    </header>
  )
}
