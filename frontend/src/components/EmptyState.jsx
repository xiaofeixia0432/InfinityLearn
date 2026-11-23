export default function EmptyState({ text = '暂无内容', emoji = '📭' }) {
  return (
    <div className="state-wrap">
      <div className="state-ico">{emoji}</div>
      <div className="state-text">{text}</div>
    </div>
  )
}
