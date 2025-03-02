import '@mantine/core/styles.css';
import { MantineProvider, createTheme } from '@mantine/core';
import { BrowserRouter as Router, Route, Routes } from 'react-router';

// Import the global theme CSS
import './styles/GlobalTheme.css';

// Import pages
import Home from './pages/Home';
import EmailGenerator from './pages/EmailGenerator';
import DraftMail from './pages/Dashboard';
import Test from './pages/test';
import Dashboard from './pages/Dashboard';
import EmailDash from './pages/EmailDash';

// Create a custom Mantine theme to complement our CSS theme
const pacmanTheme = createTheme({
  primaryColor: 'yellow',
  colors: {
    yellow: [
      '#FFF8C4', // 0
      '#FFEE99', // 1
      '#FFE566', // 2
      '#FFD700', // 3 - Our Pac-Man yellow
      '#E6C200', // 4
      '#CCB100', // 5
      '#B29900', // 6
      '#998300', // 7
      '#806E00', // 8
      '#665800', // 9
    ],
    blue: [
      '#E6F7FF', // 0
      '#BAE3FF', // 1
      '#7CC4FA', // 2
      '#4AA5F5', // 3
      '#2887EC', // 4
      '#2121DE', // 5 - Our Pac-Man blue
      '#1457C5', // 6
      '#10449E', // 7
      '#0C3078', // 8
      '#071F52', // 9
    ],
  },
  fontFamily: 'Arial, sans-serif',
  headings: {
    fontFamily: '"Press Start 2P", cursive',
  },
  components: {
    Button: {
      defaultProps: {
        color: 'blue.5',
      },
    },
  },
});

// Background component for the maze and ghosts
function PacmanBackground() {
  return (
    <div className="maze-background">
      <div className="dots">
        {Array.from({ length: 100 }).map((_, i) => (
          <div key={i} className="dot"></div>
        ))}
      </div>
      <div className="game-characters">
        <div className="ghost" style={{ left: '5%', top: '20%', backgroundColor: '#FF0000' }}>
          <div className="ghost-eyes">
            <div className="eye"></div>
            <div className="eye"></div>
          </div>
          <div className="ghost-skirt"></div>
        </div>
        <div className="ghost" style={{ left: '85%', top: '15%', backgroundColor: '#FFB8FF' }}>
          <div className="ghost-eyes">
            <div className="eye"></div>
            <div className="eye"></div>
          </div>
          <div className="ghost-skirt"></div>
        </div>
        <div className="ghost" style={{ left: '15%', top: '75%', backgroundColor: '#00FFFF' }}>
          <div className="ghost-eyes">
            <div className="eye"></div>
            <div className="eye"></div>
          </div>
          <div className="ghost-skirt"></div>
        </div>
        <div className="ghost" style={{ left: '80%', top: '80%', backgroundColor: '#FFB852' }}>
          <div className="ghost-eyes">
            <div className="eye"></div>
            <div className="eye"></div>
          </div>
          <div className="ghost-skirt"></div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <MantineProvider theme={pacmanTheme}>
      {/* Global Pac-Man background */}
      <PacmanBackground />

      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/generate" element={<EmailGenerator />} />
          <Route path="/draft" element={<DraftMail />} />
          <Route path="/test" element={<Test />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/email-dash" element={<EmailDash />} />
        </Routes>
      </Router>
    </MantineProvider>
  );
}