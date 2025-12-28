import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Header from './components/Header';
import Home from './pages/Home';
import VideoPlayer from './pages/VideoPlayer';
import Upload from './pages/Upload';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import CreatorDashboard from './pages/CreatorDashboard';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Header />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/video/:id" element={<VideoPlayer />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/dashboard" element={<CreatorDashboard />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
