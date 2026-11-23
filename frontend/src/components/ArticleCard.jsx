import { Link } from 'react-router-dom'
import {
  moduleVars,
  difficultyText,
  difficultyBadgeClass,
  fmtViews,
  shortDate,
} from '../utils.js'
import { cleanTextForSpeech, useSpeech } from '../hooks/useSpeech.js'

export default function ArticleCard({ article }) {
  const vars = moduleVars(article.module_code, article.module_color)
  const hasTags = Array.isArray(article.tags) && article.tags.length > 0
  const sp = useSpeech()

  function toggleSpeak(e) {
    e.preventDefault()
    e.stopPropagation()
    if (sp.speaking) {
      sp.stop()
    } else {
      sp.speak(cleanTextForSpeech(`${article.title}。${article.summary || ''}`))
    }
  }

  return (
    <Link className="article-card" style={vars} to={`/article/${article.article_id ?? article.id}`}>
      <h3 className="article-card-title">{article.title}</h3>
      {article.summary && <p className="article-card-summary">{article.summary}</p>}
      {hasTags && (
        <div className="tag-row">
          {article.tags.slice(0, 4).map((t) => (
            <span className="tag" key={t}>
              #{t}
            </span>
          ))}
        </div>
      )}
      <div className="article-card-foot">
        <span className={difficultyBadgeClass(article.difficulty)}>
          {difficultyText(article.difficulty)}
        </span>
        {article.duration_minutes != null && <span>⏱ {article.duration_minutes} 分钟</span>}
        {article.views != null && <span>👀 {fmtViews(article.views)}</span>}
        {article.published_at && <span>{shortDate(article.published_at)}</span>}
        {sp.supported && (
          <button
            className={`spk-mini${sp.speaking ? ' on' : ''}`}
            onClick={toggleSpeak}
            title={sp.speaking ? '停止朗读' : '朗读标题和摘要'}
          >
            {sp.speaking ? '⏹' : '🔊'}
          </button>
        )}
      </div>
    </Link>
  )
}
