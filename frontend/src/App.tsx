import './App.css'
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { MenuPage } from './pages/MenuPage'
import { CartPage } from './pages/CartPage'
import { OrdersPage } from './pages/OrdersPage'
import { VendorPage } from './pages/VendorPage'
import { AuthProvider, useAuth } from './context/AuthContext'

function AppShell() {
  const { user, token, logout } = useAuth()

  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <div className="brand">
            <span role="img" aria-label="food">
              🍔
            </span>{' '}
            CampusEats
          </div>
          <nav className="nav">
            <Link to="/">Menu</Link>
            <Link to="/cart">Cart</Link>
            <Link to="/orders">Orders</Link>
            <Link to="/vendor">Vendor</Link>
          </nav>
          <div className="auth-area">
            {token && user ? (
              <>
                <span className="muted">Hi, {user.username}</span>
                <button onClick={logout}>Logout</button>
              </>
            ) : (
              <>
                <Link to="/login">Login</Link>
                <Link to="/register">Sign up</Link>
              </>
            )}
          </div>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<MenuPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/vendor" element={<VendorPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  )
}
