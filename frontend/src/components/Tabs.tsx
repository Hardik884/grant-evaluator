import { ReactNode, useState } from 'react';

interface Tab {
  id: string;
  label: string;
  content: ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
}

export function Tabs({ tabs, defaultTab }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  const activeContent = tabs.find(tab => tab.id === activeTab)?.content;

  return (
    <div className="w-full">
      <div className="mb-6 flex gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-white/5 p-1 backdrop-blur-xl">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`min-w-fit flex-1 rounded-2xl px-6 py-3 text-sm font-semibold transition-all duration-300 ${
              activeTab === tab.id
                ? 'bg-gradient-primary text-white shadow-glow-primary'
                : 'text-slate-300 hover:bg-white/10 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="animate-fade-in">
        {activeContent}
      </div>
    </div>
  );
}
