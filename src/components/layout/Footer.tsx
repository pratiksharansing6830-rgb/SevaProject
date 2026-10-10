import { Link } from 'react-router-dom'

const platformLinks = [
  { label: 'About', to: '/about' },
  { label: 'Services', to: '/services' },
  { label: 'How It Works', to: '/how-it-works' },
]

const supportLinks = [
  { label: 'Help', to: '/help' },
]

const organizationLinks = [
  { label: 'Schools', to: '/services' },
  { label: 'NGOs', to: '/services' },
  { label: 'Healthcare', to: '/services' },
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
            A proof of concept for recording family support needs and coordinating continuity during migration. Directory listings do not confirm provider availability or service outcomes.
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

      </div>
    </footer>
  )
}
