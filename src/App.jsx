import React from 'react';
import AdminDashboard from './components/AdminDashboard';
import AccessibilityAssistant from './components/AccessibilityAssistant';
import './styles/AdminDashboard.css';

function App() {
  return (
    <div className="App">
      <AdminDashboard />
      <AccessibilityAssistant />
    </div>
  );
}

export default App;