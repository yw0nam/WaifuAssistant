import React from 'react';
import Chat from './components/Chat';
import './App.css';

function App() {
  return (
    <div className="App">
      <Chat websocketUrl="ws://localhost:8800" />
    </div>
  );
}

export default App;
