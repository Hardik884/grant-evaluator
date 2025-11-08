import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Home } from './pages/Home';
import { Results } from './pages/Results';
import { Settings } from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-midnight-900 text-slate-100">
        <Navbar />

        <main className="pb-16 pt-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/results/:id" element={<Results />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
