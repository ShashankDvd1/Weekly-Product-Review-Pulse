import React, { useState } from 'react';
import { Smartphone, Sparkles, Code, ExternalLink, RefreshCw, AlertCircle, ShoppingBag, Eye, Heart, HelpCircle } from 'lucide-react';
import './MyPicksMVP.css';

const MyPicksMVP = () => {
  const [iframeKey, setIframeKey] = useState(0);

  const handleReload = () => {
    setIframeKey(prev => prev + 1);
  };

  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const prototypeUrl = isLocal 
    ? 'http://localhost:5175' 
    : window.location.origin + '/mypicks-mvp/index.html';

  return (
    <div className="mypicks-mvp-container">
      <div className="page-header">
        <div>
          <h1 className="page-title text-gradient">Myntra My Picks MVP</h1>
          <p className="page-subtitle">
            Interactive, mobile-first fashion-commerce prototype demonstrating the Intent-Aware Wishlist re-engagement model.
          </p>
        </div>
      </div>

      <div className="mypicks-grid">
        {/* Left Panel: Strategic Teardown & Specs */}
        <div className="strategy-panel glass-panel">
          <div className="panel-header">
            <Sparkles size={18} className="icon-pink" />
            <h3>Strategic Product Framework</h3>
          </div>

          <div className="panel-body">
            <section className="strategy-section">
              <h4>🎯 Core Hypothesis</h4>
              <p>
                Traditional Wishlists act as flat, dead repositories where products sit until users lose interest. 
                By introducing an **optional, explicit user-intent layer** at the moment of saving, we can segment users by 
                their motivation and dynamically trigger tailored reminders (e.g. price drops for bargain hunters, comparisons 
                for active shoppers) to raise 30-day Wishlist-to-Purchase conversion.
              </p>
            </section>

            <section className="strategy-section">
              <h4>🔥 The Four Core User Intents</h4>
              <div className="intent-grid">
                <div className="intent-card border-orange">
                  <h5>🔥 Buy Soon</h5>
                  <p>High-urgency shoppers who need a gentle nudge to checkout.</p>
                </div>
                <div className="intent-card border-blue">
                  <h5>💰 Waiting for Price</h5>
                  <p>Bargain hunters waiting for price drop notifications.</p>
                </div>
                <div className="intent-card border-purple">
                  <h5>👀 Comparing</h5>
                  <p>Undecided shoppers comparing specs, sizes, or aesthetics.</p>
                </div>
                <div className="intent-card border-green">
                  <h5>✨ Just Saving</h5>
                  <p>Low-urgency inspiration savers who shouldn't be spammed.</p>
                </div>
              </div>
            </section>

            <section className="strategy-section">
              <h4>📱 Walkthrough & Test Guide</h4>
              <ol className="walkthrough-list">
                <li>
                  <strong>Browse & Save:</strong> Tap on any clothing item or sneakers on the Home feed, then tap the Heart (♡) icon.
                </li>
                <li>
                  <strong>Assign Intent:</strong> The **Intent Bottom Sheet** will slide up. Tap <em>🔥 Buy Soon</em>.
                </li>
                <li>
                  <strong>Observe Re-entry:</strong> Return to the Home tab. A personalized <em>"Still thinking about this?"</em> card will dynamically surface to prompt conversion.
                </li>
                <li>
                  <strong>Verify Cache:</strong> Refresh your browser session; all wishlist states, cart items, and custom intents will remain intact via localStorage.
                </li>
              </ol>
            </section>

            <div className="quick-actions">
              <a 
                href={prototypeUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn btn-primary"
              >
                <ExternalLink size={14} /> Open Live in New Tab
              </a>
              <button onClick={handleReload} className="btn btn-secondary">
                <RefreshCw size={14} /> Reset Frame
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel: Simulated Phone Mockup */}
        <div className="phone-preview-panel">
          <div className="phone-wrapper">
            <div className="phone-earpiece"></div>
            <div className="phone-volume-btn volume-up"></div>
            <div className="phone-volume-btn volume-down"></div>
            <div className="phone-power-btn"></div>
            
            <div className="phone-screen">
              <iframe
                key={iframeKey}
                src={prototypeUrl}
                title="My Picks MVP Phone Preview"
                className="phone-iframe"
                onError={() => console.error("Failed to load iframe.")}
              />
            </div>
            
            <div className="phone-home-indicator"></div>
          </div>
          
          <p className="phone-helper-text">
            <Smartphone size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
            Fully interactive mobile-frame simulation
          </p>
        </div>
      </div>
    </div>
  );
};

export default MyPicksMVP;
