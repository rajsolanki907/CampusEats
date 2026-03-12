import { FormEvent, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Order = {
  id: number
  user_id: number
  total_price: number
  status: string
}

export function VendorPage() {
  const { token, user } = useAuth()
  const navigate = useNavigate()
  const [restaurantName, setRestaurantName] = useState('')
  const [description, setDescription] = useState('')
  const [menuName, setMenuName] = useState('')
  const [menuPrice, setMenuPrice] = useState<number | ''>('')
  const [dashboardOrders, setDashboardOrders] = useState<Order[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    async function loadDashboard() {
      try {
        const res = await api.get<Order[]>('/vendor/dashboard')
        setDashboardOrders(res.data)
      } catch {
        // ignore if user is not a vendor yet
      }
    }
    void loadDashboard()
  }, [token, navigate])

  async function handleCreateVendor(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await api.post('/vendors/', {
        restaurant_name: restaurantName,
        description,
      })
      alert('Vendor profile created')
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Failed to create vendor')
    }
  }

  async function handleAddMenuItem(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await api.post('/vendors/my-menu/items', {
        name: menuName,
        price: Number(menuPrice),
      })
      alert('Menu item added')
      setMenuName('')
      setMenuPrice('')
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Failed to add menu item')
    }
  }

  async function updateStatus(id: number, newStatus: string) {
    try {
      const res = await api.put<Order>(
        `/vendor/orders/${id}/status`,
        null,
        { params: { new_status: newStatus } },
      )
      setDashboardOrders((orders) =>
        orders.map((o) => (o.id === id ? res.data : o)),
      )
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Failed to update status')
    }
  }

  return (
    <div className="page">
      <h1>Vendor Dashboard</h1>
      {user && <p className="muted">Logged in as {user.username}</p>}
      {error && <p className="error">{error}</p>}

      <div className="grid">
        <form onSubmit={handleCreateVendor} className="card form-card">
          <h2>Create / Update Vendor Profile</h2>
          <label>
            Restaurant name
            <input
              value={restaurantName}
              onChange={(e) => setRestaurantName(e.target.value)}
              required
            />
          </label>
          <label>
            Description
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </label>
          <button type="submit">Save vendor</button>
        </form>

        <form onSubmit={handleAddMenuItem} className="card form-card">
          <h2>Add Menu Item</h2>
          <label>
            Name
            <input
              value={menuName}
              onChange={(e) => setMenuName(e.target.value)}
              required
            />
          </label>
          <label>
            Price
            <input
              type="number"
              step="0.01"
              value={menuPrice}
              onChange={(e) =>
                setMenuPrice(e.target.value === '' ? '' : Number(e.target.value))
              }
              required
            />
          </label>
          <button type="submit">Add item</button>
        </form>
      </div>

      <section className="mt-lg">
        <h2>Incoming Orders</h2>
        {dashboardOrders.length === 0 ? (
          <p>No orders yet.</p>
        ) : (
          <ul className="list">
            {dashboardOrders.map((order) => (
              <li key={order.id} className="card list-item">
                <div className="order-header">
                  <div>
                    <strong>Order #{order.id}</strong>
                    <p className="muted">Customer #{order.user_id}</p>
                  </div>
                  <div>
                    <span className="badge">{order.status}</span>
                    <div>₹{order.total_price.toFixed(2)}</div>
                  </div>
                </div>
                <div className="order-actions">
                  {['Pending', 'Accepted', 'Delivered'].map((status) => (
                    <button
                      key={status}
                      type="button"
                      onClick={() => updateStatus(order.id, status)}
                      disabled={order.status === status}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}

