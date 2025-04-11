import ColorExperienceGenerator from './ColorExperienceGenerator.js';

let colorGenerator;

// Initialize color generator and apply colors
async function initializeColors() {
    try {
        console.log('Initializing color generator...');
        
        // Initialize color generator (will get API key from meta tag)
        colorGenerator = new ColorExperienceGenerator();
        
        // Apply default palette immediately
        const defaultPalette = colorGenerator.getDefaultPalette();
        colorGenerator.applyPalette(defaultPalette);
        console.log('Applied default palette:', defaultPalette);
        
        // Set up transitions
        const root = document.documentElement;
        root.style.setProperty('--transition-all', 'all var(--transition-duration) ease-in-out');

        // Generate and apply dynamic palette
        console.log('Generating dynamic palette...');
        const dynamicPalette = await colorGenerator.generatePalette();
        colorGenerator.applyPalette(dynamicPalette);
        console.log('Applied dynamic palette:', dynamicPalette);

        // Start auto-updates
        colorGenerator.startAutoUpdate();
        console.log('Started auto-updates');

        // Re-apply colors when returning from background
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                console.log('Page visible, regenerating palette...');
                colorGenerator.generatePalette().then(palette => {
                    console.log('Regenerated palette:', palette);
                    colorGenerator.applyPalette(palette);
                });
            }
        });
    } catch (error) {
        console.error('Failed to initialize color generator:', error);
        // If initialization fails, ensure default colors are applied
        if (!colorGenerator) {
            colorGenerator = new ColorExperienceGenerator();
        }
        const fallbackPalette = colorGenerator.getDefaultPalette();
        console.log('Applying fallback palette:', fallbackPalette);
        colorGenerator.applyPalette(fallbackPalette);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeColors);
} else {
    initializeColors();
}
