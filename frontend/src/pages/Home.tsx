import { Button, Container } from '@mantine/core';
import { Link } from 'react-router';
import { useState, useEffect } from 'react';
import '../styles/Home.css';

export default function Home() {
  const [ghosts, setGhosts] = useState([
    { id: 'blinky', x: 80, y: 20, color: '#FF0000' },
    { id: 'pinky', x: 80, y: 40, color: '#FFB8FF' },
    { id: 'inky', x: 10, y: 60, color: '#00FFFF' },
    { id: 'clyde', x: 10, y: 80, color: '#FFB852' }
  ]);

  // Animate ghosts
  useEffect(() => {
    const interval = setInterval(() => {
      // Move ghosts
      setGhosts(prev => 
        prev.map(ghost => {
          // Determine direction based on current position
          const moveRight = ghost.x < 10;
          const moveLeft = ghost.x > 80;
          
          // Calculate new position
          let newX = ghost.x;
          if (moveRight) newX += 0.5;
          else if (moveLeft) newX -= 0.5;
          else newX += ghost.id === 'blinky' || ghost.id === 'pinky' ? -0.5 : 0.5;
          
          return {
            ...ghost,
            x: newX,
            y: ghost.y + (Math.random() - 0.5) * 1 // Slight random y movement
          };
        })
      );
    }, 150);

    return () => clearInterval(interval);
  }, []);

  return (
    <Container className='home-container arcade-theme'>
      <div className="maze">
        <div className="dots">
          {Array.from({ length: 30 }).map((_, i) => (
            <div key={i} className="dot"></div>
          ))}
        </div>
        
        <div className="game-characters">
          {/* Ghosts */}
          {ghosts.map(ghost => (
            <div 
              key={ghost.id}
              className="ghost"
              style={{ 
                left: `${ghost.x}%`, 
                top: `${ghost.y}%`,
                backgroundColor: ghost.color 
              }}
            >
              <div className="ghost-eyes">
                <div className="eye"></div>
                <div className="eye"></div>
              </div>
              <div className="ghost-skirt"></div>
            </div>
          ))}
        </div>
      </div>

      <div className="content">
        <h1 className="arcade-title">HYPERMAIL</h1>
        <div className="arcade-subtitle">AI SALES AGENT</div>
        
        <Button component={Link} to="/generate" size="lg" className="start-button">
          USE NOW
        </Button>
      </div>
    </Container>
  );
};