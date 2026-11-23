import { useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'
import TopBar from './components/TopBar.jsx'
import BottomNav from './components/BottomNav.jsx'
import Home from './pages/Home.jsx'
import Module from './pages/Module.jsx'
import Article from './pages/Article.jsx'
import Daily from './pages/Daily.jsx'
import Plans from './pages/Plans.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Profile from './pages/Profile.jsx'
import Admin from './pages/Admin.jsx'

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

export default function App() {
  return (
    <div className="app-shell">
      <ScrollToTop />
      <Sidebar />
      <div className="app-body">
        <TopBar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/module/:code" element={<Module />} />
            <Route path="/article/:id" element={<Article />} />
            <Route path="/daily" element={<Daily />} />
            <Route path="/plans" element={<Plans />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="*" element={<Home />} />
          </Routes>
        </main>
        <footer className="app-footer">
          <span>
            <b className="foot-brand">无限学堂 InfinityLearn</b> · 每天进步一点点，无限知识等你学
          </span>
        </footer>
      </div>
      <BottomNav />
    </div>
  )
}
