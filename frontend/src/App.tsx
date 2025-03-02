import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import {BrowserRouter as Router, Route, Routes,  } from 'react-router';


import Home from './pages/Home';
import EmailGenerator from './pages/EmailGenerator';
import DraftMail from './pages/Dashboard';
import Test from './pages/test';
import Dashboard from './pages/Dashboard';
export default function App() {
  return (
  <MantineProvider>

    <Router>
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/generate" element={<EmailGenerator/>}/>
        <Route path="/draft" element={<DraftMail/>}/>
        <Route path="/test" element={<Test/>}/>
        <Route path="/dashboard" element={<Dashboard/>}/>
      </Routes>
    </Router>
  </MantineProvider>
  
);
}
