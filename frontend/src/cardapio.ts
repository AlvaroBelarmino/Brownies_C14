/** Cardápio — preços alinhados à API (backend). */

export type ItemCardapio = {
  sku: string
  nome: string
  /** Texto curto para SEO / card */
  descricao: string
  precoUnitario: number
  /** Nome do ficheiro de imagem em `/images/`. */
  imagem: string
}

export const CARDAPIO: ItemCardapio[] = [
  {
    sku: 'B001',
    nome: 'Brownie clássico',
    descricao: 'Clássico úmido, com cacau intenso e casquinha leve.',
    precoUnitario: 8.0,
    imagem: 'b001.png',
  },
  {
    sku: 'B002',
    nome: 'Brownie recheado',
    descricao: 'Centro cremoso — pedacinho de conforto em cada mordida.',
    precoUnitario: 12.0,
    imagem: 'b002.png',
  },
  {
    sku: 'B003',
    nome: 'Caixa com 4 brownies',
    descricao: 'Para dividir (ou não). Embalagem pronta para presente.',
    precoUnitario: 28.0,
    imagem: 'b003.png',
  },
  {
    sku: 'B004',
    nome: 'Brownie vegano',
    descricao: 'Versão sem ingredientes de origem animal, mesmo sabor marcante.',
    precoUnitario: 10.0,
    imagem: 'b004.png',
  },
]
