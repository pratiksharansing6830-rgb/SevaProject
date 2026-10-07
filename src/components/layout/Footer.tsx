import { Link } from 'react-router-dom'

const platformLinks = [
  { label: 'About', to: '/about' },
  { label: 'Services', to: '/services' },
  { label: 'How It Works', to: '/how-it-works' },
]

const supportLinks = [
  { label: 'Help', to: '/help' },
  { label: 'Contact', to: '/help' },
  { label: 'Accessibility', to: '/help' },
]

const organizationLinks = [
  { label: 'Schools', to: '/services' },
  { label: 'NGOs', to: '/services' },
  { label: 'Healthcare', to: '/services' },
]

const legalLinks = [
  { label: 'Privacy', to: '/help' },
  { label: 'Terms', to: '/help' },
  { label: 'Data Protection', to: '/help' },
]

export function Footer() {
  return (
    <footer className="mt-16 border-t border-slate-200 bg-slate-950 text-slate-200">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-5 lg:px-8">
        <div className="lg:col-span-2">
          <Link to="/" className="text-xl font-bold tracking-tight text-white">
            Sahaayak
          </Link>
          <p className="mt-4 max-w-md text-sm leading-6 text-slate-300">
            A prototype platform for academic and demonstration purposes, designed to help children maintain continuity of support during intra-state migration.
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Platform</h3>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            {platformLinks.map((link) => (
              <li key={link.label}>
                <Link to={link.to} className="hover:text-white">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Support</h3>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            {supportLinks.map((link) => (
              <li key={link.label}>
                <Link to={link.to} className="hover:text-white">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">For Organizations</h3>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            {organizationLinks.map((link) => (
              <li key={link.label}>
                <Link to={link.to} className="hover:text-white">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Legal</h3>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            {legalLinks.map((link) => (
              <li key={link.label}>
                <Link to={link.to} className="hover:text-white">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="border-t border-slate-800">
        <div className="mx-auto max-w-7xl px-4 py-6 text-sm text-slate-400 sm:px-6 lg:px-8">
          Prototype platform for academic and demonstration purposes.
        </div>
      </div>
    </footer>
  )
}
