import { Button, Container } from '@mantine/core';
import { useNavigate } from 'react-router';
import { useState, useEffect, useRef } from 'react';

export default function Home() {
  const navigate = useNavigate();
  const [showPacman, setShowPacman] = useState(false);
  const [eatenPellets, setEatenPellets] = useState([false, false, false, false, false]);
  const pacmanRef = useRef(null);
  const pelletsRef = useRef([]);

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
      {/* Content first so it appears above the background */}
      <div className="home-content">
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