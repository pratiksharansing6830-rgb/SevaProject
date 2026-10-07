import { Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from '../auth/ProtectedRoute'
import { Footer } from '../components/layout/Footer'
import { Navbar } from '../components/layout/Navbar'
import About from '../pages/About'
import CitizenDashboard from '../pages/CitizenDashboard'
import HelpPage from '../pages/HelpPage'
import Home from '../pages/Home'
import HowItWorks from '../pages/HowItWorks'
import Login from '../pages/Login'
import NotFound from '../pages/NotFound'
import Register from '../pages/Register'
import RoleSelection from '../pages/RoleSelection'
import ServicesPage from '../pages/ServicesPage'
import { AddChildPage, FamilyCreatePage, FamilyDashboard, FamilyDetailPage, MigrationPage } from '../pages/FamilyPages'
import { ChildProfilePage, ChildServicePage, ContinuityPage } from '../pages/ChildPages'

export function AppRoutes() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-slate-50">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/role-selection" element={<RoleSelection />} />
          <Route path="/dashboard" element={<ProtectedRoute><CitizenDashboard /></ProtectedRoute>} />
          <Route path="/family" element={<ProtectedRoute><FamilyDashboard /></ProtectedRoute>} />
          <Route path="/family/create" element={<ProtectedRoute><FamilyCreatePage /></ProtectedRoute>} />
          <Route path="/family/:familyId" element={<ProtectedRoute><FamilyDetailPage /></ProtectedRoute>} />
          <Route path="/family/:familyId/children" element={<ProtectedRoute><AddChildPage /></ProtectedRoute>} />
          <Route path="/children/:childId" element={<ProtectedRoute><ChildProfilePage /></ProtectedRoute>} />
          <Route path="/children/:childId/continuity" element={<ProtectedRoute><ContinuityPage /></ProtectedRoute>} />
          <Route path="/children/:childId/:service" element={<ProtectedRoute><ChildServicePage /></ProtectedRoute>} />
          <Route path="/migration" element={<ProtectedRoute><MigrationPage /></ProtectedRoute>} />
          <Route path="/help" element={<HelpPage />} />
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </>
  )
}
