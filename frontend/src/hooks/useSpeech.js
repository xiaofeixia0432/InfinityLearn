import { useEffect, useRef, useState } from 'react'

/* 浏览器原生朗读（Web Speech API）：分句队列播放，支持暂停/停止/循环/倍速
   中英混排自动分流：中文段用中文语音、英文段用英文语音，避免中文引擎硬念英文的怪腔 */

let voiceCache = { zh: null, en: null }

function pickVoices() {
  if (!('speechSynthesis' in window)) return voiceCache
  const voices = window.speechSynthesis.getVoices() || []
  if (voices.length) {
    const norm = (v) => v.lang.replace('_', '-').toLowerCase()
    voiceCache.zh =
      voices.find((v) => /^zh-cn$/.test(norm(v)) && /tingting|xiaoxiao|meijia|yu-shu/i.test(v.name)) ||
      voices.find((v) => /^zh-cn$/.test(norm(v))) ||
      voices.find((v) => norm(v).startsWith('zh')) ||
      voices[0] ||
      null
    voiceCache.en =
      voices.find((v) => /^en(-us)?$/.test(norm(v)) && /samantha|alex|aria|jenny|guy|aaron/i.test(v.name)) ||
      voices.find((v) => /^en(-us)?$/.test(norm(v))) ||
      voices.find((v) => /^en/.test(norm(v))) ||
      null
  }
  return voiceCache
}

/* 预热：Safari/Chrome 首次 getVoices 可能为空，监听异步加载 */
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    voiceCache = { zh: null, en: null }
    pickVoices()
  }
}

/* 判断一段文本用哪个语音引擎：含汉字倾向中文（中文 TTS 能带读英文词），
   英文引擎念不出中文会跳字/怪音，所以仅纯英文/数字段用英文语音 */
export function isChineseText(s) {
  const han = (s.match(/[\u4e00-\u9fff]/g) || []).length
  if (han === 0) return false
  const letters = (s.match(/[a-zA-Z]/g) || []).length
  return han >= 2 || letters <= han
}

