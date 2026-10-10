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
import MapPage from '../pages/MapPage'
import NotFound from '../pages/NotFound'
import Register from '../pages/Register'
import RoleSelection from '../pages/RoleSelection'
import ServicesPage from '../pages/ServicesPage'
import { AddChildPage, FamilyCreatePage, FamilyDashboard, FamilyDetailPage, MigrationPage } from '../pages/FamilyPages'
import { ChildProfilePage, ChildServicePage, ContinuityPage } from '../pages/ChildPages'
import GovernmentDashboard from '../pages/GovernmentDashboard'

export function AppRoutes() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-slate-50">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/map" element={<ProtectedRoute><MapPage /></ProtectedRoute>} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/role-selection" element={<RoleSelection />} />
          <Route path="/dashboard" element={<ProtectedRoute allowedRoles={['CITIZEN', 'NGO_WORKER', 'ADMIN']}><CitizenDashboard /></ProtectedRoute>} />
          <Route path="/government/dashboard" element={<ProtectedRoute allowedRoles={['GOVERNMENT', 'ADMIN']}><GovernmentDashboard /></ProtectedRoute>} />
          <Route path="/family" element={<ProtectedRoute allowedRoles={['CITIZEN', 'NGO_WORKER', 'ADMIN']}><FamilyDashboard /></ProtectedRoute>} />
          <Route path="/family/create" element={<ProtectedRoute allowedRoles={['CITIZEN', 'ADMIN']}><FamilyCreatePage /></ProtectedRoute>} />
          <Route path="/family/:familyId" element={<ProtectedRoute allowedRoles={['CITIZEN', 'NGO_WORKER', 'ADMIN']}><FamilyDetailPage /></ProtectedRoute>} />
          <Route path="/family/:familyId/children" element={<ProtectedRoute allowedRoles={['CITIZEN', 'NGO_WORKER', 'ADMIN']}><AddChildPage /></ProtectedRoute>} />
          <Route path="/children/:childId" element={<ProtectedRoute allowedRoles={['CITIZEN', 'NGO_WORKER', 'ADMIN']}><ChildProfilePage /></ProtectedRoute>} />
          <Route path="/children/:childId/continuity" element={<ProtectedRoute allowedRoles={['CITIZEN', 'NGO_WORKER', 'ADMIN']}><ContinuityPage /></ProtectedRoute>} />
          <Route path="/children/:childId/:service" element={<ProtectedRoute allowedRoles={['CITIZEN', 'NGO_WORKER', 'ADMIN']}><ChildServicePage /></ProtectedRoute>} />
          <Route path="/migration" element={<ProtectedRoute allowedRoles={['CITIZEN', 'NGO_WORKER', 'ADMIN']}><MigrationPage /></ProtectedRoute>} />
          <Route path="/help" element={<HelpPage />} />
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </>
  )
}