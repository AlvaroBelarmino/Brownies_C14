# Regras de negócio — Doceria (brownies)

Especificação de negócio da doceria. Os valores são **exemplificativos**; mantenham **consistência** entre esta documentação, a API e qualquer código que implemente essas regras.

---

## 1. Cardápio (preços unitários em R$)

| SKU  | Descrição              | Preço unitário |
|------|------------------------|----------------|
| B001 | Brownie clássico       | 8,00           |
| B002 | Brownie recheado       | 12,00          |
| B003 | Caixa 4 brownies       | 28,00          |
| B004 | Brownie vegano         | 10,00          |

Na API e no front, o pedido usa **SKU**, **quantidade** e **preço unitário** (em geral alinhados a esta tabela).

**Subtotal bruto:** soma de `(preço unitário × quantidade)` de todas as linhas.

**Quantidade total:** soma das **quantidades** de todas as linhas (serve para o desconto por volume).

---

## 2. Desconto por volume

- Se **quantidade total** ≥ **12 unidades**, aplicar **5%** sobre o **subtotal bruto**.
- Caso contrário, **não** há desconto por volume.

---

## 3. Cupons (case insensitive, trim)

Após o desconto por volume, aplicar **no máximo um** desconto percentual extra por cupom válido, sobre o subtotal **já reduzido pelo volume**.

| Cupom (após normalizar) | Desconto |
|-------------------------|----------|
| `PROMO10`               | 10%      |
| `INATEL5`               | 5%       |

- **Normalização:** remover espaços nas pontas (`strip`); comparar nome em maiúsculas.
- **Cupom vazio** ou **somente espaços:** tratar como **sem cupom** (0% desta etapa).
- **Cupom desconhecido:** **ignorar** só a parte do cupom (0% desta etapa), **sem falhar** o pedido. Se mudarem esta política, atualizem este documento de regras.

Chamaremos **subtotal após descontos** o valor após volume + cupom.

---

## 4. Ordem de aplicação dos descontos

1. Subtotal bruto  
2. Desconto por **volume** (se aplicável)  
3. Desconto de **cupom** (se aplicável) sobre o resultado de (2)  

---

## 5. Frete

- **Frete fixo:** R$ 10,00 quando **subtotal após descontos** \< **80,00**.
- **Frete grátis:** quando **subtotal após descontos** ≥ **80,00**, frete = R$ 0,00.

---

## 6. Imposto

- **Alíquota:** **12%** sobre **(subtotal após descontos + frete)**.

---

## 7. Total

**Total = subtotal após descontos + frete + imposto**

---

## 8. Arredondamento

Todos os valores monetários **intermediários e finais** expostos pelo domínio (centavos) usam **arredondamento para 2 casas decimais** (`round(valor, 2)` em Python). Meio centavo segue o comportamento padrão do `round` em Python no escopo atual do projeto.

### Políticas para casos-limite

- **Pedido sem itens:** totais **0,00** e **frete 0** (sem cobrança de frete em carrinho vazio).
- **Quantidade zero em linha:** **rejeição** (`ValueError` no domínio; **422** na API se validado pelo contrato HTTP).
- **Preço unitário zero:** **aceito** (item “brinde”); frete e imposto seguem as faixas sobre o subtotal após descontos.

---

## 9. Cenários sugeridos para validação

Lista de referência para garantir cobertura de fluxo principal e exceções (incluindo testes automatizados, se houver).

### Fluxo normal (10)

- [ ] **T1** — Um item, quantidade 1, sem cupom; subtotal abaixo do frete grátis; frete R$ 10 e imposto coerentes  
- [ ] **T2** — Vários itens, sem cupom; subtotal abaixo de R$ 80; frete cobrado  
- [ ] **T3** — Subtotal após descontos ≥ R$ 80; frete zero  
- [ ] **T4** — Quantidade total ≥ 12; desconto por volume de 5% aplicado antes do cupom  
- [ ] **T5** — Cupom válido (`PROMO10`) sem desconto por volume; apenas 10% no subtotal bruto  
- [ ] **T6** — Cupom válido (`INATEL5`) com desconto por volume; ordem volume → cupom verificada  
- [ ] **T7** — Um único SKU em quantidade alta (ex.: 15 unidades); volume + eventual frete grátis coerentes  
- [ ] **T8** — Preços com centavos (ex.: 8,99); resultado com 2 casas decimais estável  
- [ ] **T9** — Cupom com espaços nas pontas (`"  promo10  "`) normalizado e aceito  
- [ ] **T10** — Várias linhas no carrinho; subtotal bruto igual à soma manual das linhas  

### Fluxo de extensão (10)

- [ ] **T11** — Lista de itens vazia; comportamento definido (ex.: totais zero ou exceção — alinhar com implementação)  
- [ ] **T12** — Quantidade zero em uma linha; política de rejeição ou ignorar linha  
- [ ] **T13** — Quantidade negativa; rejeição  
- [ ] **T14** — Preço unitário zero; política documentada acima (brinde)  
- [ ] **T15** — Preço unitário negativo; rejeição  
- [ ] **T16** — Cupom inválido; ignorado sem quebrar o restante do cálculo  
- [ ] **T17** — `cupom = None` vs string vazia vs espaços; comportamento consistente com a regra 3  
- [ ] **T18** — Subtotal após descontos **exatamente** R$ 80,00; frete grátis (frete = 0)  
- [ ] **T19** — Subtotal após descontos **R$ 79,99**; frete R$ 10 aplicado  
- [ ] **T20** — Pedido mínimo que apenas atinge limiar de volume com subtotal pequeno; frete e imposto coerentes com as faixas  
