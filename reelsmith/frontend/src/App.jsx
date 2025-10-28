import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from './pages/Home';
import UploadReel from './pages/UploadReel';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white">
        <nav className="bg-gray-800 p-4">
          <ul className="flex space-x-4">
            <li>
              <Link to="/" className="hover:text-gray-300">Home</Link>
            </li>
            <li>
              <Link to="/upload" className="hover:text-gray-300">Upload Reel</Link>
            </li>
          </ul>
        </nav>
        <main className="p-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<UploadReel />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