/* Markdown 转朗读纯文本：去代码块/链接/emoji/符号，避免 TTS 念出怪声 */
export function cleanTextForSpeech(md) {
  return (md || '')
    .replace(/```[\s\S]*?```/g, '，代码示例部分略过，')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/https?:\/\/\S+/g, '')
    // 口语对话文章：去掉行首角色前缀（**Agent:** / You: / 客服： 等，含粗体包裹），只读内容
    .replace(/^\s*(?:\*\*)?\s*(?:agent|you|customer|client|seller|buyer|staff|receptionist|landlord|me|a|b)\s*[:：]\s*(?:\*\*)?\s*/gim, '')
    .replace(/^\s*(?:\*\*)?\s*(?:客服|店员|顾客|买家|卖家|房东|中介|老师|同学|路人|甲|乙|我|你)\s*[:：]\s*(?:\*\*)?\s*/gm, '')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/^>\s?/gm, '')
    .replace(/^\s*([-*+]|\d+\.)\s+/gm, '')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/^[-=_*]{3,}\s*$/gm, '')
    .replace(/^[\s\-—–]+$/gm, '')
    // emoji / 表情符号 / 箭头等（会被 TTS 念成"笑脸""扳手"之类的噪音）
    .replace(
      /[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{1F1E6}-\u{1F1FF}\u{2190}-\u{21FF}\u{FE00}-\u{FE0F}\u{2700}-\u{27BF}\u{FE0F}\u{200D}]/gu,
      '',
    )
    // 表格竖线拆成独立行：词汇表中/英文各成一段，各用对应语言语音
    .replace(/\|/g, '\n')
    // 残留 Markdown / 装饰符号
    .replace(/[#*_>~^{}[\]]/g, ' ')
    .replace(/[·•◆■□●○▲△▼▽]/g, '，')
    .replace(/([，,，]){2,}/g, '$1')
    .replace(/\n{2,}/g, '\n')
    .replace(/\s+\n/g, '\n')
    .replace(/[ \t]{2,}/g, ' ')
    .trim()
}

/* 超长段兜底切分（200 字内安全）：优先逗号/空格边界，避免拦腰切断单词 */
function hardSplit(p, max = 200) {
  if (p.length <= max) return [p]
  const out = []
  let rest = p
  while (rest.length > max) {
    const comma = rest.lastIndexOf('，', max)
    const space = rest.lastIndexOf(' ', max)
    let cut = Math.max(comma, space)
    if (cut < max * 0.5) cut = max
    else cut += 1
    out.push(rest.slice(0, cut).trim())
    rest = rest.slice(cut).trim()
  }
  if (rest) out.push(rest)
  return out
}

/* 分句：先按行/括号切段（让英文句与中文翻译分离），再按标点切句 */
export function splitSentences(text) {
  const segments = []
  for (const line of text.split(/\n+/)) {
    // 括号内翻译注释独立成段，交由对应语言语音朗读（全角/半角括号）
    for (const seg of line.split(/(?=[（(])/g)) {
      const t = seg.trim()
      if (t) segments.push(t)
    }
  }
  const raw = segments
    .flatMap((s) => s.match(/[^。！？；!?;]+[。！？；!?;]?/g) || [s])
    .map((s) => s.trim())
    // 丢弃纯符号段（孤立括号/逗号等，念出来就是噪音）
    .filter((s) => /[\u4e00-\u9fffA-Za-z0-9]/.test(s))
  return raw.length ? raw.flatMap((s) => hardSplit(s)) : [text]
}

export function useSpeech() {
  const [speaking, setSpeaking] = useState(false)
  const [paused, setPaused] = useState(false)
  const [loop, setLoop] = useState(false)
  const [rate, setRate] = useState(1)
  const [progress, setProgress] = useState({ cur: 0, total: 0 })

  const chunksRef = useRef([])
  const loopRef = useRef(false)
  const rateRef = useRef(1)
  const stoppedRef = useRef(true)

  useEffect(() => {
    loopRef.current = loop
  }, [loop])
  useEffect(() => {
    rateRef.current = rate
  }, [rate])
  useEffect(() => {
    // 其他实例开始朗读时，本实例静默让位（synthesis 队列由新实例接管）
    function onOther() {
      stoppedRef.current = true
      setSpeaking(false)
      setPaused(false)
    }
    window.addEventListener('il-speech-start', onOther)
    return () => {
      window.removeEventListener('il-speech-start', onOther)
      stoppedRef.current = true
      window.speechSynthesis?.cancel()
    }
  }, [])

  function speakFrom(i) {
    const chunks = chunksRef.current
    if (stoppedRef.current) return
    if (i >= chunks.length) {
      if (loopRef.current) {
        speakFrom(0)
      } else {
        setSpeaking(false)
        setPaused(false)
        setProgress({ cur: 0, total: 0 })
      }
      return
    }
    setProgress({ cur: i + 1, total: chunks.length })
    const u = new SpeechSynthesisUtterance(chunks[i])
    // 英文段用英文语音，中文段用中文语音（互相兜底）
    const { zh, en } = pickVoices()
    const wantEn = !isChineseText(chunks[i])
    const v = wantEn ? en || zh : zh || en
    if (v) {
      u.voice = v
      u.lang = v.lang
    } else {
      u.lang = wantEn ? 'en-US' : 'zh-CN'
    }
    u.rate = rateRef.current
    // Chrome 的 onend/onerror 可能对同一 utterance 触发多次（导致整段重复朗读），
    // 用闭包标记保证每段只推进一次
    let settled = false
    const advance = () => {
      if (settled || stoppedRef.current) return
      settled = true
      speakFrom(i + 1)
    }
    u.onend = advance
    u.onerror = () => {
      if (settled) return
      settled = true
      // 非主动停止的错误（如语音合成异常）：结束整个朗读而不是跳段
      if (!stoppedRef.current) {
        setSpeaking(false)
        setPaused(false)
      }
    }
    window.speechSynthesis.speak(u)
  }

  function speak(text) {
    if (!('speechSynthesis' in window)) return
    // 先通知其他实例让位（同步事件），再接管 synthesis 队列
    window.dispatchEvent(new Event('il-speech-start'))
    window.speechSynthesis.cancel()
    stoppedRef.current = false
    chunksRef.current = splitSentences(text)
    setSpeaking(true)
    setPaused(false)
    speakFrom(0)
  }

  function stop() {
    stoppedRef.current = true
    window.speechSynthesis?.cancel()
    setSpeaking(false)
    setPaused(false)
    setProgress({ cur: 0, total: 0 })
  }

  function pause() {
    window.speechSynthesis?.pause()
    setPaused(true)
  }

  function resume() {
    window.speechSynthesis?.resume()
    setPaused(false)
  }

  return {
    speak,
    stop,
    pause,
    resume,
    speaking,
    paused,
    loop,
    setLoop,
    rate,
    setRate,
    progress,
    supported: typeof window !== 'undefined' && 'speechSynthesis' in window,
  }
}
