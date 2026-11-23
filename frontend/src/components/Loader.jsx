export default function Loader({ text = '加载中…' }) {
  return (
    <div className="state-wrap">
      <div className="loader" />
      <div className="state-text">{text}</div>
    </div>
  )
}
