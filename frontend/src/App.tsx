import { useMemo, useState } from 'react'
import { CARDAPIO } from './cardapio'
import { ProductImage } from './ProductImage'
import './App.css'

type Totals = {
  subtotal_bruto: number
  desconto_volume: number
  subtotal_apos_volume: number
  desconto_cupom: number
  subtotal_apos_descontos: number
  frete: number
  imposto: number
  total: number
  quantidade_total: number
}

function apiBase(): string {
  return import.meta.env.VITE_API_BASE?.replace(/\/$/, '') ?? 'http://127.0.0.1:8000'
}

function formatBrl(n: number): string {
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function App() {
  const [qty, setQty] = useState<Record<string, number>>(() =>
    Object.fromEntries(CARDAPIO.map((i) => [i.sku, 0])),
  )
  const [cupom, setCupom] = useState('')
  const [result, setResult] = useState<Totals | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const itensPayload = useMemo(() => {
    return CARDAPIO.filter((i) => (qty[i.sku] ?? 0) > 0).map((i) => ({
      sku: i.sku,
      preco_unitario: i.precoUnitario,
      quantidade: qty[i.sku] ?? 0,
    }))
  }, [qty])

  const itensNoCarrinho = useMemo(
    () => CARDAPIO.reduce((n, i) => n + (qty[i.sku] ?? 0), 0),
    [qty],
  )

  async function calcular() {
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const res = await fetch(`${apiBase()}/api/pedido/calcular`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          itens: itensPayload,
          cupom: cupom.trim() === '' ? null : cupom,
        }),
      })
      const data = await res.json().catch(() => null)
      if (!res.ok) {
        const msg =
          typeof data?.detail === 'string'
            ? data.detail
            : Array.isArray(data?.detail)
              ? data.detail.map((d: { msg?: string }) => d?.msg).join(' ')
              : 'Não foi possível calcular o pedido.'
        throw new Error(msg || `Erro ${res.status}`)
      }
      setResult(data as Totals)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Falha na requisição.')
    } finally {
      setLoading(false)
    }
  }

  function setQuantidade(sku: string, raw: string) {
    const v = Number.parseInt(raw, 10)
    setQty((q) => ({
      ...q,
      [sku]: Number.isFinite(v) && v >= 0 ? v : 0,
    }))
  }

  return (
    <div className="layout">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <span className="brand-mark" aria-hidden>
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="10" fill="#8B4513" />
                <path
                  d="M8 20c2-6 6-10 8-10s6 4 8 10"
                  stroke="#F0E8DB"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
                <circle cx="16" cy="12" r="3" fill="#C9A227" />
              </svg>
            </span>
            <div>
              <span className="brand-name">Brownie da Turma</span>
              <span className="brand-sub">Artesanal</span>
            </div>
          </div>
          <nav className="topbar-nav" aria-label="Secções">
            <a href="#produtos">Cardápio</a>
            <a href="#checkout">Pedido</a>
          </nav>
        </div>
      </header>

      <section className="hero">
        <div className="hero-inner">
          <p className="hero-eyebrow">Doceria artesanal</p>
          <h1 className="hero-title">
            Brownies de verdade,
            <br />
            <em className="hero-em">do forno</em> para o seu pedido.
          </h1>
          <p className="hero-lead">
            Monte seu pedido, use cupom quando houver e veja frete e impostos na hora. Fotos dos
            produtos: pasta <code className="inline-code">public/images/</code>.
          </p>
          <div className="hero-badges">
            <span className="pill">Frete grátis a partir de R$ 80</span>
            <span className="pill">12+ unidades · 5% off</span>
            <span className="pill">PROMO10 · INATEL5</span>
          </div>
        </div>
      </section>

      <main className="main-grid">
        <div className="catalog" id="produtos">
          <div className="section-head">
            <h2>Cardápio</h2>
            <p className="section-desc">
              Ajuste as quantidades. Os preços seguem o domínio acordado no projeto (REGRAS.md).
            </p>
          </div>

          <div className="product-grid">
            {CARDAPIO.map((item) => {
              const q = qty[item.sku] ?? 0
              const src = `/images/${item.imagem}`
              return (
                <article key={item.sku} className="product-card">
                  <div className="product-card__media">
                    <ProductImage
                      src={src}
                      alt={`Foto: ${item.nome}`}
                      inicial={item.nome.slice(0, 1)}
                    />
                    {q > 0 ? <span className="product-card__badge">{q} no pedido</span> : null}
                  </div>
                  <div className="product-card__body">
                    <span className="product-card__sku">{item.sku}</span>
                    <h3 className="product-card__title">{item.nome}</h3>
                    <p className="product-card__desc">{item.descricao}</p>
                    <div className="product-card__row">
                      <span className="product-card__price">{formatBrl(item.precoUnitario)}</span>
                      <div className="stepper">
                        <button
                          type="button"
                          className="stepper__btn"
                          aria-label="Diminuir quantidade"
                          disabled={q <= 0}
                          onClick={() =>
                            setQty((prev) => ({
                              ...prev,
                              [item.sku]: Math.max(0, (prev[item.sku] ?? 0) - 1),
                            }))
                          }
                        >
                          −
                        </button>
                        <input
                          className="stepper__input"
                          type="number"
                          min={0}
                          inputMode="numeric"
                          aria-label={`Quantidade de ${item.nome}`}
                          value={q}
                          onChange={(e) => setQuantidade(item.sku, e.target.value)}
                        />
                        <button
                          type="button"
                          className="stepper__btn"
                          aria-label="Aumentar quantidade"
                          onClick={() =>
                            setQty((prev) => ({
                              ...prev,
                              [item.sku]: (prev[item.sku] ?? 0) + 1,
                            }))
                          }
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        </div>

        <aside className="sidebar" id="checkout">
          <div className="sidebar-card sidebar-sticky">
            <h2 className="sidebar-title">Seu pedido</h2>
            <p className="sidebar-meta">
              {itensNoCarrinho === 0
                ? 'Nenhum item selecionado.'
                : `${itensNoCarrinho} unidade(s) no carrinho.`}
            </p>

            <label className="field-label" htmlFor="cupom">
              Cupom de desconto
            </label>
            <input
              id="cupom"
              className="field-input"
              placeholder="Ex.: PROMO10 ou INATEL5"
              value={cupom}
              autoComplete="off"
              onChange={(e) => setCupom(e.target.value)}
            />

            <button
              type="button"
              className="btn-primary"
              disabled={loading}
              onClick={() => void calcular()}
            >
              {loading ? 'Calculando…' : 'Calcular orçamento'}
            </button>

            {error ? <p className="alert alert--error">{error}</p> : null}

            {result ? (
              <div className="receipt">
                <h3 className="receipt__title">Resumo</h3>
                <dl className="receipt__list">
                  <div className="receipt__row">
                    <dt>Subtotal bruto</dt>
                    <dd>{formatBrl(result.subtotal_bruto)}</dd>
                  </div>
                  <div className="receipt__row">
                    <dt>Desconto volume</dt>
                    <dd>− {formatBrl(result.desconto_volume)}</dd>
                  </div>
                  <div className="receipt__row">
                    <dt>Após volume</dt>
                    <dd>{formatBrl(result.subtotal_apos_volume)}</dd>
                  </div>
                  <div className="receipt__row">
                    <dt>Desconto cupom</dt>
                    <dd>− {formatBrl(result.desconto_cupom)}</dd>
                  </div>
                  <div className="receipt__row receipt__row--emph">
                    <dt>Subtotal c/ descontos</dt>
                    <dd>{formatBrl(result.subtotal_apos_descontos)}</dd>
                  </div>
                  <div className="receipt__row">
                    <dt>Frete</dt>
                    <dd>{formatBrl(result.frete)}</dd>
                  </div>
                  <div className="receipt__row">
                    <dt>Imposto (12%)</dt>
                    <dd>{formatBrl(result.imposto)}</dd>
                  </div>
                  <div className="receipt__row receipt__row--total">
                    <dt>Total</dt>
                    <dd>{formatBrl(result.total)}</dd>
                  </div>
                  <div className="receipt__row receipt__row--muted">
                    <dt>Unidades</dt>
                    <dd>{result.quantidade_total}</dd>
                  </div>
                </dl>
              </div>
            ) : null}

            <p className="dev-hint">
              API: <span className="dev-hint__url">{apiBase()}</span>
            </p>
          </div>
        </aside>
      </main>

      <footer className="footer">
        <p>
          Doceria — orçamento online. Imagens em <code>public/images/</code>.
        </p>
      </footer>
    </div>
  )
}

export default App
