/**
 * ============================================
 * Modern Admin Dashboard - Animation Engine
 * ============================================
 * 
 * Core animation modules for advanced dashboard interactions
 * Includes: CounterAnimator, RippleEffect, AnimationObserver, PerformanceMonitor
 */

// ============================================
// CounterAnimator Class
// ============================================
/**
 * Animates numbers from 0 to target value with smooth easing
 * @class CounterAnimator
 */
class CounterAnimator {
    /**
     * @param {HTMLElement} element - The element containing the number
     * @param {number} targetValue - The final value to animate to
     * @param {number} duration - Animation duration in milliseconds (default: 1500)
     */
    constructor(element, targetValue, duration = 1500) {
        this.element = element;
        this.targetValue = targetValue;
        this.duration = duration;
        this.startValue = 0;
        this.animationFrame = null;
    }

    /**
     * Easing function for natural movement (easeOutExpo)
     * @param {number} progress - Progress value between 0 and 1
     * @returns {number} Eased value
     */
    easeOutExpo(progress) {
        return progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
    }

    /**
     * Start the counter animation
     */
    animate() {
        const startTime = performance.now();

        const animateStep = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / this.duration, 1);

            // Apply easing function
            const eased = this.easeOutExpo(progress);
            const currentValue = Math.floor(this.startValue + (this.targetValue - this.startValue) * eased);

            // Format number with Brazilian locale
            this.element.textContent = currentValue.toLocaleString('pt-BR');

            // Continue animation if not complete
            if (progress < 1) {
                this.animationFrame = requestAnimationFrame(animateStep);
            } else {
                // Ensure final value is exact
                this.element.textContent = this.targetValue.toLocaleString('pt-BR');
            }
        };

        this.animationFrame = requestAnimationFrame(animateStep);
    }

    /**
     * Cancel the animation
     */
    cancel() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
    }

    /**
     * Initialize all counter elements with data-counter attribute
     * @static
     */
    static initAll() {
        const counterElements = document.querySelectorAll('[data-counter]');
        const animators = [];

        counterElements.forEach((element, index) => {
            const targetValue = parseInt(element.getAttribute('data-counter'), 10);

            if (!isNaN(targetValue)) {
                const animator = new CounterAnimator(element, targetValue);

                // Add staggered delay for multiple counters
                setTimeout(() => {
                    animator.animate();
                }, index * 100);

                animators.push(animator);
            }
        });

        return animators;
    }
}

// ============================================
// RippleEffect Class
// ============================================
/**
 * Creates ripple effect on click for interactive elements
 * @class RippleEffect
 */
class RippleEffect {
    /**
     * Apply ripple effect to an element
     * @static
     * @param {HTMLElement} element - The element to apply ripple effect to
     */
    static apply(element) {
        // Ensure element has position relative or absolute
        const position = window.getComputedStyle(element).position;
        if (position === 'static') {
            element.style.position = 'relative';
        }

        // Ensure overflow is hidden
        element.style.overflow = 'hidden';

        element.addEventListener('click', function(e) {
            // Create ripple element
            const ripple = document.createElement('span');
            ripple.className = 'ripple-effect';

            // Calculate ripple size and position
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            // Apply styles
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.5);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 600ms ease-out;
                pointer-events: none;
                z-index: 1000;
            `;

            // Add ripple to element
            this.appendChild(ripple);

            // Remove ripple after animation completes
            setTimeout(() => {
                ripple.remove()
            }, 600);
        });
    }

    /**
     * Initialize ripple effect on all elements with data-ripple attribute
     * @static
     */
    static initAll() {
        const rippleElements = document.querySelectorAll('[data-ripple]');

        rippleElements.forEach(element => {
            RippleEffect.apply(element);
        });

        return rippleElements.length;
    }
}

// ============================================
// AnimationObserver Class
// ============================================
/**
 * Observes elements entering viewport and triggers animations
 * @class AnimationObserver
 */
class AnimationObserver {
    /**
     * @param {Object} options - Configuration options for Intersection Observer
     */
    constructor(options = {}) {
        this.options = {
            threshold: options.threshold || 0.1,
            rootMargin: options.rootMargin || '0px 0px -100px 0px'
        };

        this.observer = new IntersectionObserver(
            (entries) => this.handleIntersection(entries),
            this.options
        );

        this.observedElements = new Set();
    }

    /**
     * Handle intersection events
     * @param {IntersectionObserverEntry[]} entries - Array of intersection entries
     */
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add animation class
                entry.target.classList.add('animate-in');

                // Get animation type from data attribute
                const animationType = entry.target.getAttribute('data-animate');
                if (animationType) {
                    entry.target.classList.add(`animate-${animationType}`);
                }

                // Unobserve element after animation for performance
                this.observer.unobserve(entry.target);
                this.observedElements.delete(entry.target);
            }
        });
    }

    /**
     * Observe a single element
     * @param {HTMLElement} element - Element to observe
     */
    observe(element) {
        if (!this.observedElements.has(element)) {
            this.observer.observe(element);
            this.observedElements.add(element);
        }
    }

    /**
     * Observe multiple elements
     * @param {NodeList|Array} elements - Elements to observe
     */
    observeAll(elements) {
        elements.forEach(element => this.observe(element));
    }

    /**
     * Stop observing an element
     * @param {HTMLElement} element - Element to unobserve
     */
    unobserve(element) {
        this.observer.unobserve(element);
        this.observedElements.delete(element);
    }

    /**
     * Disconnect observer and clear all observations
     */
    disconnect() {
        this.observer.disconnect();
        this.observedElements.clear();
    }

    /**
     * Initialize observer for all elements with data-animate attribute
     * @static
     */
    static initAll() {
        const observer = new AnimationObserver();
        const animateElements = document.querySelectorAll('[data-animate]');

        observer.observeAll(animateElements);

        return observer;
    }
}

// ============================================
// PerformanceMonitor Class
// ============================================
/**
 * Monitors performance and adjusts animations accordingly
 * @class PerformanceMonitor
 */
class PerformanceMonitor {
    /**
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        this.options = {
            fpsThreshold: options.fpsThreshold || 30,
            checkInterval: options.checkInterval || 1000,
            sampleSize: options.sampleSize || 10
        };

        this.fps = 60;
        this.lastTime = performance.now();
        this.frameCount = 0;
        this.fpsSamples = [];
        this.isMonitoring = false;
        this.monitoringInterval = null;
        this.performanceModeActive = false;
    }

    /**
     * Calculate current FPS
     * @returns {number} Current FPS
     */
    checkFPS() {
        const currentTime = performance.now();
        const delta = currentTime - this.lastTime;

        if (delta > 0) {
            this.fps = Math.round(1000 / delta);
            this.fpsSamples.push(this.fps);

            // Keep only recent samples
            if (this.fpsSamples.length > this.options.sampleSize) {
                this.fpsSamples.shift();
            }
        }

        this.lastTime = currentTime;
        this.frameCount++;

        return this.fps;
    }

    /**
     * Get average FPS from samples
     * @returns {number} Average FPS
     */
    getAverageFPS() {
        if (this.fpsSamples.length === 0) return 60;

        const sum = this.fpsSamples.reduce((a, b) => a + b, 0);
        return Math.round(sum / this.fpsSamples.length);
    }

    /**
     * Check if performance mode should be activated
     */
    evaluatePerformance() {
        const avgFPS = this.getAverageFPS();

        if (avgFPS < this.options.fpsThreshold && !this.performanceModeActive) {
            this.activatePerformanceMode();
        } else if (avgFPS >= this.options.fpsThreshold + 10 && this.performanceModeActive) {
            // Add hysteresis to prevent flickering
            this.deactivatePerformanceMode();
        }
    }

    /**
     * Activate performance mode to reduce animation complexity
     */
    activatePerformanceMode() {
        this.performanceModeActive = true;
        document.body.classList.add('performance-mode');

        console.log('Performance mode activated - FPS:', this.getAverageFPS());

        this.reduceAnimationComplexity();
    }

    /**
     * Deactivate performance mode
     */
    deactivatePerformanceMode() {
        this.performanceModeActive = false;
        document.body.classList.remove('performance-mode');

        console.log('Performance mode deactivated - FPS:', this.getAverageFPS());
    }

    /**
     * Reduce animation complexity for better performance
     */
    reduceAnimationComplexity() {
        // Disable heavy animations
        const heavyAnimations = document.querySelectorAll('.animate-float, .animate-float-slow, .animate-pulse-glow');
        heavyAnimations.forEach(element => {
            element.style.animation = 'none';
        });

        // Disable 3D transforms
        const transform3D = document.querySelectorAll('.card-3d, .card-3d-rotate, .card-3d-shadow');
        transform3D.forEach(element => {
            element.style.transform = 'none';
            element.style.willChange = 'auto';
        });

        // Disable backdrop filters
        const glassElements = document.querySelectorAll('.glass-card, .glass-bg');
        glassElements.forEach(element => {
            element.style.backdropFilter = 'none';
            element.style.webkitBackdropFilter = 'none';
        });
    }

    /**
     * Start monitoring performance
     */
    startMonitoring() {
        if (this.isMonitoring) return;

        this.isMonitoring = true;
        this.lastTime = performance.now();

        // Check FPS on each frame
        const checkFrame = () => {
            if (!this.isMonitoring) return;

            this.checkFPS();
            requestAnimationFrame(checkFrame);
        };

        requestAnimationFrame(checkFrame);

        // Evaluate performance periodically
        this.monitoringInterval = setInterval(() => {
            this.evaluatePerformance();
        }, this.options.checkInterval);

        console.log('Performance monitoring started');
    }

    /**
     * Stop monitoring performance
     */
    stopMonitoring() {
        this.isMonitoring = false;

        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }

        console.log('Performance monitoring stopped');
    }

    /**
     * Get current performance stats
     * @returns {Object} Performance statistics
     */
    getStats() {
        return {
            currentFPS: this.fps,
            averageFPS: this.getAverageFPS(),
            frameCount: this.frameCount,
            performanceMode: this.performanceModeActive,
            samples: this.fpsSamples.length
        };
    }

    /**
     * Initialize performance monitoring
     * @static
     */
    static init(options = {}) {
        const monitor = new PerformanceMonitor(options);
        monitor.startMonitoring();
        return monitor;
    }
}

// ============================================
// ParticleSystem Class
// ============================================
/**
 * Creates floating particle effects in the background
 * @class ParticleSystem
 */
class ParticleSystem {
    /**
     * @param {HTMLElement} container - The container element for particles
     * @param {number} particleCount - Number of particles to create (default: 50)
     */
    constructor(container, particleCount = 50) {
        this.container = container;
        this.particleCount = particleCount;
        this.particles = [];
        this.isInitialized = false;
    }

    /**
     * Initialize the particle system
     */
    init() {
        if (this.isInitialized) return;

        // Ensure container has position relative
        const position = window.getComputedStyle(this.container).position;
        if (position === 'static') {
            this.container.style.position = 'relative';
        }

        // Create particles
        for (let i = 0; i < this.particleCount; i++) {
            const particle = this.createParticle();
            this.container.appendChild(particle);
            this.particles.push(particle);
        }

        this.isInitialized = true;
        console.log(`ParticleSystem initialized with ${this.particleCount} particles`);
    }

    /**
     * Create a single particle element
     * @returns {HTMLElement} The particle element
     */
    createParticle() {
        const particle = document.createElement('div');
        particle.className = 'particle';

        // Random size between 5px and 15px
        const size = Math.random() * 10 + 5;

        // Random position
        const left = Math.random() * 100;
        const top = Math.random() * 100;

        // Random animation duration between 10s and 20s
        const duration = Math.random() * 10 + 10;

        // Random animation delay between 0s and 5s
        const delay = Math.random() * 5;

        // Random opacity between 0.1 and 0.3
        const opacity = Math.random() * 0.2 + 0.1;

        // Apply styles
        particle.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            background: radial-gradient(circle, rgba(102, 126, 234, ${opacity}), transparent);
            border-radius: 50%;
            left: ${left}%;
            top: ${top}%;
            animation: float ${duration}s infinite ease-in-out;
            animation-delay: ${delay}s;
            pointer-events: none;
            z-index: 0;
        `;

        return particle;
    }

    /**
     * Remove all particles and clean up
     */
    destroy() {
        this.particles.forEach(particle => particle.remove());
        this.particles = [];
        this.isInitialized = false;
    }

    /**
     * Adjust particle count for mobile devices
     * @param {number} count - New particle count
     */
    adjustParticleCount(count) {
        if (count < this.particles.length) {
            // Remove excess particles
            const toRemove = this.particles.length - count;
            for (let i = 0; i < toRemove; i++) {
                const particle = this.particles.pop();
                particle.remove();
            }
        } else if (count > this.particles.length) {
            // Add more particles
            const toAdd = count - this.particles.length;
            for (let i = 0; i < toAdd; i++) {
                const particle = this.createParticle();
                this.container.appendChild(particle);
                this.particles.push(particle);
            }
        }
        this.particleCount = count;
    }

    /**
     * Initialize particle system for a specific container
     * @static
     * @param {string} selector - CSS selector for the container
     * @param {number} particleCount - Number of particles
     * @returns {ParticleSystem|null} The particle system instance or null
     */
    static initForContainer(selector, particleCount = 50) {
        const container = document.querySelector(selector);
        if (!container) {
            console.warn(`ParticleSystem: Container "${selector}" not found`);
            return null;
        }

        const system = new ParticleSystem(container, particleCount);
        system.init();
        return system;
    }
}

// ============================================
// CursorFollowEffect Class
// ============================================
/**
 * Creates a glow effect that follows the cursor on cards
 * @class CursorFollowEffect
 */
class CursorFollowEffect {
    /**
     * @param {HTMLElement} card - The card element to apply the effect to
     */
    constructor(card) {
        this.card = card;
        this.isActive = false;
        this.init();
    }

