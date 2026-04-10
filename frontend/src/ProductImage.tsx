import { useState } from 'react'

type Props = {
  src: string
  alt: string
  inicial: string
}

/** Foto do produto ou placeholder com a inicial. */
export function ProductImage({ src, alt, inicial }: Props) {
  const [erro, setErro] = useState(false)

  if (erro) {
    return (
      <div className="product-image-fallback" aria-hidden>
        <span className="product-image-fallback__glyph">{inicial}</span>
        <span className="product-image-fallback__hint">Foto: em breve</span>
      </div>
    )
  }

  return (
    <img
      className="product-image"
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      onError={() => setErro(true)}
    />
  )
}
