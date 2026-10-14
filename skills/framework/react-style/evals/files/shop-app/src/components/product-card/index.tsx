import { ProductTitle, Wrapper } from './styles'

interface ProductCardProps {
  title: string
  price: number
  onAdd: () => void
}

const ProductCard = ({ title, price, onAdd }: ProductCardProps) => {
  return (
    <Wrapper>
      <ProductTitle>{title}</ProductTitle>
      <span>{price.toFixed(2)} €</span>
      <button type="button" onClick={onAdd}>
        Add to cart
      </button>
    </Wrapper>
  )
}

export default ProductCard