    /**
     * Initialize the cursor follow effect
     */
    init() {
        // Ensure card has position relative
        const position = window.getComputedStyle(this.card).position;
        if (position === 'static') {
            this.card.style.position = 'relative';
        }

        // Add mousemove listener
        this.card.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.card.addEventListener('mouseenter', () => this.activate());
        this.card.addEventListener('mouseleave', () => this.deactivate());

        // Add CSS custom properties if not set
        this.card.style.setProperty('--mouse-x', '50%');
        this.card.style.setProperty('--mouse-y', '50%');
    }

    /**
     * Handle mouse move event
     * @param {MouseEvent} e - The mouse event
     */
    handleMouseMove(e) {
        if (!this.isActive) return;

        const rect = this.card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Update CSS custom properties
        this.card.style.setProperty('--mouse-x', `${x}px`);
        this.card.style.setProperty('--mouse-y', `${y}px`);
    }

    /**
     * Activate the effect
     */
    activate() {
        this.isActive = true;
        this.card.classList.add('cursor-follow-active');
    }

    /**
     * Deactivate the effect
     */
    deactivate() {
        this.isActive = false;
        this.card.classList.remove('cursor-follow-active');
    }

    /**
     * Remove the effect
     */
    destroy() {
        this.card.removeEventListener('mouve', this.handleMouseMove);
        this.card.classList.remove('cursor-follow-active');
    }

    /**
     * Apply cursor follow effect to all elements matching selector
     * @static
     * @param {string} selector - CSS selector for cards
     * @returns {CursorFollowEffect[]} Array of effect instances
     */
    static applyToAll(selector) {
        const cards = document.querySelectorAll(selector);
        const effects = [];

        cards.forEach(card => {
            const effect = new CursorFollowEffect(card);
            effects.push(effect);
        });

        console.log(`CursorFollowEffect applied to ${effects.length} elements`);
        return effects;
    }
}

// ============================================
// SkeletonLoader Class
// ============================================
/**
 * Manages skeleton loading states for content
 * @class SkeletonLoader
 */
class SkeletonLoader {
    /**
     * @param {HTMLElement} element - The element to show skeleton for
     * @param {string} type - Type of skeleton ('card', 'table-row', 'text')
     */
    constructor(element, type = 'card') {
        this.element = element;
        this.type = type;
        this.originalContent = null;
        this.isActive = false;
    }

    /**
     * Show skeleton loader
     */
    show() {
        if (this.isActive) return;

        // Store original content
        this.originalContent = this.element.innerHTML;

        // Add skeleton class
        this.element.classList.add('skeleton', `skeleton-${this.type}`);

        // Replace content with skeleton structure
        this.element.innerHTML = this.getSkeletonHTML();

        this.isActive = true;
    }

    /**
     * Hide skeleton loader and restore content
     */
    hide() {
        if (!this.isActive) return;

        // Remove skeleton classes
        this.element.classList.remove('skeleton', `skeleton-${this.type}`);

        // Restore original content
        if (this.originalContent !== null) {
            this.element.innerHTML = this.originalContent;
        }

        this.isActive = false;
    }

    /**
     * Get skeleton HTML based on type
     * @returns {string} Skeleton HTML
     */
    getSkeletonHTML() {
        switch (this.type) {
            case 'card':
                return `
                    <div class="skeleton-icon"></div>
                    <div class="skeleton-text skeleton-text-lg"></div>
                    <div class="skeleton-text skeleton-text-sm"></div>
                `;
            case 'table-row':
                return `
                    <td><div class="skeleton-text"></div></td>
                    <td><div class="skeleton-text"></div></td>
                    <td><div class="skeleton-text"></div></td>
                `;
            case 'text':
                return `<div class="skeleton-text"></div>`;
            default:
                return '';
        }
    }

    /**
     * Simulate loading with automatic hide after duration
     * @param {number} duration - Loading duration in milliseconds
     * @returns {Promise} Promise that resolves when loading is complete
     */
    simulateLoading(duration = 2000) {
        this.show();

        return new Promise(resolve => {
            setTimeout(() => {
                this.hide();
                resolve();
            }, duration);
        });
    }

    /**
     * Create skeleton loaders for multiple elements
     * @static
     * @param {string} selector - CSS selector for elements
     * @param {string} type - Type of skeleton
     * @returns {SkeletonLoader[]} Array of skeleton loader instances
     */
    static createForElements(selector, type = 'card') {
        const elements = document.querySelectorAll(selector);
        const loaders = [];

        elements.forEach(element => {
            const loader = new SkeletonLoader(element, type);
            loaders.push(loader);
        });

        return loaders;
    }

