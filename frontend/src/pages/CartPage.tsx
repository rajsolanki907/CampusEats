import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Food = {
  id: number
  name: string
  price: number
  vendor_id: number
}

type CartItem = {
  id: number
  food_id: number
  quantity: number
  food?: Food
}

export function CartPage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [items, setItems] = useState<CartItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [checkingOut, setCheckingOut] = useState(false)

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    async function load() {
      setLoading(true)
      try {
        const res = await api.get<CartItem[]>('/cart/')
        setItems(res.data)
      } catch (err: any) {
        setError(err?.response?.data?.detail ?? 'Failed to load cart')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [token, navigate])

  const total = useMemo(
    () =>
      items.reduce(
        (sum, item) =>
          sum + (item.food?.price ?? 0) * (item.quantity ?? 0),
        0,
      ),
    [items],
  )

  async function checkout() {
    setCheckingOut(true)
    setError(null)
    try {
      await api.post('/cart/checkout')
      navigate('/orders')
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Checkout failed')
    } finally {
      setCheckingOut(false)
    }
  }

  if (loading) return <div className="page">Loading cart…</div>

  return (
    <div className="page">
      <h1>My Cart</h1>
      {items.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <>
          <ul className="list">
            {items.map((item) => (
              <li key={item.id} className="card list-item">
                <div>
                  <strong>{item.food?.name ?? `Item #${item.food_id}`}</strong>
                  <p className="muted">
                    Qty: {item.quantity} · ₹{item.food?.price.toFixed(2) ?? '—'}
                  </p>
                </div>
              </li>
            ))}
          </ul>
          <div className="cart-summary">
            <span>Total:</span>
            <strong>₹{total.toFixed(2)}</strong>
          </div>
          {error && <p className="error">{error}</p>}
          <button onClick={checkout} disabled={checkingOut}>
            {checkingOut ? 'Placing order…' : 'Checkout'}
          </button>
        </>
      )}
    </div>
  )
}

