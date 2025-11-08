import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className = '', hover = false }: CardProps) {
  return (
    <div
      className={`card-premium p-6 sm:p-8 transition-all duration-300 ${
        hover ? 'hover:-translate-y-1 hover:shadow-floating' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
}
