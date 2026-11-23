import { useEffect, useState } from 'react'
import { api } from '../api.js'
import QuoteModal from './QuoteModal.jsx'

/* 金融名言轮播：8 秒切换，彩色流光边框；支持用户自定义名言合并进轮播池 */
const BUILTIN_QUOTES = [
  { text: '别人贪婪时我恐惧，别人恐惧时我贪婪。', author: '沃伦·巴菲特' },
  { text: '价格是你付出的，价值是你得到的。', author: '沃伦·巴菲特' },
  { text: '只有在退潮时，才知道谁在裸泳。', author: '沃伦·巴菲特' },
  { text: '第一条原则是不要亏钱，第二条原则是记住第一条。', author: '沃伦·巴菲特' },
  { text: '人生就像滚雪球，重要的是找到很湿的雪和很长的坡。', author: '沃伦·巴菲特' },
  { text: '风险来自于你不知道自己在做什么。', author: '沃伦·巴菲特' },
  { text: '最好的投资，是投资自己。', author: '沃伦·巴菲特' },
  { text: '市场短期是投票机，长期是称重机。', author: '本杰明·格雷厄姆' },
  { text: '市场先生每天都会报价，但他不是来指导你的，而是来服务你的。', author: '本杰明·格雷厄姆' },
  { text: '如果我知道我会死在哪里，我就永远不去那里。', author: '查理·芒格' },
  { text: '反过来想，总是反过来想。', author: '查理·芒格' },
  { text: '长期来看，股票的回报率几乎等于企业的资本回报率。', author: '查理·芒格' },
  { text: '重要的不是你对还是错，而是你对时赚了多少，错时亏了多少。', author: '乔治·索罗斯' },
  { text: '华尔街没有新鲜事，因为人性永恒。', author: '杰西·利弗莫尔' },
  { text: '钱是坐着等来的，不是靠频繁交易赚来的。', author: '杰西·利弗莫尔' },
  { text: '你翻的石头越多，找到好股票的机会越大。', author: '彼得·林奇' },
  { text: '知道你为什么买入，比知道什么时候买更重要。', author: '彼得·林奇' },
  { text: '买入你真正了解的公司，长期持有。', author: '菲利普·费雪' },
  { text: '行情在绝望中诞生，在怀疑中成长，在乐观中成熟，在兴奋中死亡。', author: '约翰·邓普顿' },
  { text: '在别人都卖出时买入，在别人都买入时卖出。', author: '伯纳德·巴鲁克' },
  { text: '不要把所有鸡蛋放在同一个篮子里。', author: '詹姆斯·托宾' },
  { text: '复利是世界第八大奇迹。', author: '阿尔伯特·爱因斯坦' },
  { text: '痛苦 + 反思 = 进步。', author: '瑞·达利欧' },
  { text: '有钱的人可以投机，钱少的人不可以投机，根本没钱的人必须投机。', author: '安德烈·科斯托拉尼' },
]

export default function QuoteBar() {
  const [custom, setCustom] = useState([])
  const [idx, setIdx] = useState(0)
  const [fading, setFading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)

  // 拉取用户自定义名言，合并进轮播池（自定义优先展示）
  useEffect(() => {
    let cancelled = false
    api
      .get('/api/quotes')
      .then((data) => {
        if (!cancelled && Array.isArray(data.items)) {
          setCustom(data.items.map((q) => ({ text: q.text, author: q.author })))
        }
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  const pool = custom.length ? [...custom, ...BUILTIN_QUOTES] : BUILTIN_QUOTES

  // 8 秒切换：先淡出文本（0.32s）→ 换内容 → 淡入；外壳不重挂，边框动画连续无闪烁
  useEffect(() => {
    const t = setInterval(() => {
      setFading(true)
      setTimeout(() => {
        setIdx((i) => (i + 1) % pool.length)
        setFading(false)
      }, 330)
    }, 8000)
    return () => clearInterval(t)
  }, [pool.length])

  // 弹窗关闭后刷新自定义列表（有新增/删除时）
  useEffect(() => {
    if (modalOpen) return
    api
      .get('/api/quotes')
      .then((data) => {
        if (Array.isArray(data.items)) {
          setCustom(data.items.map((q) => ({ text: q.text, author: q.author })))
        }
      })
      .catch(() => {})
  }, [modalOpen])

  const q = pool[idx % pool.length]

  return (
    <div className="quote-bar">
      <span className="quote-glow" aria-hidden="true" />
      <div className={`quote-inner${fading ? ' fading' : ''}`}>
        <span className="quote-mark">❝</span>
        <div className="quote-body">
          <p className="quote-text">{q.text}</p>
          <span className="quote-author">—— {q.author}</span>
        </div>
        <button
          className="quote-add"
          onClick={() => setModalOpen(true)}
          title="添加我的名言"
        >
          ✚
        </button>
        <span className="quote-tag">金融箴言</span>
      </div>
      {modalOpen && <QuoteModal onClose={() => setModalOpen(false)} />}
    </div>
  )
}
