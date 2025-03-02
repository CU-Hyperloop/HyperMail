import { Container, Title } from '@mantine/core';
import Form from '../components/Form';
import { useState, useEffect } from 'react';
import '../styles/EmailGenerator.css';

export default function EmailGenerator() {
  const [ghosts, setGhosts] = useState([
    // Left side ghosts
    { id: 'blinky', x: 5, y: 20, color: '#FF0000', direction: 1, speed: 0.6 },
    { id: 'pinky', x: 5, y: 60, color: '#FFB8FF', direction: -1, speed: 0.4 },
    // Right side ghosts
    { id: 'inky', x: 95, y: 30, color: '#00FFFF', direction: 1, speed: 0.5 },
    { id: 'clyde', x: 95, y: 70, color: '#FFB852', direction: -1, speed: 0.3 }
  ]);

  // Animate ghosts vertically
  useEffect(() => {
    const interval = setInterval(() => {
      // Move ghosts vertically
      setGhosts(prev => 
        prev.map(ghost => {
          // Calculate new position
          let newY = ghost.y + (ghost.direction * ghost.speed);
          
          // Reverse direction if reaching the edges
          let newDirection = ghost.direction;
          if (newY > 90 || newY < 10) {
            newDirection = -ghost.direction;
            newY = ghost.y + (newDirection * ghost.speed); // Apply new direction immediately
          }
          
          return {
            ...ghost,
            y: newY,
            direction: newDirection
          };
        })
      );
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <Container className='email-generator-container arcade-theme'>
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
        <h1 className="arcade-title">EMAIL GENERATOR</h1>
        
        <div className="form-container">
          <Form />
        </div>
      </div>
    </Container>
  );
};