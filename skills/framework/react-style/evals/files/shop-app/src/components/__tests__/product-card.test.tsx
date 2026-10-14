import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, it, vi } from 'vitest'
import ProductCard from '../product-card'

it('calls onAdd when the button is clicked', async () => {
  const onAdd = vi.fn()
  render(<ProductCard title="Mug" price={9.5} onAdd={onAdd} />)
  await userEvent.click(screen.getByRole('button', { name: 'Add to cart' }))
  expect(onAdd).toHaveBeenCalledOnce()
})