    /**
     * Show skeleton loaders for elements matching selector
     * @static
     * @param {string} selector - CSS selector
     * @param {string} type - Skeleton type
     * @param {number} duration - Auto-hide duration (0 = manual hide)
     * @returns {SkeletonLoader[]} Array of loader instances
     */
    static showForElements(selector, type = 'card', duration = 0) {
        const loaders = SkeletonLoader.createForElements(selector, type);

        loaders.forEach(loader => {
            if (duration > 0) {
                loader.simulateLoading(duration);
            } else {
                loader.show();
            }
        });

        return loaders;
    }
}

// ============================================
// TableAnimator Class
// ============================================
/**
 * Manages table row animations including hover effects and reordering
 * @class TableAnimator
 */
class TableAnimator {
    /**
     * @param {HTMLElement} table - The table element to animate
     */
    constructor(table) {
        this.table = table;
        this.tbody = table.querySelector('tbody');
        this.rows = [];
        this.isAnimating = false;
        this.init();
    }

    /**
     * Initialize table animations
     */
    init() {
        if (!this.tbody) return;

        this.rows = Array.from(this.tbody.querySelectorAll('tr'));

        // Add sequential animation delays if not already set
        this.rows.forEach((row, index) => {
            if (!row.style.animationDelay) {
                row.style.animationDelay = `${(index + 1) * 0.1}s`;
            }
        });

        console.log(`TableAnimator initialized for ${this.rows.length} rows`);
    }

    /**
     * Animate row reordering
     * @param {number} fromIndex - Original index
     * @param {number} toIndex - Target index
     */
    reorderRow(fromIndex, toIndex) {
        if (this.isAnimating || fromIndex === toIndex) return;
        if (fromIndex < 0 || fromIndex >= this.rows.length) return;
        if (toIndex < 0 || toIndex >= this.rows.length) return;

        this.isAnimating = true;

        const movingRow = this.rows[fromIndex];
        const direction = fromIndex < toIndex ? 'down' : 'up';

        // Add reordering class
        movingRow.classList.add('reordering', `moving-${direction}`);

        // Wait for animation to complete
        setTimeout(() => {
            // Update DOM
            if (direction === 'down') {
                const referenceRow = this.rows[toIndex].nextSibling;
                this.tbody.insertBefore(movingRow, referenceRow);
            } else {
                this.tbody.insertBefore(movingRow, this.rows[toIndex]);
            }

            // Update rows array
            this.rows.splice(fromIndex, 1);
            this.rows.splice(toIndex, 0, movingRow);

            // Remove animation classes
            movingRow.classList.remove('reordering', `moving-${direction}`);

            this.isAnimating = false;
        }, 500);
    }

    /**
     * Highlight a specific row temporarily
     * @param {number} index - Row index to highlight
     * @param {number} duration - Highlight duration in ms
     */
    highlightRow(index, duration = 2000) {
        if (index < 0 || index >= this.rows.length) return;

        const row = this.rows[index];
        const originalBg = row.style.background;

        // Apply highlight
        row.style.background = 'linear-gradient(90deg, rgba(102, 126, 234, 0.15) 0%, rgba(255, 255, 255, 0) 100%)';
        row.style.transition = 'background 0.3s ease';

        // Remove highlight after duration
        setTimeout(() => {
            row.style.background = originalBg;
        }, duration);
    }

    /**
     * Add a new row with animation
     * @param {HTMLElement} newRow - The new row element
     * @param {number} position - Position to insert (default: end)
     */
    addRow(newRow, position = -1) {
        // Set initial state for animation
        newRow.style.opacity = '0';
        newRow.style.transform = 'translateX(-30px)';
        newRow.setAttribute('data-animate', 'slideInRight');

        // Insert row
        if (position === -1 || position >= this.rows.length) {
            this.tbody.appendChild(newRow);
            this.rows.push(newRow);
        } else {
            this.tbody.insertBefore(newRow, this.rows[position]);
            this.rows.splice(position, 0, newRow);
        }

        // Trigger animation
        requestAnimationFrame(() => {
            newRow.classList.add('animate-in');
        });
    }

    /**
     * Remove a row with animation
     * @param {number} index - Row index to remove
     */
    removeRow(index) {
        if (index < 0 || index >= this.rows.length) return;

        const row = this.rows[index];

        // Animate out
        row.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        row.style.opacity = '0';
        row.style.transform = 'translateX(30px) scale(0.95)';

        // Remove after animation
        setTimeout(() => {
            row.remove();
            this.rows.splice(index, 1);
        }, 400);
    }

    /**
     * Refresh row references (call after external DOM changes)
     */
    refresh() {
        this.rows = Array.from(this.tbody.querySelectorAll('tr'));
    }

    /**
     * Initialize table animator for all tables with .table-modern class
     * @static
     * @returns {TableAnimator[]} Array of table animator instances
     */
    static initAll() {
        const tables = document.querySelectorAll('.table-modern');
        const animators = [];

        tables.forEach(table => {
            const animator = new TableAnimator(table);
            animators.push(animator);
        });

        console.log(`Initialized ${animators.length} table animators`);
        return animators;
    }
}

// ============================================
// TooltipManager Class
// ============================================
/**
 * Manages modern tooltips and popovers with animations
 * @class TooltipManager
 */
class TooltipManager {
    /**
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        this.options = {
            animationDuration: options.animationDuration || 200,
            offset: options.offset || 10,
            zIndexBase: options.zIndexBase || 10000
        };

        this.tooltips = new Map();
        this.activeTooltips = [];
        this.nextZIndex = this.options.zIndexBase;
    }

    /**
     * Create a tooltip element
     * @param {string} content - Tooltip content
     * @param {string} type - Tooltip type ('tooltip' or 'popover')
     * @returns {HTMLElement} The tooltip element
     */
    createTooltip(content, type = 'tooltip') {
        const tooltip = document.createElement('div');
        tooltip.className = `tooltip-modern tooltip-${type}`;
        tooltip.innerHTML = content;

        // Apply base styles
        tooltip.style.cssText = `
            position: fixed;
            opacity: 0;
            pointer-events: none;
            z-index: ${this.getNextZIndex()};
            transform: translateY(10px);
            transition: opacity ${this.options.animationDuration}ms ease,
                        transform ${this.options.animationDuration}ms ease;
        `;

        document.body.appendChild(tooltip);
        return tooltip;
    }

    /**
     * Get next z-index for stacking tooltips
     * @returns {number} Next z-index value
     */
    getNextZIndex() {
        return this.nextZIndex++;
    }

    /**
     * Calculate tooltip position
     * @param {HTMLElement} trigger - The trigger element
     * @param {HTMLElement} tooltip - The tooltip element
     * @param {string} position - Preferred position ('top', 'bottom', 'left', 'right', 'auto')
     * @returns {Object} Position coordinates {x, y, finalPosition}
     */
    calculatePosition(trigger, tooltip, position = 'auto') {
        const triggerRect = trigger.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const offset = this.options.offset;

        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const scrollX = window.scrollX;
        const scrollY = window.scrollY;

        // Calculate available space in each direction
        const spaceTop = triggerRect.top;
        const spaceBottom = viewportHeight - triggerRect.bottom;
        const spaceLeft = triggerRect.left;
        const spaceRight = viewportWidth - triggerRect.right;

        let finalPosition = position;

        // Auto-detect best position if set to 'auto'
        if (position === 'auto') {
            if (spaceTop > tooltipRect.height + offset) {
                finalPosition = 'top';
            } else if (spaceBottom > tooltipRect.height + offset) {
                finalPosition = 'bottom';
            } else if (spaceRight > tooltipRect.width + offset) {
                finalPosition = 'right';
            } else if (spaceLeft > tooltipRect.width + offset) {
                finalPosition = 'left';
            } else {
                finalPosition = 'bottom'; // Default fallback
            }
        }

        let x, y;

        switch (finalPosition) {
            case 'top':
                x = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
                y = triggerRect.top + scrollY - tooltipRect.height - offset;
                break;

            case 'bottom':
                x = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
                y = triggerRect.bottom + scrollY + offset;
                break;

            case 'left':
                x = triggerRect.left + scrollX - tooltipRect.width - offset;
                y = triggerRect.top + scrollY + (triggerRect.height - tooltipRect.height) / 2;
                break;

            case 'right':
                x = triggerRect.right + scrollX + offset;
                y = triggerRect.top + scrollY + (triggerRect.height - tooltipRect.height) / 2;
                break;

            default:
                x = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
                y = triggerRect.bottom + scrollY + offset;
                finalPosition = 'bottom';
        }

        // Ensure tooltip stays within viewport bounds
        x = Math.max(offset, Math.min(x, viewportWidth - tooltipRect.width - offset));
        y = Math.max(offset, Math.min(y, viewportHeight - tooltipRect.height - offset));

        return {
            x,
            y,
            finalPosition
        };
    }

    /**
     * Show tooltip for an element
     * @param {HTMLElement} trigger - The trigger element
     * @param {string} content - Tooltip content
     * @param {Object} options - Display options
     */
    show(trigger, content, options = {}) {
        const type = options.type || 'tooltip';
        const position = options.position || 'auto';

        // Check if tooltip already exists for this trigger
        if (this.tooltips.has(trigger)) {
            return;
        }

        // Create tooltip
        const tooltip = this.createTooltip(content, type);
        this.tooltips.set(trigger, tooltip);
        this.activeTooltips.push(tooltip);

        // Add position class
        tooltip.classList.add(`tooltip-position-${position}`);

        // Calculate position after a frame to get accurate dimensions
        requestAnimationFrame(() => {
            const pos = this.calculatePosition(trigger, tooltip, position);

            // Update position
            tooltip.style.left = `${pos.x}px`;
            tooltip.style.top = `${pos.y}px`;

            // Update position class if auto-detected
            if (position === 'auto') {
                tooltip.classList.remove(`tooltip-position-auto`);
                tooltip.classList.add(`tooltip-position-${pos.finalPosition}`);
            }

            // Animate in
            requestAnimationFrame(() => {
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateY(0)';
            });
        });
    }

    /**
     * Hide tooltip for an element
     * @param {HTMLElement} trigger - The trigger element
     */
    hide(trigger) {
        const tooltip = this.tooltips.get(trigger);
        if (!tooltip) return;

        // Animate out
        tooltip.style.opacity = '0';
        tooltip.style.transform = 'translateY(10px)';

        // Remove after animation
        setTimeout(() => {
            tooltip.remove();
            this.tooltips.delete(trigger);

            const index = this.activeTooltips.indexOf(tooltip);
            if (index > -1) {
                this.activeTooltips.splice(index, 1);
            }
        }, this.options.animationDuration);
    }

    /**
     * Hide all active tooltips
     */
    hideAll() {
        this.tooltips.forEach((tooltip, trigger) => {
            this.hide(trigger);
        });
    }

    /**
     * Attach tooltip to an element
     * @param {HTMLElement} element - The element to attach tooltip to
     * @param {Object} options - Configuration options
     */
    attach(element, options = {}) {
        const content = options.content || element.getAttribute('data-tooltip') || element.getAttribute('title');
        const trigger = options.trigger || 'hover'; // 'hover' or 'click'
        const position = options.position || element.getAttribute('data-tooltip-position') || 'auto';
        const type = options.type || 'tooltip';

        if (!content) return;

        // Remove title attribute to prevent native tooltip
        if (element.hasAttribute('title')) {
            element.removeAttribute('title');
        }

        if (trigger === 'hover') {
            element.addEventListener('mouseenter', () => {
                this.show(element, content, {
                    position,
                    type
                });
            });

            element.addEventListener('mouseleave', () => {
                this.hide(element);
            });
        } else if (trigger === 'click') {
            element.addEventListener('click', (e) => {
                e.stopPropagation();

                if (this.tooltips.has(element)) {
                    this.hide(element);
                } else {
                    this.show(element, content, {
                        position,
                        type
                    });
                }
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!element.contains(e.target) && this.tooltips.has(element)) {
                    this.hide(element);
                }
            });
        }
    }

    /**
     * Initialize tooltips for all elements with data-tooltip attribute
     * @static
     * @param {Object} options - Configuration options
     * @returns {TooltipManager} The tooltip manager instance
     */
    static initAll(options = {}) {
        const manager = new TooltipManager(options);

        // Find all elements with data-tooltip attribute
        const tooltipElements = document.querySelectorAll('[data-tooltip]');

        tooltipElements.forEach(element => {
            const trigger = element.getAttribute('data-tooltip-trigger') || 'hover';
            const position = element.getAttribute('data-tooltip-position') || 'auto';
            const type = element.getAttribute('data-tooltip-type') || 'tooltip';

            manager.attach(element, {
                trigger,
                position,
                type
            });
        });

        console.log(`TooltipManager initialized for ${tooltipElements.length} elements`);
        return manager;
    }
}

// ============================================
// ActionButton Class
// ============================================
/**
 * Manages action button states with visual feedback
 * @class ActionButton
 */
class ActionButton {
    /**
     * @param {HTMLElement} button - The button element
     * @param {Object} options - Configuration options
     */
    constructor(button, options = {}) {
        this.button = button;
        this.options = {
            successDuration: options.successDuration || 2000,
            errorDuration: options.errorDuration || 2000,
            loadingText: options.loadingText || '',
            successText: options.successText || '',
            errorText: options.errorText || ''
        };

        this.originalContent = null;
        this.currentState = 'normal';
        this.stateTimeout = null;

        this.init();
    }

    /**
     * Initialize the button
     */
    init() {
        // Ensure button has btn-action class
        if (!this.button.classList.contains('btn-action')) {
            this.button.classList.add('btn-action');
        }

        // Store original content
        this.originalContent = this.button.innerHTML;

        // Wrap content if not already wrapped
        if (!this.button.querySelector('.btn-content')) {
            this.button.innerHTML = `
                <span class="btn-content">${this.originalContent}</span>
                <span class="btn-spinner"></span>
                <i class="btn-state-icon icon-success fas fa-check"></i>
                <i class="btn-state-icon icon-error fas fa-times"></i>
            `;
        }

        // Apply ripple effect if available
        if (typeof RippleEffect !== 'undefined' && RippleEffect.apply) {
            RippleEffect.apply(this.button);
        }
    }

    /**
     * Set button to loading state
     * @param {string} text - Optional loading text
     */
    setLoading(text = null) {
        this.clearStateTimeout();
        this.currentState = 'loading';

        this.button.classList.remove('btn-success', 'btn-error');
        this.button.classList.add('btn-loading');
        this.button.disabled = true;

        if (text || this.options.loadingText) {
            const content = this.button.querySelector('.btn-content');
            if (content) {
                content.textContent = text || this.options.loadingText;
            }
        }
    }

    /**
     * Set button to success state
     * @param {string} text - Optional success text
     * @param {number} duration - Duration before returning to normal (ms)
     */
    setSuccess(text = null, duration = null) {
        this.clearStateTimeout();
        this.currentState = 'success';

        this.button.classList.remove('btn-loading', 'btn-error');
        this.button.classList.add('btn-success');
        this.button.disabled = false;

        const successMessage = text || this.options.successText || 'Operação concluída com sucesso';

        const content = this.button.querySelector('.btn-content');
        if (content) content.textContent = successMessage;

        // Announce success to screen readers
        if (window.dashboardInstance ?.accessibilityManager) {
            window.dashboardInstance.accessibilityManager.announce(successMessage);
        }

        // Auto-reset after duration
        const resetDuration = duration !== null ? duration : this.options.successDuration;
        if (resetDuration > 0) {
            this.stateTimeout = setTimeout(() => this.reset(), resetDuration);
        }
    }

    /**
     * Set button to error state
     * @param {string} text - Optional error text
     * @param {number} duration - Duration before returning to normal (ms)
     */
    setError(text = null, duration = null) {
        this.clearStateTimeout();
        this.currentState = 'error';

        this.button.classList.remove('btn-loading', 'btn-success');
        this.button.classList.add('btn-error');
        this.button.disabled = false;

        const errorMessage = text || this.options.errorText || 'Erro na operação';

        const content = this.button.querySelector('.btn-content');
        if (content) content.textContent = errorMessage;

        // Announce error to screen readers with assertive priority
        if (window.dashboardInstance ?.accessibilityManager) {
            window.dashboardInstance.accessibilityManager.announce(errorMessage, 'assertive');
        }

        // Auto-reset after duration
        const resetDuration = duration !== null ? duration : this.options.errorDuration;
        if (resetDuration > 0) {
            this.stateTimeout = setTimeout(() => this.reset(), resetDuration);
        }
    }

    /**
     * Reset button to normal state
     */
    reset() {
        this.clearStateTimeout();
        this.currentState = 'normal';

        this.button.classList.remove('btn-loading', 'btn-success', 'btn-error');
        this.button.disabled = false;

        // Restore original content
        const content = this.button.querySelector('.btn-content');
        if (content && this.originalContent) {
            // Extract text from original content (remove wrapper if present)
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = this.originalContent;
            const textContent = tempDiv.textContent || tempDiv.innerText;
            content.innerHTML = this.originalContent.includes('<') ? this.originalContent : textContent;
        }
    }

    /**
     * Clear state timeout
     */
    clearStateTimeout() {
        if (this.stateTimeout) {
            clearTimeout(this.stateTimeout);
            this.stateTimeout = null;
        }
    }

    /**
     * Get current button state
     * @returns {string} Current state ('normal', 'loading', 'success', 'error')
     */
    getState() {
        return this.currentState;
    }

    /**
     * Simulate an async action with automatic state management
     * @param {Function} action - Async function to execute
     * @param {Object} options - State text options
     * @returns {Promise} Promise that resolves with action result
     */
    async executeAction(action, options = {}) {
        try {
            this.setLoading(options.loadingText);
            const result = await action();
            this.setSuccess(options.successText);
            return result;
        } catch (error) {
            this.setError(options.errorText || 'Erro');
            throw error;
        }
    }

    /**
     * Destroy the button instance and clean up
     */
    destroy() {
        this.clearStateTimeout();
        this.button.classList.remove('btn-action', 'btn-loading', 'btn-success', 'btn-error');
        this.button.disabled = false;
    }

    /**
     * Create ActionButton instances for all buttons with data-action attribute
     * @static
     * @param {Object} options - Default options for all buttons
     * @returns {Map} Map of button elements to ActionButton instances
     */
    static initAll(options = {}) {
        const buttons = document.querySelectorAll('[data-action], .btn-action');
        const instances = new Map();

        buttons.forEach(button => {
            const instance = new ActionButton(button, options);
            instances.set(button, instance);
        });

        console.log(`ActionButton initialized for ${instances.size} buttons`);
        return instances;
    }

    /**
     * Get ActionButton instance for a button element
     * @static
     * @param {HTMLElement} button - The button element
     * @param {Map} instances - Map of instances from initAll()
     * @returns {ActionButton|null} The ActionButton instance or null
     */
    static getInstance(button, instances) {
        return instances.get(button) || null;
    }
}

// ============================================
// ContentTransition Class
// ============================================
/**
 * Manages smooth content transitions with fade and slide effects
 * @class ContentTransition
 */
class ContentTransition {
    /**
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        this.options = {
            fadeDuration: options.fadeDuration || 400,
            slideDistance: options.slideDistance || 30,
            highlightDuration: options.highlightDuration || 2000,
            maintainScroll: options.maintainScroll !== false
        };

        this.isTransitioning = false;
        this.scrollPositions = new Map();
    }

    /**
     * Fade transition for content swapping
     * @param {HTMLElement} container - The container element
     * @param {Function|string} newContentOrCallback - New content HTML or callback that returns content
     * @param {Object} options - Transition options
     * @returns {Promise} Promise that resolves when transition is complete
     */
    async fadeTransition(container, newContentOrCallback, options = {}) {
        if (this.isTransitioning) {
            console.warn('Transition already in progress');
            return;
        }

        this.isTransitioning = true;
        const fadeDuration = options.fadeDuration || this.options.fadeDuration;
        const maintainScroll = options.maintainScroll !== undefined ? options.maintainScroll : this.options.maintainScroll;
        const announceChange = options.announceChange !== false;

        // Store scroll position if needed
        let scrollPosition = 0;
        if (maintainScroll) {
            scrollPosition = window.scrollY || window.pageYOffset;
            this.scrollPositions.set(container, scrollPosition);
        }

        try {
            // Announce content loading
            if (announceChange && window.dashboardInstance ?.accessibilityManager) {
                window.dashboardInstance.accessibilityManager.announce('Carregando novo conteúdo');
            }

            // Phase 1: Fade out
            await this.fadeOut(container, fadeDuration);

            // Phase 2: Update content
            if (typeof newContentOrCallback === 'function') {
                const newContent = await newContentOrCallback();
                container.innerHTML = newContent;
            } else {
                container.innerHTML = newContentOrCallback;
            }

            // Restore scroll position if needed
            if (maintainScroll) {
                window.scrollTo(0, scrollPosition);
            }

            // Phase 3: Fade in
            await this.fadeIn(container, fadeDuration);

            // Announce content loaded
            if (announceChange && window.dashboardInstance ?.accessibilityManager) {
                window.dashboardInstance.accessibilityManager.announce('Conteúdo atualizado');
            }

        } finally {
            this.isTransitioning = false;
        }
    }

    /**
     * Fade out an element
     * @param {HTMLElement} element - Element to fade out
     * @param {number} duration - Fade duration in ms
     * @returns {Promise} Promise that resolves when fade out is complete
     */
    fadeOut(element, duration = 400) {
        return new Promise(resolve => {
            element.style.transition = `opacity ${duration}ms ease-out`;
            element.style.opacity = '0';

            setTimeout(resolve, duration);
        });
    }

    /**
     * Fade in an element
     * @param {HTMLElement} element - Element to fade in
     * @param {number} duration - Fade duration in ms
     * @returns {Promise} Promise that resolves when fade in is complete
     */
    fadeIn(element, duration = 400) {
        return new Promise(resolve => {
            // Ensure element starts at opacity 0
            element.style.opacity = '0';

            // Force reflow
            element.offsetHeight;

            element.style.transition = `opacity ${duration}ms ease-in`;
            element.style.opacity = '1';

            setTimeout(() => {
                // Clean up inline styles
                element.style.transition = '';
                resolve();
            }, duration);
        });
    }

    /**
     * Add slide animation for filters
     * @param {HTMLElement} filterElement - The filter element to animate
     * @param {string} direction - Slide direction ('in' or 'out')
     * @param {Object} options - Animation options
     * @returns {Promise} Promise that resolves when animation is complete
     */
    slideFilter(filterElement, direction = 'in', options = {}) {
        return new Promise(resolve => {
            const duration = options.duration || 400;
            const distance = options.distance || this.options.slideDistance;

            if (direction === 'in') {
                // Slide in from left
                filterElement.style.cssText = `
                    opacity: 0;
                    transform: translateX(-${distance}px);
                    transition: opacity ${duration}ms ease-out, transform ${duration}ms cubic-bezier(0.175, 0.885, 0.32, 1.275);
                `;

                // Force reflow
                filterElement.offsetHeight;

                requestAnimationFrame(() => {
                    filterElement.style.opacity = '1';
                    filterElement.style.transform = 'translateX(0)';

                    setTimeout(() => {
                        filterElement.style.cssText = '';
                        resolve();
                    }, duration);
                });
            } else {
                // Slide out to right
                filterElement.style.transition = `opacity ${duration}ms ease-in, transform ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
                filterElement.style.opacity = '0';
                filterElement.style.transform = `translateX(${distance}px)`;

                setTimeout(() => {
                    filterElement.remove();
                    resolve();
                }, duration);
            }
        });
    }

    /**
     * Highlight updated data with pulse effect
     * @param {HTMLElement} element - Element to highlight
     * @param {Object} options - Highlight options
     * @returns {Promise} Promise that resolves when highlight is complete
     */
    highlightUpdate(element, options = {}) {
        return new Promise(resolve => {
            const duration = options.duration || this.options.highlightDuration;
            const color = options.color || 'rgba(102, 126, 234, 0.2)';
            const pulseCount = options.pulseCount || 2;

            // Store original styles
            const originalBackground = element.style.background;
            const originalTransition = element.style.transition;

            // Add highlight class for animation
            element.classList.add('data-highlight');

            // Apply pulse animation
            element.style.cssText = `
                ${element.style.cssText}
                animation: dataHighlightPulse ${duration}ms ease-in-out;
                animation-iteration-count: ${pulseCount};
            `;

            // Create keyframes if not already defined
            if (!document.getElementById('data-highlight-keyframes')) {
                const style = document.createElement('style');
                style.id = 'data-highlight-keyframes';
                style.textContent = `
                    @keyframes dataHighlightPulse {
                        0%, 100% {
                            background: transparent;
                            transform: scale(1);
                        }
                        50% {
                            background: ${color};
                            transform: scale(1.02);
                        }
                    }
                `;
                document.head.appendChild(style);
            }

            // Remove highlight after animation
            setTimeout(() => {
                element.classList.remove('data-highlight');
                element.style.animation = '';
                element.style.background = originalBackground;
                element.style.transition = originalTransition;
                resolve();
            }, duration * pulseCount);
        });
    }

    /**
     * Batch highlight multiple elements with staggered timing
     * @param {NodeList|Array} elements - Elements to highlight
     * @param {Object} options - Highlight options
     * @returns {Promise} Promise that resolves when all highlights are complete
     */
    async highlightMultiple(elements, options = {}) {
        const staggerDelay = options.staggerDelay || 100;
        const promises = [];

        elements.forEach((element, index) => {
            const promise = new Promise(resolve => {
                setTimeout(() => {
                    this.highlightUpdate(element, options).then(resolve);
                }, index * staggerDelay);
            });
            promises.push(promise);
        });

        return Promise.all(promises);
    }

    /**
     * Transition table rows with fade and reorder
     * @param {HTMLElement} tbody - Table body element
     * @param {Array} newRowsData - Array of new row data
     * @param {Function} rowRenderer - Function to render a row from data
     * @param {Object} options - Transition options
     * @returns {Promise} Promise that resolves when transition is complete
     */
    async transitionTableRows(tbody, newRowsData, rowRenderer, options = {}) {
        const fadeDuration = options.fadeDuration || this.options.fadeDuration;
        const maintainScroll = options.maintainScroll !== undefined ? options.maintainScroll : this.options.maintainScroll;

        // Store scroll position
        let scrollPosition = 0;
        if (maintainScroll) {
            scrollPosition = window.scrollY || window.pageYOffset;
        }

        // Fade out existing rows
        const existingRows = Array.from(tbody.querySelectorAll('tr'));
        await Promise.all(existingRows.map(row => this.fadeOut(row, fadeDuration / 2)));

        // Remove old rows
        existingRows.forEach(row => row.remove());

        // Add new rows
        newRowsData.forEach((data, index) => {
            const row = rowRenderer(data);
            row.style.opacity = '0';
            row.setAttribute('data-animate', 'slideInRight');
            row.style.animationDelay = `${index * 0.05}s`;
            tbody.appendChild(row);
        });

        // Restore scroll position
        if (maintainScroll) {
            window.scrollTo(0, scrollPosition);
        }

        // Fade in new rows
        const newRows = Array.from(tbody.querySelectorAll('tr'));
        await Promise.all(newRows.map((row, index) => {
            return new Promise(resolve => {
                setTimeout(() => {
                    this.fadeIn(row, fadeDuration / 2).then(resolve);
                }, index * 50);
            });
        }));
    }

    /**
     * Apply filter with slide animation
     * @param {HTMLElement} filterContainer - Container for filter badges
     * @param {string} filterText - Filter text to display
     * @param {Function} onRemove - Callback when filter is removed
     * @returns {HTMLElement} The created filter badge element
     */
    addFilterBadge(filterContainer, filterText, onRemove) {
        const badge = document.createElement('span');
        badge.className = 'filter-badge badge badge-modern bg-primary';
        badge.setAttribute('role', 'status');
        badge.innerHTML = `
            ${filterText}
            <i class="fas fa-times ms-2" style="cursor: pointer;" aria-label="Remover filtro ${filterText}"></i>
        `;

        // Add remove handler
        const removeIcon = badge.querySelector('.fa-times');
        removeIcon.addEventListener('click', () => {
            // Announce filter removal
            if (window.dashboardInstance ?.accessibilityManager) {
                window.dashboardInstance.accessibilityManager.announce(`Filtro ${filterText} removido`);
            }

            this.slideFilter(badge, 'out').then(() => {
                if (onRemove) onRemove();
            });
        });

        // Add to container with slide animation
        filterContainer.appendChild(badge);
        this.slideFilter(badge, 'in');

        // Announce filter added
        if (window.dashboardInstance ?.accessibilityManager) {
            window.dashboardInstance.accessibilityManager.announce(`Filtro ${filterText} adicionado`);
        }

        return badge;
    }

    /**
     * Clear all filters with animation
     * @param {HTMLElement} filterContainer - Container with filter badges
     * @returns {Promise} Promise that resolves when all filters are removed
     */
    async clearAllFilters(filterContainer) {
        const badges = Array.from(filterContainer.querySelectorAll('.filter-badge'));
        const badgeCount = badges.length;

        if (badgeCount === 0) {
            return Promise.resolve();
        }

        // Announce clearing filters
        if (window.dashboardInstance ?.accessibilityManager) {
            window.dashboardInstance.accessibilityManager.announce(`Removendo ${badgeCount} filtro${badgeCount > 1 ? 's' : ''}`);
        }

        const promises = badges.map((badge, index) => {
            return new Promise(resolve => {
                setTimeout(() => {
                    this.slideFilter(badge, 'out').then(resolve);
                }, index * 50);
            });
        });

        await Promise.all(promises);

        // Announce filters cleared
        if (window.dashboardInstance ?.accessibilityManager) {
            window.dashboardInstance.accessibilityManager.announce('Todos os filtros foram removidos');
        }
    }

    /**
     * Smooth scroll to element while maintaining context
     * @param {HTMLElement} element - Element to scroll to
     * @param {Object} options - Scroll options
     */
    scrollToElement(element, options = {}) {
        const offset = options.offset || 0;
        const behavior = options.behavior || 'smooth';

        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: behavior
        });
    }

    /**
     * Create a loading overlay during transitions
     * @param {HTMLElement} container - Container to overlay
     * @returns {HTMLElement} The overlay element
     */
    createLoadingOverlay(container) {
        const overlay = document.createElement('div');
        overlay.className = 'content-transition-overlay';
        overlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            transition: opacity 300ms ease;
        `;

        overlay.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        `;

        // Ensure container has position relative
        const position = window.getComputedStyle(container).position;
        if (position === 'static') {
            container.style.position = 'relative';
        }

        container.appendChild(overlay);

        // Fade in overlay
        requestAnimationFrame(() => {
            overlay.style.opacity = '1';
        });

        return overlay;
    }

    /**
     * Remove loading overlay
     * @param {HTMLElement} overlay - The overlay element to remove
     * @returns {Promise} Promise that resolves when overlay is removed
     */
    removeLoadingOverlay(overlay) {
        return new Promise(resolve => {
            overlay.style.opacity = '0';

            setTimeout(() => {
                overlay.remove();
                resolve();
            }, 300);
        });
    }

    /**
     * Initialize content transition system
     * @static
     * @param {Object} options - Configuration options
     * @returns {ContentTransition} The content transition instance
     */
    static init(options = {}) {
        const instance = new ContentTransition(options);
        console.log('ContentTransition system initialized');
        return instance;
    }
}

// ============================================
// AccessibilityManager Class
// ============================================
/**
 * Manages accessibility preferences and adaptations
 * @class AccessibilityManager
 */
class AccessibilityManager {
    /**
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        this.options = {
            respectReducedMotion: options.respectReducedMotion !== false,
            respectColorScheme: options.respectColorScheme !== false,
            enableAriaLive: options.enableAriaLive !== false
        };

        this.prefersReducedMotion = false;
        this.prefersColorScheme = 'light';
        this.supportsBackdropFilter = false;
        this.ariaLiveRegion = null;

        this.init();
    }

    /**
     * Initialize accessibility detection and setup
     */
    init() {
        console.log('Initializing AccessibilityManager...');

        // Detect prefers-reduced-motion
        this.detectReducedMotion();

        // Detect color scheme preference
        this.detectColorScheme();

        // Detect backdrop-filter support
        this.detectBackdropFilterSupport();

        // Setup ARIA live region
        if (this.options.enableAriaLive) {
            this.setupAriaLiveRegion();
        }

        // Listen for preference changes
        this.setupPreferenceListeners();

        console.log('AccessibilityManager initialized', {
            reducedMotion: this.prefersReducedMotion,
            colorScheme: this.prefersColorScheme,
            backdropFilter: this.supportsBackdropFilter
        });
    }

    /**
     * Detect prefers-reduced-motion preference
     */
    detectReducedMotion() {
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        this.prefersReducedMotion = mediaQuery.matches;

        if (this.prefersReducedMotion && this.options.respectReducedMotion) {
            document.body.classList.add('reduced-motion');
            console.log('Reduced motion preference detected - applying simplified animations');
            this.applyReducedMotionStyles();
        } else {
            document.body.classList.remove('reduced-motion');
        }
    }

    /**
     * Detect color scheme preference
     */
    detectColorScheme() {
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        this.prefersColorScheme = darkModeQuery.matches ? 'dark' : 'light';

        if (this.options.respectColorScheme) {
            document.body.setAttribute('data-color-scheme', this.prefersColorScheme);
        }
    }

    /**
     * Detect backdrop-filter support
     */
    detectBackdropFilterSupport() {
        // Check if backdrop-filter is supported
        const testElement = document.createElement('div');
        testElement.style.backdropFilter = 'blur(10px)';
        testElement.style.webkitBackdropFilter = 'blur(10px)';

        this.supportsBackdropFilter =
            testElement.style.backdropFilter !== '' ||
            testElement.style.webkitBackdropFilter !== '';

        if (!this.supportsBackdropFilter) {
            document.body.classList.add('no-backdrop-filter');
            console.log('Backdrop-filter not supported - applying fallback styles');
            this.applyBackdropFilterFallback();
        }
    }

    /**
     * Apply reduced motion styles
     */
    applyReducedMotionStyles() {
        // Create a style element with reduced motion overrides
        const styleId = 'reduced-motion-overrides';

        // Remove existing style if present
        const existingStyle = document.getElementById(styleId);
        if (existingStyle) {
            existingStyle.remove();
        }

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            /* Reduced Motion Overrides */
            .reduced-motion *,
            .reduced-motion *::before,
            .reduced-motion *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }

            /* Disable complex animations */
            .reduced-motion .stats-card::before,
            .reduced-motion .page-header::before,
            .reduced-motion .particle,
            .reduced-motion .stats-trend i {
                animation: none !important;
            }

            /* Disable 3D transforms */
            .reduced-motion .stats-card:hover,
            .reduced-motion .card-3d:hover {
                transform: none !important;
            }

            /* Simplify hover effects */
            .reduced-motion .stats-card:hover {
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
            }

            /* Disable gradient animations */
            .reduced-motion .page-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                animation: none !important;
            }

            /* Disable shimmer effects */
            .reduced-motion .page-header h1:
           display: none !important;
            }

            /* Simplify badge animations */
            .reduced-motion .badge-animated {
                animation: none !important;
            }

            /* Disable ripple effects */
            .reduced-motion .ripple-effect {
                display: none !important;
            }

            /* Simplify table row animations */
            .reduced-motion .table-modern tbody tr:hover {
                transform: none !important;
                background: rgba(102, 126, 234, 0.05) !important;
            }

            /* Disable floating animations */
            .reduced-motion .particle {
                display: none !important;
            }

            /* Simplify button states */
            .reduced-motion .btn-action:hover {
                transform: none !important;
            }

            /* Disable skeleton animations */
            .reduced-motion .skeleton {
                animation: none !important;
                background: #f0f0f0 !important;
            }
        `;

        document.head.appendChild(style);
    }

    /**
     * Apply backdrop-filter fallback styles
     */
    applyBackdropFilterFallback() {
        const styleId = 'backdrop-filter-fallback';

        // Remove existing style if present
        const existingStyle = document.getElementById(styleId);
        if (existingStyle) {
            existingStyle.remove();
        }

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            /* Backdrop Filter Fallback */
            .no-backdrop-filter .stats-card,
            .no-backdrop-filter .glass-card,
            .no-backdrop-filter .glass-bg {
                background: rgba(255, 255, 255, 0.95) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
            }

            .no-backdrop-filter .tooltip-modern {
                background: rgba(255, 255, 255, 0.98) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2) !important;
            }

            /* Dark mode fallback */
            @media (prefers-color-scheme: dark) {
                .no-backdrop-filter .stats-card,
                .no-backdrop-filter .glass-card,
                .no-backdrop-filter .glass-bg {
                    background: rgba(45, 45, 45, 0.95) !important;
                }

                .no-backdrop-filter .tooltip-modern {
                    background: rgba(45, 45, 45, 0.98) !important;
                }
            }
        `;

        document.head.appendChild(style);
    }

    /**
     * Setup ARIA live region for announcements
     */
    setupAriaLiveRegion() {
        // Check if already exists
        this.ariaLiveRegion = document.getElementById('aria-live-region');

        if (!this.ariaLiveRegion) {
            this.ariaLiveRegion = document.createElement('div');
            this.ariaLiveRegion.id = 'aria-live-region';
            this.ariaLiveRegion.setAttribute('role', 'status');
            this.ariaLiveRegion.setAttribute('aria-live', 'polite');
            this.ariaLiveRegion.setAttribute('aria-atomic', 'true');
            this.ariaLiveRegion.className = 'visually-hidden';

            // Add screen reader only styles
            this.ariaLiveRegion.style.cssText = `
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            `;

            document.body.appendChild(this.ariaLiveRegion);
            console.log('ARIA live region created');
        }
    }

    /**
     * Announce message to screen readers
     * @param {string} message - Message to announce
     * @param {string} priority - Priority level ('polite' or 'assertive')
     */
    announce(message, priority = 'polite') {
        if (!this.ariaLiveRegion) {
            console.warn('ARIA live region not initialized');
            return;
        }

        // Update aria-live attribute
        this.ariaLiveRegion.setAttribute('aria-live', priority);

        // Clear previous message
        this.ariaLiveRegion.textContent = '';

        // Set new message after a brief delay to ensure it's announced
        setTimeout(() => {
            this.ariaLiveRegion.textContent = message;
            console.log(`ARIA announcement (${priority}):`, message);

            // Clear message after 5 seconds
            setTimeout(() => {
                this.ariaLiveRegion.textContent = '';
            }, 5000);
        }, 100);
    }

    /**
     * Setup listeners for preference changes
     */
    setupPreferenceListeners() {
        // Listen for reduced motion changes
        const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

        // Modern browsers
        if (reducedMotionQuery.addEventListener) {
            reducedMotionQuery.addEventListener('change', (e) => {
                this.prefersReducedMotion = e.matches;
                this.detectReducedMotion();
                this.announce('Preferências de animação atualizadas');
            });
        } else if (reducedMotionQuery.addListener) {
            // Fallback for older browsers
            reducedMotionQuery.addListener((e) => {
                this.prefersReducedMotion = e.matches;
                this.detectReducedMotion();
                this.announce('Preferências de animação atualizadas');
            });
        }

        // Listen for color scheme changes
        const colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)');

        if (colorSchemeQuery.addEventListener) {
            colorSchemeQuery.addEventListener('change', (e) => {
                this.prefersColorScheme = e.matches ? 'dark' : 'light';
                this.detectColorScheme();
                this.announce(`Tema alterado para modo ${this.prefersColorScheme === 'dark' ? 'escuro' : 'claro'}`);
            });
        } else if (colorSchemeQuery.addListener) {
            colorSchemeQuery.addListener((e) => {
                this.prefersColorScheme = e.matches ? 'dark' : 'light';
                this.detectColorScheme();
                this.announce(`Tema alterado para modo ${this.prefersColorScheme === 'dark' ? 'escuro' : 'claro'}`);
            });
        }
    }

    /**
     * Check if reduced motion is enabled
     * @returns {boolean} True if reduced motion is enabled
     */
    isReducedMotion() {
        return this.prefersReducedMotion;
    }

    /**
     * Check if backdrop-filter is supported
     * @returns {boolean} True if backdrop-filter is supported
     */
    hasBackdropFilterSupport() {
        return this.supportsBackdropFilter;
    }

    /**
     * Get current color scheme preference
     * @returns {string} Color scheme ('light' or 'dark')
     */
    getColorScheme() {
        return this.prefersColorScheme;
    }

    /**
     * Manually enable reduced motion mode
     */
    enableReducedMotion() {
        this.prefersReducedMotion = true;
        document.body.classList.add('reduced-motion');
        this.applyReducedMotionStyles();
        this.announce('Modo de movimento reduzido ativado');
    }

    /**
     * Manually disable reduced motion mode
     */
    disableReducedMotion() {
        this.prefersReducedMotion = false;
        document.body.classList.remove('reduced-motion');

        const style = document.getElementById('reduced-motion-overrides');
        if (style) {
            style.remove();
        }

        this.announce('Modo de movimento reduzido desativado');
    }

    /**
     * Get accessibility status report
     * @returns {Object} Accessibility status
     */
    getStatus() {
        return {
            reducedMotion: this.prefersReducedMotion,
            colorScheme: this.prefersColorScheme,
            backdropFilter: this.supportsBackdropFilter,
            ariaLiveEnabled: this.ariaLiveRegion !== null
        };
    }

    /**
     * Initialize accessibility manager
     * @static
     * @param {Object} options - Configuration options
     * @returns {AccessibilityManager} The accessibility manager instance
     */
    static init(options = {}) {
        const manager = new AccessibilityManager(options);
        console.log('AccessibilityManager ready');
        return manager;
    }
}

// ============================================
// Dashboard Initialization
// ============================================
/**
 * Initialize all animation modules for the dashboard
 */
function initDashboard() {
    console.log('Initializing Modern Admin Dashboard Animation Engine...');

    // Initialize AccessibilityManager first
    const accessibilityManager = AccessibilityManager.init({
        respectReducedMotion: true,
        respectColorScheme: true,
        enableAriaLive: true
    });

    // Check if reduced motion is enabled
    if (accessibilityManager.isReducedMotion()) {
        console.log('Reduced motion mode active - skipping complex animations');

        // Still initialize basic functionality but skip heavy animations
        const dashboardInstance = {
            accessibilityManager,
            counters: [],
            observer: null,
            performanceMonitor: null,
            particleSystem: null,
            cursorEffects: [],
            tableAnimators: [],
            tooltipManager: null,
            actionButtons: new Map(),
            contentTransition: null
        };

        window.dashboardInstance = dashboardInstance;

        // Announce dashboard ready
        accessibilityManager.announce('Painel administrativo carregado');

        return dashboardInstance;
    }
    // Initialize CounterAnimator for all counter elements
    const counters = CounterAnimator.initAll();
    console.log(`Initialized ${counters.length} counter animations`);

    // Initialize RippleEffect for all ripple elements
    const rippleCount = RippleEffect.initAll();
    console.log(`Initialized ${rippleCount} ripple effects`);

    // Initialize AnimationObserver for viewport animations
    const observer = AnimationObserver.initAll();
    console.log('Animation observer initialized');

    // Initialize PerformanceMonitor
    const performanceMonitor = PerformanceMonitor.init({
        fpsThreshold: 30,
        checkInterval: 1000
    });
    console.log('Performance monitor started');

    // Initialize ParticleSystem with lazy loading
    let particleSystem = null;
    const initParticles = () => {
        if (!particleSystem) {
            const particleCount = window.innerWidth < 768 ? 25 : 50;
            particleSystem = ParticleSystem.initForContainer('.page-header', particleCount);
        }
    };

    // Lazy load particles when header is visible
    const headerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                initParticles();
                headerObserver.disconnect();
            }
        });
    }, {
        threshold: 0.1
    });

    const pageHeader = document.querySelector('.page-header');
    if (pageHeader) {
        headerObserver.observe(pageHeader);
    }

    // Initialize CursorFollowEffect with lazy loading
    let cursorEffects = [];
    const initCursorEffects = () => {
        if (cursorEffects.length === 0 && !('ontouchstart' in window)) {
            cursorEffects = CursorFollowEffect.applyToAll('.stats-card');
        }
    };

    // Lazy load cursor effects when cards are visible
    const cardsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                initCursorEffects();
                cardsObserver.disconnect();
            }
        });
    }, {
        threshold: 0.1
    });

    const statsCards = document.querySelectorAll('.stats-card');
    if (statsCards.length > 0) {
        cardsObserver.observe(statsCards[0]);
    }

    // Initialize TableAnimators
    const tableAnimators = TableAnimator.initAll();

    // Initialize TooltipManager
    const tooltipManager = TooltipManager.initAll({
        animationDuration: 200,
        offset: 10
    });

    // Initialize ActionButton
    const actionButtons = ActionButton.initAll({
        successDuration: 2000,
        errorDuration: 2000
    });

    // Initialize ContentTransition
    const contentTransition = ContentTransition.init({
        fadeDuration: 400,
        maintainScroll: true
    });

    // Apply will-change optimization
    applyWillChangeOptimization();

    // Apply CSS containment
    applyCSSContainment();

    // Setup visibility change handler for pause/resume
    setupVisibilityHandler(counters, particleSystem, performanceMonitor);

    // Setup debounced resize and scroll handlers
    setupDebouncedHandlers();

    // Create dashboard instance
    const dashboardInstance = {
        accessibilityManager,
        counters,
        observer,
        performanceMonitor,
        particleSystem,
        cursorEffects,
        tableAnimators,
        tooltipManager,
        actionButtons,
        contentTransition,
        // Lazy loading functions
        initParticles,
        initCursorEffects
    };

    // Store globally for demo purposes
    window.dashboardInstance = dashboardInstance;

    // Announce dashboard ready
    accessibilityManager.announce('Painel administrativo carregado');

    console.log('Dashboard initialization complete!');
    return dashboardInstance;
}

// ============================================
// Performance Optimization Functions
// ============================================

/**
 * Apply will-change property only during active animations
 */
function applyWillChangeOptimization() {
    console.log('Applying will-change optimization...');

    // Stats cards - add will-change on hover, remove on hover end
    const statsCards = document.querySelectorAll('.stats-card');
    statsCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.willChange = 'transform, box-shadow';
        });

        card.addEventListener('mouseleave', function() {
            // Remove will-change after transition completes
            setTimeout(() => {
                this.style.willChange = 'auto';
            }, 400);
        });

        // Also handle animation start/end
        card.addEventListener('animationstart', function() {
            this.style.willChange = 'transform, opacity';
        });

        card.addEventListener('animationend', function() {
            this.style.willChange = 'auto';
        });
    });

    // Table rows - add will-change during hover
    const tableRows = document.querySelectorAll('.table-modern tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.willChange = 'transform, background';
        });

        row.addEventListener('mouseleave', function() {
            setTimeout(() => {
                this.style.willChange = 'auto';
            }, 400);
        });
    });

    // Buttons - add will-change during interaction
    const buttons = document.querySelectorAll('.btn-action');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.willChange = 'transform, box-shadow';
        });

        button.addEventListener('mouseleave', function() {
            setTimeout(() => {
                this.style.willChange = 'auto';
            }, 300);
        });

        button.addEventListener('click', function() {
            this.style.willChange = 'transform, opacity';
            setTimeout(() => {
                this.style.willChange = 'auto';
            }, 600);
        });
    });

    console.log('will-change optimization applied to interactive elements');
}

/**
 * Apply CSS containment for isolated cards
 */
function applyCSSContainment() {
    console.log('Applying CSS containment...');

    // Apply containment to stats cards
    const statsCards = document.querySelectorAll('.stats-card');
    statsCards.forEach(card => {
        card.style.contain = 'layout style paint';
    });

    // Apply containment to content cards
    const contentCards = document.querySelectorAll('.content-card');
    contentCards.forEach(card => {
        card.style.contain = 'layout style paint';
    });

    // Apply containment to table rows
    const tableRows = document.querySelectorAll('.table-modern tbody tr');
    tableRows.forEach(row => {
        row.style.contain = 'layout style';
    });

    console.log('CSS containment applied to isolated components');
}

/**
 * Setup visibility change handler to pause/resume animations
 * @param {Array} counters - Counter animator instances
 * @param {ParticleSystem} particleSystem - Particle system instance
 * @param {PerformanceMonitor} performanceMonitor - Performance monitor instance
 */
function setupVisibilityHandler(counters, particleSystem, performanceMonitor) {
    console.log('Setting up visibility change handler...');

    let animationsPaused = false;

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            // Page is hidden - pause animations
            console.log('Page hidden - pausing animations');
            animationsPaused = true;

            // Cancel counter animations
            counters.forEach(counter => {
                if (counter && counter.cancel) {
                    counter.cancel();
                }
            });

            // Stop performance monitoring
            if (performanceMonitor && performanceMonitor.stopMonitoring) {
                performanceMonitor.stopMonitoring();
            }

            // Pause CSS animations
            document.body.classList.add('animations-paused');

            // Add CSS to pause animations
            const pauseStyle = document.createElement('style');
            pauseStyle.id = 'animation-pause-style';
            pauseStyle.textContent = `
                .animations-paused * {
                    animation-play-state: paused !important;
                }
            `;
            document.head.appendChild(pauseStyle);

        } else {
            // Page is visible - resume animations
            console.log('Page visible - resuming animations');
            animationsPaused = false;

            // Resume performance monitoring
            if (performanceMonitor && performanceMonitor.startMonitoring) {
                performanceMonitor.startMonitoring();
            }

            // Resume CSS animations
            document.body.classList.remove('animations-paused');

            // Remove pause style
            const pauseStyle = document.getElementById('animation-pause-style');
            if (pauseStyle) {
                pauseStyle.remove();
            }
        }
    });

    console.log('Visibility change handler configured');
}

/**
 * Debounce function to limit event handler execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 250) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Setup debounced resize and scroll handlers
 */
function setupDebouncedHandlers() {
    console.log('Setting up debounced event handlers...');

    // Debounced resize handler
    const handleResize = debounce(() => {
        console.log('Window resized - adjusting animations');

        // Adjust particle count for mobile
        const particleSystem = window.dashboardInstance ?.particleSystem;
        if (particleSystem && particleSystem.adjustParticleCount) {
            const particleCount = window.innerWidth < 768 ? 25 : 50;
            particleSystem.adjustParticleCount(particleCount);
        }

        // Reposition tooltips if any are active
        const tooltipManager = window.dashboardInstance ?.tooltipManager;
        if (tooltipManager && tooltipManager.hideAll) {
            tooltipManager.hideAll();
        }

        // Update will-change properties
        applyWillChangeOptimization();

        // Announce resize to screen readers
        if (window.dashboardInstance ?.accessibilityManager) {
            window.dashboardInstance.accessibilityManager.announce('Layout ajustado para novo tamanho de tela');
        }
    }, 250);

    // Debounced scroll handler
    const handleScroll = debounce(() => {
        // Hide tooltips on scroll
        const tooltipManager = window.dashboardInstance ?.tooltipManager;
        if (tooltipManager && tooltipManager.hideAll) {
            tooltipManager.hideAll();
        }

        // Check if elements need lazy loading
        checkLazyLoadElements();
    }, 150);

    // Attach event listeners
    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleScroll, {
        passive: true
    });

    console.log('Debounced handlers configured (resize: 250ms, scroll: 150ms)');
}

/**
 * Check and initialize lazy-loaded elements
 */
function checkLazyLoadElements() {
    const dashboardInstance = window.dashboardInstance;
    if (!dashboardInstance) return;

    // Lazy load particles if not initialized
    if (!dashboardInstance.particleSystem && dashboardInstance.initParticles) {
        const pageHeader = document.querySelector('.page-header');
        if (pageHeader && isElementInViewport(pageHeader)) {
            dashboardInstance.initParticles();
        }
    }

    // Lazy load cursor effects if not initialized
    if (dashboardInstance.cursorEffects.length === 0 && dashboardInstance.initCursorEffects) {
        const statsCards = document.querySelectorAll('.stats-card');
        if (statsCards.length > 0 && isElementInViewport(statsCards[0])) {
            dashboardInstance.initCursorEffects();
        }
    }
}

/**
 * Check if element is in viewport
 * @param {HTMLElement} element - Element to check
 * @returns {boolean} True if element is in viewport
 */
function isElementInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// ============================================
// Visibility Handler Setup
// ============================================

/**
 * Setup visibility change handler to pause/resume animations
 * @param {Array} counters - Counter animator instances
 * @param {ParticleSystem} particleSystem - Particle system instance
 * @param {PerformanceMonitor} performanceMonitor - Performance monitor instance
 */
function setupVisibilityHandler(counters, particleSystem, performanceMonitor) {
    console.log('Setting up visibility change handler...');

    let animationsPaused = false;

    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Page is hidden - pause animations
            console.log('Page hidden - pausing animations');
            animationsPaused = true;

            // Cancel counter animations
            counters.forEach(counter => {
                if (counter.cancel) {
                    counter.cancel();
                }
            });

            // Stop performance monitoring
            if (performanceMonitor && performanceMonitor.stopMonitoring) {
                performanceMonitor.stopMonitoring();
            }

            // Pause CSS animations
            document.body.classList.add('animations-paused');

            // Add CSS to pause animations
            if (!document.getElementById('pause-animations-style')) {
                const style = document.createElement('style');
                style.id = 'pause-animations-style';
                style.textContent = `
                    .animations-paused * {
                        animation-play-state: paused!important;
                    }
                `;
                document.head.appendChild(style);
            }

        } else {
            // Page is visible - resume animations
            console.log('Page visible - resuming animations');
            animationsPaused = false;

            // Resume performance monitoring
            if (performanceMonitor && performanceMonitor.startMonitoring) {
                performanceMonitor.startMonitoring();
            }

            // Resume CSS animations
            document.body.classList.remove('animations-paused');

            // Remove pause style
            const pauseStyle = document.getElementById('pause-animations-style');
            if (pauseStyle) {
                pauseStyle.remove();
            }
        }
    });

    console.log('Visibility change handler configured');
}

/**
 * Setup debounced resize and scroll handlers
 */
function setupDebouncedHandlers() {
    console.log('Setting up debounced event handlers...');

    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle function for scroll
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Debounced resize handler
    const handleResize = debounce(() => {
        console.log('Window resized - adjusting layout');

        // Adjust particle count for mobile
        const particleSystem = window.dashboardInstance ?.particleSystem;
        if (particleSystem && particleSystem.adjustParticleCount) {
            const newCount = window.innerWidth < 768 ? 25 : 50;
            particleSystem.adjustParticleCount(newCount);
        }

        // Reposition tooltips if any are active
        const tooltipManager = window.dashboardInstance ?.tooltipManager;
        if (tooltipManager && tooltipManager.hideAll) {
            tooltipManager.hideAll();
        }

        // Announce resize to screen readers
        const accessibilityManager = window.dashboardInstance ?.accessibilityManager;
        if (accessibilityManager && accessibilityManager.announce) {
            accessibilityManager.announce('Layout ajustado para novo tamanho de tela');
        }
    }, 250);

    // Throttled scroll handler
    const handleScroll = throttle(() => {
        // Update any scroll-dependent features
        // Currently just for future use
    }, 100);

    // Add event listeners
    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleScroll, {
        passive: true
    });

    console.log('Debounced handlers configured (resize: 250ms, scroll: 100ms)');
}

// ============================================
// Initialize on DOM Content Loaded
// ============================================
// Auto-initialize on DOM ready
// ============================================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    // DOM is already ready
    initDashboard();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        AccessibilityManager,
        CounterAnimator,
        RippleEffect,
        AnimationObserver,
        PerformanceMonitor,
        ParticleSystem,
        CursorFollowEffect,
        SkeletonLoader,
        TableAnimator,
        TooltipManager,
        ActionButton,
        ContentTransition,
        initDashboard
    };
}
