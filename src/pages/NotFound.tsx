import { Button } from '../components/common/Button'

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[60vh] max-w-4xl items-center justify-center px-4 py-20 text-center sm:px-6 lg:px-8">
      <div className="max-w-xl rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">404 Error</p>
        <h1 className="mt-4 text-5xl font-black tracking-tight text-slate-900">Page not found</h1>
        <p className="mt-4 text-base leading-7 text-slate-600">
          The page you are looking for does not exist, or it is part of a later development phase.
        </p>
        <div className="mt-8 flex justify-center">
          <Button to="/">Return Home</Button>
        </div>
      </div>
    </div>
  )
}
