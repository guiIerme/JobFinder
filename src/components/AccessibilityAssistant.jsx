import React, { useState, useEffect } from 'react';
import '../styles/AccessibilityAssistant.css';

const AccessibilityAssistant = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLibrasActive, setIsLibrasActive] = useState(false);
  const [fontSize, setFontSize] = useState(100);
  const [contrastMode, setContrastMode] = useState('normal');

  // Load user preferences from localStorage
  useEffect(() => {
    const savedLibras = localStorage.getItem('librasActive') === 'true';
    const savedFontSize = localStorage.getItem('fontSize') || 100;
    const savedContrast = localStorage.getItem('contrastMode') || 'normal';
    
    setIsLibrasActive(savedLibras);
    setFontSize(parseInt(savedFontSize));
    setContrastMode(savedContrast);
    
    // Apply saved settings
    if (savedLibras) {
      loadLibrasWidget();
    }
    applyFontSize(parseInt(savedFontSize));
    applyContrastMode(savedContrast);
  }, []);

  // Save preferences when they change
  useEffect(() => {
    localStorage.setItem('librasActive', isLibrasActive.toString());
    localStorage.setItem('fontSize', fontSize.toString());
    localStorage.setItem('contrastMode', contrastMode);
  }, [isLibrasActive, fontSize, contrastMode]);

  const loadLibrasWidget = () => {
    // Check if widget is already loaded
    if (window.vLibras) return;

    // Create script element for VLibras widget
    const script = document.createElement('script');
    script.src = 'https://vlibras.gov.br/app/vlibras-plugin.js';
    script.async = true;
    script.onload = () => {
      new window.VLibras.Widget('https://vlibras.gov.br/app');
      window.vLibras = true;
    };
    document.head.appendChild(script);
  };

  const toggleLibras = () => {
    const newState = !isLibrasActive;
    setIsLibrasActive(newState);
    
    if (newState) {
      loadLibrasWidget();
    } else if (window.vLibrasWidget) {
      // Disable VLibras if it exists
      window.vLibrasWidget.destroy();
      window.vLibrasWidget = null;
    }
  };

  const increaseFontSize = () => {
    const newSize = Math.min(fontSize + 10, 150);
    setFontSize(newSize);
    applyFontSize(newSize);
  };

  const decreaseFontSize = () => {
    const newSize = Math.max(fontSize - 10, 80);
    setFontSize(newSize);
    applyFontSize(newSize);
  };

  const resetFontSize = () => {
    setFontSize(100);
    applyFontSize(100);
  };

  const applyFontSize = (size) => {
    document.documentElement.style.fontSize = `${size}%`;
  };

  const toggleContrast = () => {
    const modes = ['normal', 'high'];
    const currentIndex = modes.indexOf(contrastMode);
    const nextMode = modes[(currentIndex + 1) % modes.length];
    
    setContrastMode(nextMode);
    applyContrastMode(nextMode);
  };

  const applyContrastMode = (mode) => {
    document.body.classList.remove('high-contrast');
    if (mode === 'high') {
      document.body.classList.add('high-contrast');
    }
  };

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  // Toggle dark mode
  const toggleDarkMode = () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return (
    <>
      {/* Floating Accessibility Button */}
      <button 
        className="accessibility-toggle"
        onClick={toggleVisibility}
        aria-label="Abrir assistente de acessibilidade"
        title="Assistente de Acessibilidade"
      >
        <i className="fas fa-hands accessibility-icon"></i>
      </button>

      {/* Accessibility Panel */}
      {isVisible && (
        <div className="accessibility-panel">
          <div className="accessibility-header">
            <h3>Assistente de Acessibilidade</h3>
            <button 
              className="close-btn" 
              onClick={toggleVisibility}
              aria-label="Fechar painel de acessibilidade"
            >
              ×
            </button>
          </div>
          
          <div className="accessibility-options">
            {/* Libras Toggle */}
            <div className="option">
              <button 
                className={`toggle-btn ${isLibrasActive ? 'active' : ''}`}
                onClick={toggleLibras}
              >
                <i className="fas fa-sign-language option-icon"></i>
                <span className="option-text">Libras</span>
              </button>
              <p className="option-description">Ativar/Desativar tradução para Libras</p>
            </div>
            
            {/* Font Size Controls */}
            <div className="option">
              <div className="font-controls">
                <button 
                  className="control-btn"
                  onClick={decreaseFontSize}
                  aria-label="Diminuir tamanho da fonte"
                >
                  A-
                </button>
                <span className="font-size-display">{fontSize}%</span>
                <button 
                  className="control-btn"
                  onClick={increaseFontSize}
                  aria-label="Aumentar tamanho da fonte"
                >
                  A+
                </button>
                <button 
                  className="reset-btn"
                  onClick={resetFontSize}
                  aria-label="Redefinir tamanho da fonte"
                >
                  Redefinir
                </button>
              </div>
              <p className="option-description">Ajustar tamanho do texto</p>
            </div>
            
            {/* Contrast Toggle */}
            <div className="option">
              <button 
                className={`toggle-btn ${contrastMode === 'high' ? 'active' : ''}`}
                onClick={toggleContrast}
              >
                <i className="fas fa-adjust option-icon"></i>
                <span className="option-text">
                  {contrastMode === 'high' ? 'Alto Contraste Ativado' : 'Alto Contraste'}
                </span>
              </button>
              <p className="option-description">Alternar modo de alto contraste</p>
            </div>
            
            {/* Dark Mode Toggle */}
            <div className="option">
              <button 
                className="toggle-btn"
                onClick={toggleDarkMode}
              >
                <i className="fas fa-moon option-icon"></i>
                <span className="option-text">Modo Escuro</span>
              </button>
              <p className="option-description">Alternar entre modo claro e escuro</p>
            </div>
            
            {/* Text Reader */}
            <div className="option">
              <button className="toggle-btn">
                <i className="fas fa-volume-up option-icon"></i>
                <span className="option-text">Leitor de Texto</span>
              </button>
              <p className="option-description">Ouvir o conteúdo da página</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AccessibilityAssistant;