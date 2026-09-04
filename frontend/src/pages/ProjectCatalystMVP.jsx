import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Heart, 
  Check, 
  ShoppingBag, 
  RotateCcw, 
  ShieldCheck, 
  Star, 
  Truck, 
  ArrowRight, 
  Database, 
  Search, 
  Camera, 
  Mic, 
  Bell, 
  SlidersHorizontal, 
  ChevronRight, 
  Zap, 
  Tag, 
  Clock, 
  CheckCircle2, 
  X, 
  Share2, 
  RefreshCw, 
  Percent, 
  Gift, 
  Plus, 
  Minus, 
  MapPin, 
  CheckCheck,
  Grid,
  Filter
} from 'lucide-react';
import './ProjectCatalystMVP.css';

// 16+ Curated High-Fidelity Myntra Fashion Products
const ALL_PRODUCTS = [
  {
    id: 'shirt-1',
    brand: 'HIGHLANDER',
    title: 'Men Olive Relaxed Fit Cotton Casual Shirt',
    price: 1299,
    mrp: 2599,
    discount: '50% OFF',
    rating: '4.3',
    ratingCount: '2.4k',
    inferredSize: 'M',
    sizes: ['S', 'M', 'L', 'XL'],
    fitConsensus: '85% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=600&q=80',
    tag: 'BESTSELLER',
    category: 'Shirts',
    gender: 'Men'
  },
  {
    id: 'jacket-1',
    brand: 'WROGN',
    title: 'Men Washed Slim Fit Denim Biker Jacket',
    price: 1299,
    mrp: 2799,
    discount: '54% OFF',
    rating: '4.5',
    ratingCount: '1.8k',
    inferredSize: 'L',
    sizes: ['M', 'L', 'XL', 'XXL'],
    fitConsensus: '90% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=600&q=80',
    tag: 'TRENDING',
    category: 'Jackets',
    gender: 'Men'
  },
  {
    id: 'tshirt-1',
    brand: 'ROADSTER',
    title: 'Men Pure Cotton Vintage Graphic T-Shirt',
    price: 599,
    mrp: 1199,
    discount: '50% OFF',
    rating: '4.2',
    ratingCount: '5.1k',
    inferredSize: 'M',
    sizes: ['S', 'M', 'L', 'XL'],
    fitConsensus: '88% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80',
    tag: 'POPULAR',
    category: 'T-Shirts',
    gender: 'Men'
  },
  {
    id: 'shoes-1',
    brand: 'NIKE',
    title: 'Men Air Max Alpha Training Sneakers',
    price: 3495,
    mrp: 6995,
    discount: '50% OFF',
    rating: '4.7',
    ratingCount: '920',
    inferredSize: 'UK 9',
    sizes: ['UK 7', 'UK 8', 'UK 9', 'UK 10', 'UK 11'],
    fitConsensus: '92% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80',
    tag: 'PREMIUM',
    category: 'Footwear',
    gender: 'Men'
  },
  {
    id: 'jeans-1',
    brand: "LEVI'S",
    title: '511 Slim Fit Mid-Rise Stretchable Jeans',
    price: 2199,
    mrp: 3999,
    discount: '45% OFF',
    rating: '4.6',
    ratingCount: '3.8k',
    inferredSize: '32',
    sizes: ['30', '32', '34', '36'],
    fitConsensus: '94% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=600&q=80',
    tag: 'ICONIC',
    category: 'Jeans',
    gender: 'Men'
  },
  {
    id: 'hoodie-1',
    brand: 'ZARA',
    title: 'Men Oversized Heavyweight Boxy Hoodie',
    price: 2290,
    mrp: 3590,
    discount: '36% OFF',
    rating: '4.4',
    ratingCount: '1.2k',
    inferredSize: 'L',
    sizes: ['S', 'M', 'L', 'XL'],
    fitConsensus: '82% say Runs Slightly Loose',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=600&q=80',
    tag: 'HOT DEAL',
    category: 'Jackets',
    gender: 'Men'
  },
  {
    id: 'polo-1',
    brand: 'TOMMY HILFIGER',
    title: 'Men Classic Striped Pique Polo T-Shirt',
    price: 1999,
    mrp: 3999,
    discount: '50% OFF',
    rating: '4.5',
    ratingCount: '890',
    inferredSize: 'M',
    sizes: ['S', 'M', 'L', 'XL'],
    fitConsensus: '91% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?auto=format&fit=crop&w=600&q=80',
    tag: 'CLASSIC',
    category: 'T-Shirts',
    gender: 'Men'
  },
  {
    id: 'sneaker-2',
    brand: 'ADIDAS',
    title: 'Originals Stan Smith Classic Leather Sneakers',
    price: 3999,
    mrp: 6999,
    discount: '43% OFF',
    rating: '4.8',
    ratingCount: '4.5k',
    inferredSize: 'UK 8',
    sizes: ['UK 7', 'UK 8', 'UK 9', 'UK 10'],
    fitConsensus: '95% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=600&q=80',
    tag: 'BESTSELLER',
    category: 'Footwear',
    gender: 'Unisex'
  },
  {
    id: 'shirt-2',
    brand: 'JACK & JONES',
    title: 'Men Slim Fit Checked Cotton Casual Shirt',
    price: 1199,
    mrp: 2499,
    discount: '52% OFF',
    rating: '4.3',
    ratingCount: '1.6k',
    inferredSize: 'M',
    sizes: ['S', 'M', 'L', 'XL'],
    fitConsensus: '87% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=600&q=80',
    tag: 'NEW',
    category: 'Shirts',
    gender: 'Men'
  },
  {
    id: 'dress-1',
    brand: 'VERO MODA',
    title: 'Women Floral Print Tiered A-Line Midi Dress',
    price: 2199,
    mrp: 4499,
    discount: '51% OFF',
    rating: '4.5',
    ratingCount: '2.1k',
    inferredSize: 'S',
    sizes: ['XS', 'S', 'M', 'L'],
    fitConsensus: '89% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=600&q=80',
    tag: 'TRENDING',
    category: 'Women',
    gender: 'Women'
  },
  {
    id: 'cargo-1',
    brand: 'ONLY',
    title: 'Women High-Rise Wide-Leg Relaxed Cargo Trousers',
    price: 1799,
    mrp: 3299,
    discount: '45% OFF',
    rating: '4.4',
    ratingCount: '1.4k',
    inferredSize: '28',
    sizes: ['26', '28', '30', '32'],
    fitConsensus: '86% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=600&q=80',
    tag: 'POPULAR',
    category: 'Women',
    gender: 'Women'
  },
  {
    id: 'shirt-3',
    brand: 'MANGO',
    title: 'Women Solid Pure Cotton Oversized Casual Shirt',
    price: 1490,
    mrp: 2990,
    discount: '50% OFF',
    rating: '4.6',
    ratingCount: '980',
    inferredSize: 'M',
    sizes: ['XS', 'S', 'M', 'L'],
    fitConsensus: '93% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1598554747436-c9293d6a588f?auto=format&fit=crop&w=600&q=80',
    tag: 'ELEGANT',
    category: 'Women',
    gender: 'Women'
  },
  {
    id: 'track-1',
    brand: 'HRX by Hrithik Roshan',
    title: 'Men Active Rapid-Dry Training Joggers',
    price: 899,
    mrp: 1999,
    discount: '55% OFF',
    rating: '4.3',
    ratingCount: '7.2k',
    inferredSize: 'L',
    sizes: ['S', 'M', 'L', 'XL'],
    fitConsensus: '88% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1552902865-b72c031ac5ea?auto=format&fit=crop&w=600&q=80',
    tag: 'ACTIVEWEAR',
    category: 'Jeans',
    gender: 'Men'
  },
  {
    id: 'sneaker-3',
    brand: 'PUMA',
    title: 'Unisex Rebound V6 High-Top Leather Sneakers',
    price: 2899,
    mrp: 5499,
    discount: '47% OFF',
    rating: '4.5',
    ratingCount: '3.1k',
    inferredSize: 'UK 9',
    sizes: ['UK 7', 'UK 8', 'UK 9', 'UK 10'],
    fitConsensus: '90% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=600&q=80',
    tag: 'HOT DEAL',
    category: 'Footwear',
    gender: 'Unisex'
  },
  {
    id: 'polo-2',
    brand: 'US POLO ASSN',
    title: 'Men Solid Slim Fit Cotton Pique Polo',
    price: 1099,
    mrp: 2199,
    discount: '50% OFF',
    rating: '4.4',
    ratingCount: '4.2k',
    inferredSize: 'M',
    sizes: ['S', 'M', 'L', 'XL', 'XXL'],
    fitConsensus: '89% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1625910513413-562a1290c00a?auto=format&fit=crop&w=600&q=80',
    tag: 'CLASSIC',
    category: 'T-Shirts',
    gender: 'Men'
  },
  {
    id: 'jacket-2',
    brand: 'DIESEL',
    title: 'Men Regular Fit Premium Cotton Trucker Jacket',
    price: 4599,
    mrp: 8999,
    discount: '49% OFF',
    rating: '4.8',
    ratingCount: '620',
    inferredSize: 'L',
    sizes: ['M', 'L', 'XL'],
    fitConsensus: '94% say True to Size',
    returns: '14-Day Easy Returns',
    image: 'https://images.unsplash.com/photo-1495105787522-5334e3ffa0ef?auto=format&fit=crop&w=600&q=80',
    tag: 'LUXURY',
    category: 'Jackets',
    gender: 'Men'
  }
];

const CATEGORIES_DATA = [
  { 
    id: 'men', 
    name: 'Men', 
    icon: '👔', 
    count: '85,000+ Items',
    banner: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80',
    subcategories: ['Shirts', 'Jackets', 'T-Shirts', 'Jeans', 'Footwear'] 
  },
  { 
    id: 'women', 
    name: 'Women', 
    icon: '👗', 
    count: '120,000+ Items',
    banner: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80',
    subcategories: ['Women', 'Dresses', 'Tops', 'Trousers', 'Footwear'] 
  },
  { 
    id: 'footwear', 
    name: 'Footwear', 
    icon: '👟', 
    count: '34,000+ Items',
    banner: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=400&q=80',
    subcategories: ['Footwear', 'Sneakers', 'Casual Shoes', 'Training Shoes'] 
  },
  { 
    id: 'casuals', 
    name: 'Casuals', 
    icon: '👕', 
    count: '62,000+ Items',
    banner: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=400&q=80',
    subcategories: ['Shirts', 'T-Shirts', 'Jeans'] 
  },
  { 
    id: 'deals', 
    name: 'Deals Hub', 
    icon: '🔥', 
    count: 'Flat 50-80% OFF',
    banner: 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&w=400&q=80',
    subcategories: ['All', 'BESTSELLER', 'TRENDING', 'HOT DEAL'] 
  }
];

const FILTER_PILLS = ['All', 'Shirts', 'Jackets', 'T-Shirts', 'Jeans', 'Footwear', 'Women'];

