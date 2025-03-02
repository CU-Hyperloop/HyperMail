import { Button, Container } from '@mantine/core';
import { useNavigate } from 'react-router';
import { useState, useEffect, useRef } from 'react';
import '../styles/Home.css';

export default function Home() {
  const navigate = useNavigate();
  const [ghosts, setGhosts] = useState([
    { id: 'blinky', x: 80, y: 10, color: '#FF0000' },
    { id: 'pinky', x: 80, y: 30, color: '#FFB8FF' },
    { id: 'inky', x: 10, y: 70, color: '#00FFFF' },
    { id: 'clyde', x: 10, y: 90, color: '#FFB852' }
  ]);
  
  const [showPacman, setShowPacman] = useState(false);
  const [eatenPellets, setEatenPellets] = useState([false, false, false, false, false]);
  const pacmanRef = useRef(null);
  const pelletsRef = useRef([]);

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

  // Check for pellet collisions as Pacman moves
  useEffect(() => {
    if (!showPacman) return;

    let animationId;
    const checkCollisions = () => {
      if (!pacmanRef.current) return;
      
      const pacmanRect = pacmanRef.current.getBoundingClientRect();
      const pacmanRight = pacmanRect.right;
      
      // Check each pellet
      pelletsRef.current.forEach((pellet, index) => {
        if (!pellet || eatenPellets[index]) return;
        
        const pelletRect = pellet.getBoundingClientRect();
        // If Pacman's right edge passes the pellet's center
        if (pacmanRight >= pelletRect.left + (pelletRect.width / 2)) {
          setEatenPellets(prev => {
            const updated = [...prev];
            updated[index] = true;
            return updated;
          });
        }
      });
      
      animationId = requestAnimationFrame(checkCollisions);
    };
    
    animationId = requestAnimationFrame(checkCollisions);
    return () => cancelAnimationFrame(animationId);
  }, [showPacman, eatenPellets]);

  const handleButtonClick = () => {
    console.log("Button clicked, showing Pac-Man");
    setShowPacman(true);
    setEatenPellets([false, false, false, false, false]);
    
    // Navigate after the Pac-Man animation completes
    setTimeout(() => {
      navigate('/generate');
    }, 3000); // 3 seconds delay to show animation
  };

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
        
        <Button 
          size="lg"
          className="start-button"
          onClick={handleButtonClick}
        >
          USE NOW
        </Button>
      </div>

      {/* Pac-Man Animation with static pellets */}
      {showPacman && (
        <div className="pacman-animation">
          <div className="pacman-container">
            <div 
              ref={pacmanRef} 
              className="pacman-character"
            >
              <div className="pacman-eye"></div>
              <div className="pacman-mouth"></div>
            </div>
            
            {/* Static pellets across the screen */}
            <div 
              ref={el => pelletsRef.current[0] = el}
              className={`pacman-pellet ${eatenPellets[0] ? 'eaten' : ''}`}
              style={{ left: '20%' }}
            ></div>
            <div 
              ref={el => pelletsRef.current[1] = el}
              className={`pacman-pellet ${eatenPellets[1] ? 'eaten' : ''}`}
              style={{ left: '35%' }}
            ></div>
            <div 
              ref={el => pelletsRef.current[2] = el}
              className={`pacman-pellet ${eatenPellets[2] ? 'eaten' : ''}`}
              style={{ left: '50%' }}
            ></div>
            <div 
              ref={el => pelletsRef.current[3] = el}
              className={`pacman-pellet ${eatenPellets[3] ? 'eaten' : ''}`}
              style={{ left: '65%' }}
            ></div>
            <div 
              ref={el => pelletsRef.current[4] = el}
              className={`pacman-pellet ${eatenPellets[4] ? 'eaten' : ''}`}
              style={{ left: '80%' }}
            ></div>
          </div>
        </div>
      )}
    </Container>
  );
}