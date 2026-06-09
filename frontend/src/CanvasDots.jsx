import React, { useEffect, useRef } from 'react';

const CanvasDots = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    let mouse = { x: -1000, y: -1000 };

    const handleMouseMove = (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };
    
    const handleMouseLeave = () => {
      mouse.x = -1000;
      mouse.y = -1000;
    };

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      initDots();
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseout', handleMouseLeave);
    window.addEventListener('resize', handleResize);

    const dots = [];
    const spacing = 30; // Grid spacing between dots

    function initDots() {
      dots.length = 0;
      // Add a little padding to the grid so edges don't look empty
      for (let x = -50; x < width + 50; x += spacing) {
        for (let y = -50; y < height + 50; y += spacing) {
          dots.push({
            ox: x,
            oy: y,
            x: x,
            y: y
          });
        }
      }
    }

    initDots();

    // Interaction radius
    const radius = 120; 

    let animationFrameId;

    function animate() {
      // Fill background to ensure it is visible and not hidden by body background
      ctx.fillStyle = '#0b0f19'; // Deep dark background
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle = 'rgba(255, 255, 255, 0.25)'; // Bright dots

      for (let i = 0; i < dots.length; i++) {
        const dot = dots[i];
        
        // Calculate distance to mouse
        const dx = mouse.x - dot.ox;
        const dy = mouse.y - dot.oy;
        const dist = Math.sqrt(dx * dx + dy * dy);

        // Bubble effect: push away from cursor
        if (dist < radius) {
          const force = (radius - dist) / radius;
          const angle = Math.atan2(dy, dx);
          // Push away up to 40 pixels
          const targetX = dot.ox - Math.cos(angle) * force * 40;
          const targetY = dot.oy - Math.sin(angle) * force * 40;
          
          dot.x += (targetX - dot.x) * 0.15;
          dot.y += (targetY - dot.y) * 0.15;
        } else {
          // Return smoothly to original position
          dot.x += (dot.ox - dot.x) * 0.1;
          dot.y += (dot.oy - dot.y) * 0.1;
        }

        ctx.beginPath();
        ctx.arc(dot.x, dot.y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(animate);
    }

    animate();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseout', handleMouseLeave);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas 
      ref={canvasRef} 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: -1
      }}
    />
  );
};

export default CanvasDots;