const ProjectCatalystMVP = () => {
  // Navigation & UI state
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'categories' | 'wishlist' | 'bag'
  const [selectedFilter, setSelectedFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProductForPDP, setSelectedProductForPDP] = useState(null);
  const [pdpSelectedSize, setPdpSelectedSize] = useState('M');
  const [orderPlacedSuccess, setOrderPlacedSuccess] = useState(false);
  const [selectedCategoryTab, setSelectedCategoryTab] = useState('men');

  // Interactive edge case states
  const [pincode, setPincode] = useState('560034');
  const [pincodeModalOpen, setPincodeModalOpen] = useState(false);
  const [tempPincode, setTempPincode] = useState('560034');
  const [couponApplied, setCouponApplied] = useState(false);

  // Prototype state simulating Zustand client-side store
  const [wishlist, setWishlist] = useState({}); // { [productId]: { size: 'M', savedAt: string } }
  const [bagItems, setBagItems] = useState([
    {
      id: 'jacket-1',
      brand: 'WROGN',
      title: 'Men Washed Slim Fit Denim Biker Jacket',
      size: 'L',
      price: 1299,
      mrp: 2799,
      image: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=600&q=80',
      quantity: 1
    }
  ]);

  // Toast feedback
  const [toastMessage, setToastMessage] = useState('');
  const [toastVisible, setToastVisible] = useState(false);

  // Telemetry log for strategy panel
  const [telemetryLogs, setTelemetryLogs] = useState([]);

  const FREE_DELIVERY_THRESHOLD = 2500;
  
  // Calculate cart math
  const rawSubtotal = bagItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
  const couponDiscount = couponApplied ? 200 : 0;
  const bagSubtotal = Math.max(0, rawSubtotal - couponDiscount);
  const isFreeDeliveryUnlocked = bagSubtotal >= FREE_DELIVERY_THRESHOLD;
  const deliveryFee = (bagItems.length === 0 || isFreeDeliveryUnlocked) ? 0 : 99;
  const totalMrp = bagItems.reduce((acc, item) => acc + (item.mrp * item.quantity), 0);
  const totalDiscount = (totalMrp - rawSubtotal) + couponDiscount;
  const finalTotal = bagSubtotal + deliveryFee;

  // Filtered Products for Home Feed
  const filteredProducts = ALL_PRODUCTS.filter(prod => {
    const matchesFilter = selectedFilter === 'All' 
      ? true 
      : (prod.category === selectedFilter || prod.gender === selectedFilter || prod.tag === selectedFilter);
    const matchesSearch = searchQuery.trim() === '' 
      ? true 
      : (prod.brand.toLowerCase().includes(searchQuery.toLowerCase()) || 
         prod.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
         prod.category.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  const showToast = (msg) => {
    setToastMessage(msg);
    setToastVisible(true);
    setTimeout(() => {
      setToastVisible(false);
    }, 2400);
  };

  const logTelemetry = (event, payload) => {
    const entry = {
      timestamp: new Date().toLocaleTimeString(),
      event,
      payload
    };
    setTelemetryLogs(prev => [entry, ...prev.slice(0, 5)]);
  };

  // Step 1: Implicit Wishlist Save
  const handleToggleWishlist = (product, sizeOverride = null) => {
    const isAlreadySaved = !!wishlist[product.id];
    const targetSize = sizeOverride || product.inferredSize || 'M';

    if (!isAlreadySaved) {
      setWishlist(prev => ({
        ...prev,
        [product.id]: {
          ...product,
          savedSize: targetSize,
          savedAt: new Date().toISOString()
        }
      }));

      showToast(`✓ Saved in Size ${targetSize} (Relaxed Fit)`);

      logTelemetry('IMPLICIT_CONTEXT_CAPTURE', {
        productId: product.id,
        inferredSize: targetSize,
        method: 'SCROLL_DEPTH_INFERENCE',
        targetStore: 'Zustand Local Cache',
        latency: '0ms'
      });
    } else {
      setWishlist(prev => {
        const copy = { ...prev };
        delete copy[product.id];
        return copy;
      });
      showToast(`Removed from Wishlist`);
      logTelemetry('WISHLIST_ITEM_REMOVED', { productId: product.id });
    }
  };

  // Step 2 & 3: Move from Wishlist to Bag
  const handleAddWishlistToBag = (product) => {
    const targetSize = wishlist[product.id]?.savedSize || product.inferredSize || 'M';
    const existingIndex = bagItems.findIndex(i => i.id === product.id && i.size === targetSize);

    if (existingIndex >= 0) {
      setBagItems(prev => prev.map((item, idx) => idx === existingIndex ? { ...item, quantity: item.quantity + 1 } : item));
    } else {
      setBagItems(prev => [
        ...prev,
        {
          id: product.id,
          brand: product.brand,
          title: product.title,
          size: targetSize,
          price: product.price,
          mrp: product.mrp,
          image: product.image,
          quantity: 1
        }
      ]);
    }

    // Remove from wishlist once added
    setWishlist(prev => {
      const copy = { ...prev };
      delete copy[product.id];
      return copy;
    });

    showToast(`🛒 Added Size ${targetSize} to Shopping Bag`);

    logTelemetry('CART_BRIDGE_CONVERSION', {
      productId: product.id,
      size: targetSize,
      cartSubtotalBefore: bagSubtotal,
      cartSubtotalAfter: bagSubtotal + product.price,
      unlockedFreeDelivery: (bagSubtotal + product.price) >= FREE_DELIVERY_THRESHOLD
    });
  };

  // Cart item quantity handlers
  const handleUpdateQuantity = (id, size, delta) => {
    setBagItems(prev => prev.map(item => {
      if (item.id === id && item.size === size) {
        const newQty = item.quantity + delta;
        return newQty > 0 ? { ...item, quantity: newQty } : null;
      }
      return item;
    }).filter(Boolean));
    showToast('Cart updated');
  };

  const handleRemoveCartItem = (id, size) => {
    setBagItems(prev => prev.filter(item => !(item.id === id && item.size === size)));
    showToast('Item removed from Bag');
  };

  const handleReset = () => {
    setWishlist({});
    setSelectedProductForPDP(null);
    setOrderPlacedSuccess(false);
    setActiveTab('home');
    setSelectedFilter('All');
    setSearchQuery('');
    setCouponApplied(false);
    setPincode('560034');
    setBagItems([
      {
        id: 'jacket-1',
        brand: 'WROGN',
        title: 'Men Washed Slim Fit Denim Biker Jacket',
        size: 'L',
        price: 1299,
        mrp: 2799,
        image: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=600&q=80',
        quantity: 1
      }
    ]);
    setTelemetryLogs([]);
    showToast('Prototype state reset');
  };

  // Open PDP handler
  const handleOpenPDP = (product) => {
    setSelectedProductForPDP(product);
    setPdpSelectedSize(product.inferredSize || 'M');
  };

  const wishlistCount = Object.keys(wishlist).length;
  
  // Intelligent Cart Utility Bridge Item Selector:
  // Pick the best wishlist item that bridges the shortfall to ₹2,500
  const shortfall = FREE_DELIVERY_THRESHOLD - bagSubtotal;
  const wishlistItemsArray = Object.values(wishlist);
  const bestBridgeItem = wishlistItemsArray.length > 0
    ? (wishlistItemsArray.find(item => item.price >= shortfall) || wishlistItemsArray[0])
    : null;

  return (
    <div className="project-catalyst-container">
      {/* Top Header */}
      <div className="page-header">
        <div className="header-left">
          <div className="badge-pill">
            <Zap size={14} className="icon-pulse" /> Zero-Friction Re-engagement Engine
          </div>
          <h1 className="page-title text-gradient">Myntra Project Catalyst — Full MVP App (16+ Items)</h1>
          <p className="page-subtitle">
            Autonomous product experiment converting dormant wishlists into high-converting transactions without monetary discounts.
          </p>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary reset-btn" onClick={handleReset}>
            <RotateCcw size={14} /> Reset State
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="catalyst-grid">
        
        {/* Left Column: Strategy & Live Telemetry Inspector */}
        <div className="strategy-column">
          
          {/* Strategy Framework */}
          <div className="strategy-panel glass-panel">
            <div className="panel-header">
              <Sparkles size={18} className="icon-pink" />
              <h3>The 3-Step Zero-Friction Architecture</h3>
            </div>

            <div className="panel-body">
              <div className="strategy-steps">
                {/* Step 1 */}
                <div 
                  className={`step-card ${activeTab === 'home' ? 'step-active' : ''}`}
                  onClick={() => { setActiveTab('home'); setSelectedProductForPDP(null); }}
                >
                  <div className="step-num">1</div>
                  <div className="step-info">
                    <div className="step-title-row">
                      <h5>Implicit Context Capture</h5>
                      <span className="step-tag tag-blue">Home Feed</span>
                    </div>
                    <p>
                      Users tap the heart icon on any item. Telemetry instantly records the active variant (e.g. <strong>Size M</strong>) from scroll depth and acknowledges via a subtle 2s toast. Zero modal interruption.
                    </p>
                  </div>
                </div>

                {/* Step 2 */}
                <div 
                  className={`step-card ${activeTab === 'wishlist' ? 'step-active' : ''}`}
                  onClick={() => { setActiveTab('wishlist'); setSelectedProductForPDP(null); }}
                >
                  <div className="step-num">2</div>
                  <div className="step-info">
                    <div className="step-title-row">
                      <h5>The Decision Card</h5>
                      <span className="step-tag tag-purple">Wishlist Surface</span>
                    </div>
                    <p>
                      Replaces dead thumbnail grids with actionable Decision Cards. Features <strong>Fit Consensus badges</strong>, return guarantees, and a 1-tap checkout CTA.
                    </p>
                  </div>
                </div>

                {/* Step 3 */}
                <div 
                  className={`step-card ${activeTab === 'bag' ? 'step-active' : ''}`}
                  onClick={() => { setActiveTab('bag'); setSelectedProductForPDP(null); }}
                >
                  <div className="step-num">3</div>
                  <div className="step-info">
                    <div className="step-title-row">
                      <h5>Cart Utility Bridge</h5>
                      <span className="step-tag tag-green">Pre-Checkout Surface</span>
                    </div>
                    <p>
                      Dynamically detects when cart subtotal is near the <strong>₹2,500 Free Shipping</strong> threshold. Injects a 1-tap bridge to add the saved item and save ₹99 delivery fees.
                    </p>
                  </div>
                </div>
              </div>

              {/* Interactive Test Walkthrough */}
              <div className="quick-test-guide">
                <h4>🧪 Comprehensive Test Guide (All Edge Cases)</h4>
                <ol className="walkthrough-list">
                  <li>
                    <strong>Test 1 (Catalog & Search):</strong> Scroll through all 16 products in the phone frame. Use the search bar or filter pills (Shirts, Jackets, Footwear) to filter items.
                  </li>
                  <li>
                    <strong>Test 2 (Implicit Saves):</strong> Tap the <strong>Heart (♡)</strong> on multiple items. Notice the instant toast and live telemetry cache updates.
                  </li>
                  <li>
                    <strong>Test 3 (Categories Tab):</strong> Tap the <strong>Categories (🗂️)</strong> tab in the bottom bar. Browse subcategories and tap any to filter the feed!
                  </li>
                  <li>
                    <strong>Test 4 (Decision Cards):</strong> Tap <strong>Wishlist (❤️)</strong>. See Decision Cards for all saved items with 1-tap Add to Bag CTAs.
                  </li>
                  <li>
                    <strong>Test 5 (Cart Bridge & Coupons):</strong> Tap <strong>Bag (🛍️)</strong>. Test the <strong>Cart Bridge banner</strong>, coupon toggle (`MYNTRA200`), and quantity (+/-) controls!
                  </li>
                </ol>
              </div>
            </div>
          </div>

          {/* Telemetry Inspector */}
          <div className="telemetry-panel glass-panel">
            <div className="panel-header">
              <Database size={16} className="icon-cyan" />
              <h3>Client-Side Store & Pipeline Telemetry</h3>
            </div>
            <div className="telemetry-body">
              <div className="telemetry-grid">
                <div className="telemetry-card">
                  <span className="telemetry-label">Wishlist Cache (Zustand)</span>
                  <span className={`telemetry-metric ${wishlistCount > 0 ? 'text-pink' : 'text-muted'}`}>
                    {wishlistCount} Item(s) Locked
                  </span>
                </div>
                <div className="telemetry-card">
                  <span className="telemetry-label">Cart Subtotal</span>
                  <span className="telemetry-metric text-cyan">₹{bagSubtotal}</span>
                </div>
                <div className="telemetry-card">
                  <span className="telemetry-label">Free Delivery Status</span>
                  <span className={`telemetry-metric ${isFreeDeliveryUnlocked ? 'text-green' : 'text-orange'}`}>
                    {isFreeDeliveryUnlocked ? '✓ FREE DELIVERED' : `Shortfall: ₹${Math.max(0, FREE_DELIVERY_THRESHOLD - bagSubtotal)}`}
                  </span>
                </div>
                <div className="telemetry-card">
                  <span className="telemetry-label">Cart Bridge Math</span>
                  <span className="telemetry-metric text-green">
                    {bestBridgeItem && !isFreeDeliveryUnlocked ? `⚡ ACTIVE (Item: ₹${bestBridgeItem.price})` : 'IDLE'}
                  </span>
                </div>
              </div>

              {telemetryLogs.length > 0 && (
                <div className="telemetry-feed">
                  <div className="feed-header">⚡ Live Telemetry Event Stream:</div>
                  <div className="feed-list">
                    {telemetryLogs.map((log, idx) => (
                      <div key={idx} className="feed-item">
                        <div className="feed-meta">
                          <span className="feed-event">{log.event}</span>
                          <span className="feed-time">{log.timestamp}</span>
                        </div>
                        <pre>{JSON.stringify(log.payload, null, 2)}</pre>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>

        {/* Right Column: Simulated Myntra Native Mobile App */}
        <div className="phone-preview-panel">
          <div className="phone-wrapper">
            {/* Phone Hardware Shell */}
            <div className="phone-speaker-cutout"></div>
            <div className="phone-camera-lens"></div>
            <div className="phone-volume-btn volume-up"></div>
            <div className="phone-volume-btn volume-down"></div>
            <div className="phone-power-btn"></div>

            {/* Screen Viewport */}
            <div className="phone-screen">
              <div className="mobile-app">
                
                {/* iOS Top Status Bar */}
                <div className="status-bar">
                  <span className="status-time">09:41</span>
                  <div className="status-icons">
                    <span className="signal-bars">●●●●</span>
                    <span className="wifi-icon">📶</span>
                    <span className="battery-icon">🔋</span>
                  </div>
                </div>

                {/* Myntra Sticky App Header */}
                <div className="myntra-app-header">
                  <div className="header-top-row">
                    <div 
                      className="myntra-logo-group"
                      onClick={() => { setActiveTab('home'); setSelectedFilter('All'); setSearchQuery(''); }}
                    >
                      <div className="myntra-m-badge">M</div>
                      <span className="myntra-brand-text">MYNTRA</span>
                    </div>
                    <div className="header-nav-icons">
                      <div className="h-icon-btn" onClick={() => showToast("Notifications: 2 offers available")}>
                        <Bell size={18} color="#282c3f" />
                      </div>
                      <div 
                        className={`h-icon-btn ${activeTab === 'wishlist' ? 'active' : ''}`}
                        onClick={() => { setActiveTab('wishlist'); setSelectedProductForPDP(null); }}
                      >
                        <Heart size={18} fill={wishlistCount > 0 ? "#ff3f6c" : "none"} color={wishlistCount > 0 ? "#ff3f6c" : "#282c3f"} />
                        {wishlistCount > 0 && <span className="h-badge">{wishlistCount}</span>}
                      </div>
                      <div 
                        className={`h-icon-btn ${activeTab === 'bag' ? 'active' : ''}`}
                        onClick={() => { setActiveTab('bag'); setSelectedProductForPDP(null); }}
                      >
                        <ShoppingBag size={18} color="#282c3f" />
                        <span className="h-badge">{bagItems.length}</span>
                      </div>
                    </div>
                  </div>

                  {/* Search Bar with Live Filtering */}
                  <div className="myntra-search-bar">
                    <Search size={14} color="#7e818c" />
                    <input 
                      type="text" 
                      placeholder="Search 16+ shirts, denim, sneakers..." 
                      className="search-input"
                      value={searchQuery}
                      onChange={(e) => {
                        setSearchQuery(e.target.value);
                        if (activeTab !== 'home') setActiveTab('home');
                      }}
                    />
                    {searchQuery ? (
                      <X size={14} color="#7e818c" className="cursor-pointer" onClick={() => setSearchQuery('')} />
                    ) : (
                      <div className="search-actions">
                        <Camera size={14} color="#7e818c" onClick={() => showToast("Visual Search ready")} />
                        <Mic size={14} color="#7e818c" onClick={() => showToast("Voice Search ready")} />
                      </div>
                    )}
                  </div>
                </div>

                {/* App Content Body (Scrollable) */}
                <div className="app-content-scrollable">

                  {/* ================================================= */}
                  {/* TAB 1: HOME FEED VIEW (16+ Items)                 */}
                  {/* ================================================= */}
                  {activeTab === 'home' && (
                    <div className="home-feed-view">
                      
                      {/* Stories / Category Avatars */}
                      <div className="category-stories">
                        {CATEGORIES_DATA.map((cat) => (
                          <div 
                            key={cat.id} 
                            className="story-item" 
                            onClick={() => {
                              setSelectedFilter(cat.name);
                              showToast(`Filtered: ${cat.name}`);
                            }}
                          >
                            <div className="story-ring">
                              <img src={cat.banner} alt={cat.name} className="story-img" />
                            </div>
                            <span className="story-label">{cat.name}</span>
                          </div>
                        ))}
                      </div>

                      {/* Promo Carousel Banner */}
                      <div className="promo-banner" onClick={() => showToast("Grand Festive Offers Applied!")}>
                        <div className="banner-badge">FESTIVAL SPECIAL</div>
                        <div className="banner-title">FLAT 50% - 80% OFF</div>
                        <div className="banner-subtitle">Highlander, Wrogn, Levi's, Nike & Zara</div>
                      </div>

                      {/* Horizontal Filter Pills */}
                      <div className="filter-pills-row">
                        {FILTER_PILLS.map((pill) => (
                          <button
                            key={pill}
                            className={`filter-pill-btn ${selectedFilter === pill ? 'active' : ''}`}
                            onClick={() => setSelectedFilter(pill)}
                          >
                            {pill}
                          </button>
                        ))}
                      </div>

                      {/* Feed Header */}
                      <div className="feed-section-header">
                        <span className="feed-title">
                          {selectedFilter === 'All' ? 'ALL PRODUCTS' : selectedFilter.toUpperCase()} ({filteredProducts.length})
                        </span>
                        <span className="feed-filter-btn" onClick={() => setSelectedFilter('All')}>
                          <SlidersHorizontal size={11} /> Reset
                        </span>
                      </div>

                      {/* 2-Column Product Grid (16 Products) */}
                      {filteredProducts.length > 0 ? (
                        <div className="myntra-product-grid">
                          {filteredProducts.map((prod) => {
                            const isSaved = !!wishlist[prod.id];
                            return (
                              <div 
                                key={prod.id} 
                                className="feed-product-card"
                              >
                                <div 
                                  className="feed-img-box"
                                  onClick={() => handleOpenPDP(prod)}
                                >
                                  <img src={prod.image} alt={prod.title} className="feed-prod-img" />
                                  <div className="rating-tag">
                                    <Star size={10} fill="#03a685" color="#03a685" />
                                    <span>{prod.rating}</span>
                                    <span className="r-count">| {prod.ratingCount}</span>
                                  </div>
                                  <span className="prod-badge-tag">{prod.tag}</span>
                                </div>

                                {/* 1-Tap Heart Button (Implicit Save) */}
                                <button 
                                  className={`feed-heart-btn ${isSaved ? 'saved' : ''}`}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleToggleWishlist(prod);
                                  }}
                                  title="Wishlist Item"
                                >
                                  <Heart 
                                    size={16} 
                                    fill={isSaved ? "#ff3f6c" : "rgba(255,255,255,0.8)"} 
                                    color={isSaved ? "#ff3f6c" : "#282c3f"} 
                                  />
                                </button>

                                <div 
                                  className="feed-prod-details"
                                  onClick={() => handleOpenPDP(prod)}
                                >
                                  <div className="feed-brand">{prod.brand}</div>
                                  <div className="feed-title-line">{prod.title}</div>
                                  <div className="feed-price-row">
                                    <span className="feed-price">₹{prod.price}</span>
                                    <span className="feed-mrp">₹{prod.mrp}</span>
                                    <span className="feed-disc">{prod.discount}</span>
                                  </div>
                                  <div className="feed-size-hint">
                                    <span className="hint-pill">Size {prod.inferredSize} Inferred</span>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="empty-search-state">
                          <p>No products found matching "{searchQuery}".</p>
                          <button className="btn-myntra-solid" onClick={() => { setSearchQuery(''); setSelectedFilter('All'); }}>
                            Clear Search Filters
                          </button>
                        </div>
                      )}

                    </div>
                  )}

                  {/* ================================================= */}
                  {/* TAB 2: CATEGORIES BROWSER VIEW (Full Section)     */}
                  {/* ================================================= */}
                  {activeTab === 'categories' && (
                    <div className="categories-tab-view">
                      <div className="categories-header">
                        <h2>EXPLORE CATEGORIES</h2>
                        <span className="cat-count">100+ Curated Brands</span>
                      </div>

                      {/* Category Switcher Tabs */}
                      <div className="cat-nav-tabs">
                        {CATEGORIES_DATA.map((cat) => (
                          <button
                            key={cat.id}
                            className={`cat-tab-btn ${selectedCategoryTab === cat.id ? 'active' : ''}`}
                            onClick={() => setSelectedCategoryTab(cat.id)}
                          >
                            <span>{cat.icon}</span>
                            <span>{cat.name}</span>
                          </button>
                        ))}
                      </div>

                      {/* Selected Category Content */}
                      {(() => {
                        const activeCat = CATEGORIES_DATA.find(c => c.id === selectedCategoryTab) || CATEGORIES_DATA[0];
                        return (
                          <div className="cat-detail-panel animate-fade-in">
                            <div className="cat-banner-box">
                              <img src={activeCat.banner} alt={activeCat.name} className="cat-banner-img" />
                              <div className="cat-banner-overlay">
                                <h3>{activeCat.name} Collection</h3>
                                <p>{activeCat.count}</p>
                              </div>
                            </div>

                            <div className="subcat-list">
                              <span className="subcat-title">POPULAR SUB-CATEGORIES</span>
                              <div className="subcat-grid">
                                {activeCat.subcategories.map((sub, i) => (
                                  <div 
                                    key={i} 
                                    className="subcat-card"
                                    onClick={() => {
                                      setSelectedFilter(sub === 'All' ? 'All' : sub);
                                      setActiveTab('home');
                                      showToast(`Filtered: ${sub}`);
                                    }}
                                  >
                                    <span className="subcat-name">{sub}</span>
                                    <ChevronRight size={14} color="#7e818c" />
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        );
                      })()}
                    </div>
                  )}

                  {/* ================================================= */}
                  {/* TAB 3: WISHLIST (PROJECT CATALYST DECISION CARDS)  */}
                  {/* ================================================= */}
                  {activeTab === 'wishlist' && (
                    <div className="wishlist-view">
                      <div className="view-header-strip">
                        <div className="vh-title-group">
                          <h2 className="vh-title">MY WISHLIST</h2>
                          <span className="vh-count">{wishlistCount} Items</span>
                        </div>
                        {wishlistCount > 0 && (
                          <span className="vh-action" onClick={() => { setWishlist({}); showToast('Wishlist cleared'); }}>
                            Clear All
                          </span>
                        )}
                      </div>

                      {wishlistCount > 0 ? (
                        <div className="decision-cards-list">
                          {Object.values(wishlist).map((item) => (
                            <div key={item.id} className="decision-card animate-fade-in">
                              
                              <div className="dc-top-row">
                                <div className="dc-img-container" onClick={() => handleOpenPDP(item)}>
                                  <img src={item.image} alt={item.title} className="dc-img" />
                                </div>
                                <div className="dc-info-col">
                                  <div className="dc-brand-name">{item.brand}</div>
                                  <div className="dc-item-title">{item.title}</div>
                                  
                                  {/* Locked Inferred Variant */}
                                  <div className="dc-variant-locked">
                                    <span>Selected Variant:</span>
                                    <span className="size-badge-pink">Size {item.savedSize || item.inferredSize}</span>
                                  </div>

                                  <div className="dc-price-line">
                                    <span className="dc-price-bold">₹{item.price}</span>
                                    <span className="dc-mrp-strike">₹{item.mrp}</span>
                                    <span className="dc-disc-tag">{item.discount}</span>
                                  </div>

                                  {/* Trust Injectors */}
                                  <div className="dc-trust-injectors">
                                    <div className="trust-pill pill-green">
                                      <CheckCircle2 size={11} /> {item.fitConsensus}
                                    </div>
                                    <div className="trust-pill pill-blue">
                                      <ShieldCheck size={11} /> {item.returns}
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* 1-Tap Add to Bag CTA */}
                              <div className="dc-action-footer">
                                <button 
                                  className="btn-dc-add"
                                  onClick={() => {
                                    handleAddWishlistToBag(item);
                                    setActiveTab('bag');
                                  }}
                                >
                                  🛒 Add Size {item.savedSize || item.inferredSize} to Bag
                                </button>
                              </div>

                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="empty-state-box">
                          <div className="empty-heart-ring">
                            <Heart size={38} color="#ff3f6c" strokeWidth={1.5} />
                          </div>
                          <h3>Your Wishlist is Empty</h3>
                          <p>Tap the heart icon on any shirt, jeans, or jacket in the Home feed to see the Decision Card in action.</p>
                          <button className="btn-myntra-solid" onClick={() => setActiveTab('home')}>
                            Explore Catalog (16+ Items)
                          </button>
                        </div>
                      )}
                    </div>
                  )}

                  {/* ================================================= */}
                  {/* TAB 4: SHOPPING BAG & CART UTILITY BRIDGE         */}
                  {/* ================================================= */}
                  {activeTab === 'bag' && (
                    <div className="bag-view">
                      
                      {/* Pincode & Express Delivery Strip */}
                      <div className="pincode-strip">
                        <div className="pin-info">
                          <Truck size={14} color="#ff3f6c" />
                          <span>Deliver to: <strong>Bangalore - {pincode}</strong></span>
                        </div>
                        <span className="pin-change" onClick={() => setPincodeModalOpen(true)}>CHANGE</span>
                      </div>

                      {/* Threshold Progress Bar */}
                      <div className="free-shipping-tracker">
                        <div className="fst-header">
                          <span className="fst-title">
                            {isFreeDeliveryUnlocked 
                              ? "🎉 FREE Delivery Unlocked on this Order!" 
                              : `Add ₹${Math.max(0, FREE_DELIVERY_THRESHOLD - bagSubtotal)} more for FREE Delivery`}
                          </span>
                          <span className="fst-target">Goal: ₹2,500</span>
                        </div>
                        <div className="fst-bar">
                          <div 
                            className={`fst-fill ${isFreeDeliveryUnlocked ? 'unlocked' : ''}`}
                            style={{ width: `${Math.min(100, (bagSubtotal / FREE_DELIVERY_THRESHOLD) * 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Available Coupon Strip */}
                      <div className="coupon-promo-strip">
                        <div className="coupon-left">
                          <Gift size={16} color="#ff3f6c" />
                          <div>
                            <strong>MYNTRA200</strong>
                            <p>Save flat ₹200 on orders above ₹1,000</p>
                          </div>
                        </div>
                        <button 
                          className={`btn-coupon-toggle ${couponApplied ? 'applied' : ''}`}
                          onClick={() => {
                            setCouponApplied(!couponApplied);
                            showToast(couponApplied ? 'Coupon removed' : 'Coupon MYNTRA200 applied (-₹200)!');
                          }}
                        >
                          {couponApplied ? 'APPLIED ✓' : 'APPLY'}
                        </button>
                      </div>

                      {/* Cart Items List */}
                      {bagItems.length > 0 ? (
                        <div className="cart-items-wrapper">
                          {bagItems.map((item) => (
                            <div key={`${item.id}-${item.size}`} className="bag-item-card">
                              <div className="bi-img-box">
                                <img src={item.image} alt={item.title} className="bi-img" />
                              </div>
                              <div className="bi-details">
                                <div className="bi-brand">{item.brand}</div>
                                <div className="bi-title">{item.title}</div>
                                <div className="bi-selectors">
                                  <span className="bi-pill">Size: {item.size}</span>
                                </div>
                                <div className="bi-qty-row">
                                  <div className="qty-stepper">
                                    <button onClick={() => handleUpdateQuantity(item.id, item.size, -1)}>
                                      <Minus size={11} />
                                    </button>
                                    <span>{item.quantity}</span>
                                    <button onClick={() => handleUpdateQuantity(item.id, item.size, 1)}>
                                      <Plus size={11} />
                                    </button>
                                  </div>
                                  <div className="bi-pricing">
                                    <span className="bi-price">₹{item.price * item.quantity}</span>
                                    <span className="bi-mrp">₹{item.mrp * item.quantity}</span>
                                  </div>
                                </div>
                              </div>
                              <button 
                                className="bi-remove-btn"
                                onClick={() => handleRemoveCartItem(item.id, item.size)}
                                title="Remove item"
                              >
                                <X size={14} />
                              </button>
                            </div>
                          ))}
                        </div>
                      ) : null}

                      {/* DYNAMIC CART UTILITY BRIDGE BANNER (Intelligent Match) */}
                      {bestBridgeItem && !isFreeDeliveryUnlocked && (
                        <div className="cart-utility-bridge-banner animate-slide-up">
                          <div className="cub-badge">💡 RE-ENGAGEMENT BRIDGE</div>
                          <div className="cub-body">
                            <div className="cub-sparkle">
                              <Sparkles size={20} color="#ff3f6c" />
                            </div>
                            <div className="cub-text">
                              <div className="cub-headline">Complete your look & save ₹99 shipping!</div>
                              <div className="cub-sub">
                                Add saved <strong>{bestBridgeItem.brand} (Size {bestBridgeItem.savedSize || bestBridgeItem.inferredSize})</strong> for ₹{bestBridgeItem.price} to unlock <strong>FREE Delivery</strong>.
                              </div>
                            </div>
                            <button 
                              className="btn-bridge-instant-add"
                              onClick={() => handleAddWishlistToBag(bestBridgeItem)}
                            >
                              + Add
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Price Details Card */}
                      {bagItems.length > 0 ? (
                        <div className="bill-details-card">
                          <div className="bill-heading">PRICE DETAILS ({bagItems.reduce((a, b) => a + b.quantity, 0)} Items)</div>
                          
                          <div className="bill-row">
                            <span>Total MRP</span>
                            <span>₹{totalMrp}</span>
                          </div>

                          <div className="bill-row">
                            <span>Discount on MRP</span>
                            <span className="text-green">-₹{totalMrp - rawSubtotal}</span>
                          </div>

                          {couponApplied && (
                            <div className="bill-row">
                              <span>Coupon Discount (MYNTRA200)</span>
                              <span className="text-green">-₹200</span>
                            </div>
                          )}

                          <div className="bill-row">
                            <span>Delivery Fee</span>
                            <span>
                              {isFreeDeliveryUnlocked ? (
                                <span className="text-green font-bold">FREE (Saved ₹99)</span>
                              ) : (
                                <span>₹99</span>
                              )}
                            </span>
                          </div>

                          <div className="bill-divider"></div>

                          <div className="bill-row bill-total">
                            <span>Total Amount</span>
                            <span className="bill-final-price">₹{finalTotal}</span>
                          </div>

                          <div className="savings-badge">
                            🎉 You are saving ₹{totalDiscount + (isFreeDeliveryUnlocked ? 99 : 0)} on this order!
                          </div>

                          <button 
                            className="btn-place-order"
                            onClick={() => setOrderPlacedSuccess(true)}
                          >
                            PLACE ORDER <ChevronRight size={16} />
                          </button>
                        </div>
                      ) : (
                        <div className="empty-state-box">
                          <h3>Your Bag is Empty</h3>
                          <p>Add products from Home, Categories, or your Wishlist to proceed.</p>
                          <button className="btn-myntra-solid" onClick={() => setActiveTab('home')}>
                            Shop Now
                          </button>
                        </div>
                      )}

                    </div>
                  )}

                </div>

                {/* Floating Bottom Toast Notification */}
                <div className={`myntra-toast ${toastVisible ? 'toast-show' : ''}`}>
                  <CheckCircle2 size={16} color="#10b981" />
                  <span>{toastMessage}</span>
                </div>

                {/* Native Bottom App Navigation Bar (4 Working Tabs) */}
                <div className="myntra-bottom-nav">
                  <div 
                    className={`nav-tab ${activeTab === 'home' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('home'); setSelectedProductForPDP(null); }}
                  >
                    <div className="tab-icon">🏠</div>
                    <span>Home</span>
                  </div>
                  <div 
                    className={`nav-tab ${activeTab === 'categories' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('categories'); setSelectedProductForPDP(null); }}
                  >
                    <div className="tab-icon">🗂️</div>
                    <span>Categories</span>
                  </div>
                  <div 
                    className={`nav-tab ${activeTab === 'wishlist' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('wishlist'); setSelectedProductForPDP(null); }}
                  >
                    <div className="tab-icon">
                      ❤️
                      {wishlistCount > 0 && <span className="tab-badge">{wishlistCount}</span>}
                    </div>
                    <span>Wishlist</span>
                  </div>
                  <div 
                    className={`nav-tab ${activeTab === 'bag' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('bag'); setSelectedProductForPDP(null); }}
                  >
                    <div className="tab-icon">
                      🛍️
                      {bagItems.length > 0 && (
                        <span className="tab-badge">{bagItems.reduce((a, b) => a + b.quantity, 0)}</span>
                      )}
                    </div>
                    <span>Bag</span>
                  </div>
                </div>

                {/* ================================================= */}
                {/* MODAL 1: PRODUCT DETAILS PAGE (PDP) QUICK VIEW    */}
                {/* ================================================= */}
                {selectedProductForPDP && (
                  <div className="pdp-modal-overlay">
                    <div className="pdp-modal animate-slide-up">
                      <div className="pdp-header">
                        <span className="pdp-brand">{selectedProductForPDP.brand}</span>
                        <button className="pdp-close" onClick={() => setSelectedProductForPDP(null)}>
                          <X size={18} />
                        </button>
                      </div>

                      <div className="pdp-scroll-body">
                        <div className="pdp-image-box">
                          <img src={selectedProductForPDP.image} alt="PDP" className="pdp-img" />
                          <div className="pdp-depth-badge">
                            <Zap size={12} color="#00f2fe" /> Scroll Depth: 85% on Size {pdpSelectedSize}
                          </div>
                        </div>

                        <div className="pdp-details-block">
                          <h3 className="pdp-title">{selectedProductForPDP.title}</h3>
                          <div className="pdp-price-row">
                            <span className="pdp-price">₹{selectedProductForPDP.price}</span>
                            <span className="pdp-mrp">₹{selectedProductForPDP.mrp}</span>
                            <span className="pdp-discount">{selectedProductForPDP.discount}</span>
                          </div>

                          {/* Size Selection Chips */}
                          <div className="pdp-size-section">
                            <div className="pdp-size-header">
                              <span>SELECT SIZE</span>
                              <span className="size-chart-link" onClick={() => showToast("Size Chart: Standard Regular Fit")}>
                                Size Chart
                              </span>
                            </div>
                            <div className="pdp-size-chips">
                              {(selectedProductForPDP.sizes || ['S', 'M', 'L', 'XL']).map((s) => (
                                <button 
                                  key={s}
                                  className={`pdp-size-pill ${pdpSelectedSize === s ? 'selected' : ''}`}
                                  onClick={() => setPdpSelectedSize(s)}
                                >
                                  {s}
                                </button>
                              ))}
                            </div>
                          </div>

                          {/* Trust Badges */}
                          <div className="pdp-trust-grid">
                            <div className="pdp-trust-box">
                              <CheckCircle2 size={16} color="#03a685" />
                              <div>
                                <strong>{selectedProductForPDP.fitConsensus}</strong>
                                <p>Based on verified returns data</p>
                              </div>
                            </div>
                            <div className="pdp-trust-box">
                              <ShieldCheck size={16} color="#3b82f6" />
                              <div>
                                <strong>14-Day Doorstep Returns</strong>
                                <p>Free pickup & instant exchanges</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* PDP Bottom Sticky CTA */}
                      <div className="pdp-cta-bar">
                        <button 
                          className="btn-pdp-wishlist"
                          onClick={() => {
                            handleToggleWishlist(selectedProductForPDP, pdpSelectedSize);
                            setSelectedProductForPDP(null);
                          }}
                        >
                          <Heart size={16} fill={wishlist[selectedProductForPDP.id] ? "#ff3f6c" : "none"} color="#ff3f6c" />
                          <span>{wishlist[selectedProductForPDP.id] ? 'Wishlisted' : 'Wishlist'}</span>
                        </button>
                        <button 
                          className="btn-pdp-addbag"
                          onClick={() => {
                            handleAddWishlistToBag({ ...selectedProductForPDP, inferredSize: pdpSelectedSize });
                            setSelectedProductForPDP(null);
                            setActiveTab('bag');
                          }}
                        >
                          <ShoppingBag size={16} />
                          <span>Add to Bag</span>
                        </button>
                      </div>

                    </div>
                  </div>
                )}

                {/* ================================================= */}
                {/* MODAL 2: PINCODE CHANGER MODAL                    */}
                {/* ================================================= */}
                {pincodeModalOpen && (
                  <div className="pdp-modal-overlay">
                    <div className="pincode-modal-card animate-scale-up">
                      <h3>Delivery Address</h3>
                      <p>Enter your 6-digit delivery pincode:</p>
                      <input 
                        type="text" 
                        maxLength={6} 
                        value={tempPincode}
                        onChange={(e) => setTempPincode(e.target.value)}
                        className="pincode-input"
                      />
                      <div className="pincode-actions">
                        <button className="btn-pin-cancel" onClick={() => setPincodeModalOpen(false)}>
                          Cancel
                        </button>
                        <button 
                          className="btn-pin-save"
                          onClick={() => {
                            setPincode(tempPincode || '560034');
                            setPincodeModalOpen(false);
                            showToast(`Delivery updated for pincode: ${tempPincode}`);
                          }}
                        >
                          Check Delivery
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* ================================================= */}
                {/* MODAL 3: ORDER PLACED SUCCESS CELEBRATION         */}
                {/* ================================================= */}
                {orderPlacedSuccess && (
                  <div className="order-success-modal-overlay">
                    <div className="order-success-card animate-scale-up">
                      <div className="success-icon-circle">
                        🎉
                      </div>
                      <h2>Order Placed Successfully!</h2>
                      <p className="order-id">Order ID: #MYN-894201</p>
                      
                      <div className="order-summary-box">
                        <div className="os-row">
                          <span>Items Ordered:</span>
                          <strong>{bagItems.reduce((a, b) => a + b.quantity, 0)} Products</strong>
                        </div>
                        <div className="os-row">
                          <span>Total Amount Paid:</span>
                          <strong className="text-pink">₹{finalTotal}</strong>
                        </div>
                        <div className="os-row">
                          <span>Deliver To:</span>
                          <strong>Bangalore - {pincode}</strong>
                        </div>
                        <div className="os-row">
                          <span>Estimated Delivery:</span>
                          <strong>Tuesday, 8 PM (Express)</strong>
                        </div>
                      </div>

                      <div className="order-savings-pill">
                        💸 You saved a total of ₹{totalDiscount + (isFreeDeliveryUnlocked ? 99 : 0)}!
                      </div>

                      <button 
                        className="btn-continue-shopping"
                        onClick={handleReset}
                      >
                        Continue Shopping / Reset
                      </button>
                    </div>
                  </div>
                )}

              </div>
            </div>

            {/* Bottom Home Bar */}
            <div className="phone-bottom-home-bar"></div>
          </div>

          <div className="phone-under-caption">
            <span className="live-badge">LIVE SIMULATION</span>
            <span>Myntra Native App Engine • 16+ Products</span>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ProjectCatalystMVP;
