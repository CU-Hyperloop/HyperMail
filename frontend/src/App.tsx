import '@mantine/core/styles.css';

import { MantineProvider } from '@mantine/core';
import {BrowserRouter as Router, Route, Routes,  } from 'react-router';

export default function App() {
  return (
  <MantineProvider>

    <Router>
      <Routes>
        <Route path="/" element={<div>hello hypermail !!!</div>} />
      </Routes>
    </Router>
    
  </MantineProvider>
  
);
}
