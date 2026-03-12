import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type OrderItem = {
  id: number
  food_id: number
  quantity: number
  unit_price: number
  food?: {
    name: string
  }
}

type Order = {
  id: number
  vendor_id: number
  total_price: number
  status: string
  items?: OrderItem[]
}

export function OrdersPage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    async function load() {
      setLoading(true)
      try {
        const res = await api.get<Order[]>('/orders/me')
        setOrders(res.data)
      } catch (err: any) {
        setError(err?.response?.data?.detail ?? 'Failed to load orders')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [token, navigate])

  if (loading) return <div className="page">Loading orders…</div>
  if (error) return <div className="page error">{error}</div>

  return (
    <div className="page">
      <h1>My Orders</h1>
      {orders.length === 0 ? (
        <p>You have no past orders yet.</p>
      ) : (
        <ul className="list">
          {orders.map((order) => (
            <li key={order.id} className="card list-item">
              <div className="order-header">
                <div>
                  <strong>Order #{order.id}</strong>
                  <p className="muted">Vendor #{order.vendor_id}</p>
                </div>
                <div>
                  <span className="badge">{order.status}</span>
                  <div>₹{order.total_price.toFixed(2)}</div>
                </div>
              </div>
              {order.items && order.items.length > 0 && (
                <ul className="order-items">
                  {order.items.map((item) => (
                    <li key={item.id}>
                      {item.food?.name ?? `Item #${item.food_id}`} ×{' '}
                      {item.quantity} @ ₹{item.unit_price.toFixed(2)}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

