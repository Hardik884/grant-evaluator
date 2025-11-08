import { Link, useLocation } from 'react-router-dom';
import { Sparkles, Settings, LayoutDashboard } from 'lucide-react';

export function Navbar() {
  const location = useLocation();

  const links = [
    { label: 'Evaluate', href: '/', icon: LayoutDashboard },
    { label: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <nav className="sticky top-4 z-40 px-4">
      <div className="mx-auto flex max-w-6xl items-center justify-between rounded-3xl border border-white/10 bg-surface-900/80 px-5 py-3 shadow-floating backdrop-blur-xl">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-primary text-white">
            <Sparkles className="h-5 w-5" />
          </div>
          <h1 className="text-lg font-semibold text-white">AI Grant Evaluator</h1>
        </Link>

        <div className="hidden items-center gap-2 md:flex">
          {links.map(({ label, href, icon: Icon }) => {
            const isActive = location.pathname === href;
            return (
              <Link
                key={href}
                to={href}
                className={`flex items-center gap-2 rounded-2xl px-4 py-2 text-sm font-medium transition-all duration-300 ${
                  isActive
                    ? 'bg-white/10 text-white shadow-glow-secondary'
                    : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </div>
        <div className="flex gap-1 md:hidden">
          {links.map(({ label, href }) => (
            <Link
              key={href}
              to={href}
              className={`rounded-2xl px-3 py-2 text-xs font-semibold transition-all ${
                location.pathname === href
                  ? 'bg-white/15 text-white'
                  : 'text-slate-300/90 hover:bg-white/10 hover:text-white'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
