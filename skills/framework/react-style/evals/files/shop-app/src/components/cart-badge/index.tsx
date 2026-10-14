import { useCartStore } from '@/store/cart'
import { Badge } from './styles'

interface CartBadgeProps {
  label?: string
}

const CartBadge = ({ label = 'Cart' }: CartBadgeProps) => {
  const count = useCartStore((s) => s.items.length)
  return (
    <Badge aria-label={`${label}: ${count} items`}>
      {label} ({count})
    </Badge>
  )
}

export default CartBadge
