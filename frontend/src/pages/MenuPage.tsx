import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

type FoodItem = {
  id: number
  name: string
  price: number
  vendor_id: number
}

export function MenuPage() {
  const [items, setItems] = useState<FoodItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [addingId, setAddingId] = useState<number | null>(null)
  const { token } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const res = await api.get<FoodItem[]>('/menu/')
        setItems(res.data)
      } catch {
        setError('Failed to load menu')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [])

  async function addToCart(id: number) {
    if (!token) {
      navigate('/login')
      return
    }
    setAddingId(id)
    try {
      await api.post('/cart/', { food_id: id, quantity: 1 })
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Failed to add to cart')
    } finally {
      setAddingId(null)
    }
  }

  if (loading) return <div className="page">Loading menu…</div>
  if (error) return <div className="page error">{error}</div>

  return (
    <div className="page">
      <h1>Campus Menu</h1>
      <div className="grid">
        {items.map((item) => (
          <div className="card" key={item.id}>
            <h2>{item.name}</h2>
            <p>₹{item.price.toFixed(2)}</p>
            <p className="muted">Vendor #{item.vendor_id}</p>
            <button
              onClick={() => addToCart(item.id)}
              disabled={addingId === item.id}
            >
              {addingId === item.id ? 'Adding…' : 'Add to cart'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

