
import { useState, useEffect } from "react";
import ChatInterface from "./components/ChatInterface";
import { BrainIcon, SunIcon, MoonIcon } from "./components/Icons";
import "./App.css";

function App() {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="app">
      <header className="header">
        <h1 className="header-title">
          <BrainIcon size={24} />
          ContextBase AI
        </h1>
        <button 
          className="theme-toggle" 
          onClick={toggleTheme}
          aria-label="Toggle theme"
        >
          {theme === 'light' ? <MoonIcon size={20} /> : <SunIcon size={20} />}
        </button>
      </header>

      <main className="content">
        <ChatInterface />
      </main>
    </div>
  );
}

export default App;