/* 统一 SVG 线性图标集（stroke 风格，跟随 currentColor），替代 emoji 图标 */

const PATHS = {
  home: (
    <>
      <path d="M4 10.8 12 4l8 6.8V20a1 1 0 0 1-1 1h-4.6v-5.6h-4.8V21H5a1 1 0 0 1-1-1v-9.2Z" />
      <path d="M9.6 14.2h4.8" opacity=".55" />
    </>
  ),
  daily: (
    <>
      <rect x="3.5" y="5" width="17" height="16" rx="3" />
      <path d="M3.5 10h17M8 2.8V7M16 2.8V7" />
      <path d="m9 15 2.2 2.2L15.5 13" opacity=".6" />
    </>
  ),
  plan: (
    <>
      <rect x="5" y="4" width="14" height="17" rx="3" />
      <path d="M9 2.5h6v3.4H9z" />
      <path d="m8.4 12 1.6 1.6 3-3.2M8.4 17l1.6 1.6 3-3.2" opacity=".6" />
    </>
  ),
  english: (
    <>
      <path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v8a2.5 2.5 0 0 1-2.5 2.5H12l-4.5 3.6V17H6.5A2.5 2.5 0 0 1 4 14.5v-8Z" />
      <path d="M8.2 10.6h.01M12 10.6h.01M15.8 10.6h.01" strokeWidth="2.6" opacity=".65" />
    </>
  ),
  embedded: (
    <>
      <rect x="7" y="7" width="10" height="10" rx="2" />
      <rect x="10.2" y="10.2" width="3.6" height="3.6" rx="1" opacity=".6" />
      <path d="M9.5 7V4M14.5 7V4M9.5 20v-3M14.5 20v-3M7 9.5H4M7 14.5H4M20 9.5h-3M20 14.5h-3" opacity=".7" />
    </>
  ),
  ecommerce: (
    <>
      <path d="M5.5 8h13l-1 12a1.8 1.8 0 0 1-1.8 1.6H8.3A1.8 1.8 0 0 1 6.5 20l-1-12Z" />
      <path d="M8.8 10.5V6.7a3.2 3.2 0 0 1 6.4 0v3.8" opacity=".7" />
    </>
  ),
  science: (
    <>
      <path d="M9.5 3h5M10.5 3v5.2L4.8 18.2A2 2 0 0 0 6.6 21h10.8a2 2 0 0 0 1.8-2.8L13.5 8.2V3" />
      <path d="M7.5 15.5h9" opacity=".6" />
    </>
  ),
  finance: (
    <>
      <path d="M3.5 20.5h17" opacity=".5" />
      <path d="m4.5 15.5 4.2-4.6 3.4 3 6-6.8" />
      <path d="M14.6 6.8h3.7v3.7" />
    </>
  ),
  book: (
    <>
      <path d="M12 6.8C10.5 5.2 8.4 4.5 4 4.5v14c4.4 0 6.5.7 8 2.3 1.5-1.6 3.6-2.3 8-2.3v-14c-4.4 0-6.5.7-8 2.3Z" />
      <path d="M12 6.8V20.6" opacity=".55" />
    </>
  ),
  logout: (
    <>
      <path d="M14.5 3.5H7A2.5 2.5 0 0 0 4.5 6v12A2.5 2.5 0 0 0 7 20.5h7.5" />
      <path d="M15.5 8.2 19.5 12l-4 3.8M19 12h-9" opacity=".7" />
    </>
  ),
  user: (
    <>
      <circle cx="12" cy="8.2" r="3.8" />
      <path d="M4.5 20.4c1.2-3.6 4-5.4 7.5-5.4s6.3 1.8 7.5 5.4" />
    </>
  ),
  audio: (
    <>
      <path d="M4 9.5h3.2L12 5.4v13.2l-4.8-4.1H4a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1Z" />
      <path d="M15.5 9.2a4 4 0 0 1 0 5.6M18 6.8a7.4 7.4 0 0 1 0 10.4" opacity=".65" />
    </>
  ),
  crawler: (
    <>
      <circle cx="12" cy="12" r="2.6" />
      <circle cx="5.2" cy="6.8" r="1.5" />
      <circle cx="18.8" cy="6.8" r="1.5" />
      <circle cx="5.2" cy="17.2" r="1.5" />
      <circle cx="18.8" cy="17.2" r="1.5" />
      <path d="M10.2 10.4 6.5 7.9M13.8 10.4l3.7-2.5M10.2 13.6l-3.7 2.5M13.8 13.6l3.7 2.5" />
    </>
  ),
  python: (
    <>
      <path d="M9.6 8.2h6a2.8 2.8 0 0 1 0 5.6h-3.4" />
      <path d="M14.4 15.8h-6a2.8 2.8 0 0 1 0-5.6h3.4" />
      <circle cx="10.6" cy="10.2" r=".95" fill="currentColor" stroke="none" />
      <circle cx="13.4" cy="13.8" r=".95" fill="currentColor" stroke="none" />
    </>
  ),
  fastapi: (
    <>
      <path d="M13.4 2.6 5.6 13.4h5.1l-1.1 8 7.8-10.9h-5.1l1.1-7.9Z" />
    </>
  ),
  ai: (
    <>
      <rect x="6" y="9" width="12" height="9.5" rx="2.5" />
      <circle cx="9.8" cy="13.3" r="1.05" fill="currentColor" stroke="none" />
      <circle cx="14.2" cy="13.3" r="1.05" fill="currentColor" stroke="none" />
      <path d="M12 9V6.4" />
      <circle cx="12" cy="5.1" r="1.2" />
      <path d="M3.5 12.5v3.2M20.5 12.5v3.2" />
    </>
  ),
  agent: (
    <>
      <path d="M12 4.3c3.7 0 6.4 2.5 6.4 5.9 0 1.5-.6 2.9-1.5 3.9.9.8 1.5 2 1.5 3.4 0 3.1-2.9 5.4-6.4 5.4s-6.4-2.3-6.4-5.4c0-1.4.6-2.6 1.5-3.4-.9-1-1.5-2.4-1.5-3.9 0-3.4 2.7-5.9 6.4-5.9Z" />
      <path d="M12 4.3v18.6M8.8 9.3c1.3.5 3.1.5 6.4 0M8.8 15.7c1.3-.5 3.1-.5 6.4 0" opacity=".7" />
    </>
  ),
}

/* 模块 code → 图标名（数据库 icon 为 emoji，前端统一映射为 SVG） */
export function moduleIconName(code) {
  return {
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
  }[code] || 'book'
}

export default function Icon({ name, size = 17, strokeWidth = 1.8, className = '', style }) {
  const glyph = PATHS[name] || PATHS.book
  return (
    <svg
      className={className}
      style={style}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {glyph}
    </svg>
  )
}
