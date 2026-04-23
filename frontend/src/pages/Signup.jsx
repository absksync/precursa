import { SignUp } from '@clerk/clerk-react'
import { Link } from 'react-router-dom'

export default function Signup() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_#1f355d_0%,_#070b14_46%,_#05070c_100%)] px-4 py-10">
      <div className="w-full max-w-md rounded-3xl border border-white/20 bg-white/10 p-6 shadow-[0_24px_80px_rgba(0,0,0,0.55)] backdrop-blur-xl">
        <p className="text-xs uppercase tracking-[0.22em] text-sky-200/90">Precursa Secure Access</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Create your account</h1>
        <p className="mt-2 text-sm text-slate-300">Set up your credentials to unlock the dashboard.</p>

        <div className="mt-6 overflow-hidden rounded-2xl border border-white/20 bg-black/20 p-2">
          <SignUp routing="path" path="/sign-up" signInUrl="/sign-in" afterSignUpUrl="/" />
        </div>

        <p className="mt-4 text-center text-sm text-slate-300">
          Already have an account?{' '}
          <Link to="/sign-in" className="font-medium text-sky-300 hover:text-sky-200">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  )
}
