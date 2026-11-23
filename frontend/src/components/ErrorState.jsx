export default function ErrorState({ message = '加载失败，请稍后重试', onRetry }) {
  return (
    <div className="state-wrap">
      <div className="state-ico">⚠️</div>
      <div className="state-text">{message}</div>
      {onRetry && (
        <button className="btn btn-ghost btn-sm" onClick={onRetry}>
          重试
        </button>
      )}
    </div>
  )
}
