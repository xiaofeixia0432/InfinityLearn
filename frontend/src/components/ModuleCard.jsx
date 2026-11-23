import { Link, useNavigate } from 'react-router-dom'
import { moduleVars } from '../utils.js'
import Icon, { moduleIconName } from './Icon.jsx'

/* 模块卡：有子模块时卡片本身可点击进入子模块选择页，卡内列出子模块快捷入口 */
export default function ModuleCard({ module, subModules = [] }) {
  const vars = moduleVars(module.code, module.color)
  const navigate = useNavigate()
  const hasSubs = subModules.length > 0

  const body = (
    <>
      <div className="module-ico">
        <Icon name={moduleIconName(module.code)} size={30} strokeWidth={1.7} />
      </div>
      <h3 className="module-name">{module.name}</h3>
      <p className="module-desc">{module.description || '持续更新中的学习内容'}</p>

      {hasSubs && (
        <div className="module-subs">
          {subModules.map((s) => (
            <Link
              key={s.code}
              to={`/module/${s.code}`}
              className="module-sub"
              onClick={(e) => e.stopPropagation()}
            >
              <Icon name={moduleIconName(s.code)} size={13} />
              <span>{s.name}</span>
              <i>{s.article_count ?? 0}</i>
            </Link>
          ))}
        </div>
      )}

      <div className="module-meta">
        {hasSubs ? (
          <span className="module-chip">{subModules.length} 个子模块</span>
        ) : (
          <span className="module-chip">{module.article_count ?? 0} 篇文章</span>
        )}
        {Number(module.today_count) > 0 && (
          <span className="module-today">今日 +{module.today_count}</span>
        )}
      </div>
    </>
  )

  if (!hasSubs) {
    return (
      <Link className="module-card" style={vars} to={`/module/${module.code}`}>
        {body}
      </Link>
    )
  }

  return (
    <div
      className="module-card"
      style={vars}
      role="link"
      tabIndex={0}
      onClick={() => navigate(`/module/${module.code}`)}
      onKeyDown={(e) => {
        if (e.key === 'Enter') navigate(`/module/${module.code}`)
      }}
    >
      {body}
    </div>
  )
}
