import ColorUtils from './utils/ColorUtils.js';
import WeatherService from './services/WeatherService.js';

/**
 * Generates dynamic color palettes based on environmental factors
 */
class ColorExperienceGenerator {
  constructor() {
    // Get configuration from template variables
    const config = window.templateVars || {};
    const defaultFeatures = {
      weather_enabled: false,
      transitions_enabled: true,
      season_enabled: true,
      time_based: true
    };

    // Initialize features with defaults
    this.features = {
      ...defaultFeatures,
      ...(config.COLOR_FEATURES || {})
    };

    this.debug = config.DEBUG || false;
    this.currentPalette = null;
    this.updateInterval = 30 * 60 * 1000; // 30 minutes
    
    // Log initial configuration
    if (this.debug) {
      console.group('ColorExperienceGenerator Initialization');
      console.log('Config:', config);
      console.log('Features:', this.features);
      console.log('Debug mode:', this.debug);
    }
    
    // Initialize weather service if enabled and API key is available
    if (this.features.weather_enabled && config.OPENWEATHER_API_KEY) {
      try {
        this.weatherService = new WeatherService(config.OPENWEATHER_API_KEY);
        if (this.debug) console.log('Weather service initialized successfully');
      } catch (error) {
        console.error('Failed to initialize weather service:', error);
        this.features.weather_enabled = false;
      }
    } else {
      if (this.debug) {
        console.log('Weather features disabled:', {
          enabled: this.features.weather_enabled,
          hasApiKey: Boolean(config.OPENWEATHER_API_KEY)
        });
      }
      this.features.weather_enabled = false;
    }
    
    if (this.debug) console.groupEnd();
  }

  /**
   * Get time of day period
   * @returns {string} Period of day
   */
  getTimeOfDay() {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 21) return 'evening';
    return 'night';
  }

  /**
   * Get base hue for time of day
   * @param {string} timeOfDay Time period
   * @returns {number} Base hue value
   */
  getBaseHue(timeOfDay) {
    switch (timeOfDay) {
      case 'morning':
        return 60; // Soft yellow
      case 'afternoon':
        return 200; // Sky blue
      case 'evening':
        return 280; // Purple
      case 'night':
        return 240; // Deep blue
      default:
        return 200;
    }
  }

  /**
   * Adjust color attributes based on weather
   * @param {Object} weatherAttrs Weather attributes
   * @returns {Object} Adjusted color attributes
   */
  adjustForWeather(weatherAttrs) {
    let saturation = 60; // Default saturation
    let lightness = 50; // Default lightness

    // Adjust based on cloudiness
    if (weatherAttrs.cloudiness > 50) {
      saturation = Math.max(30, saturation - weatherAttrs.cloudiness / 3);
      lightness = Math.min(70, lightness + weatherAttrs.cloudiness / 4);
    }

    // Adjust based on weather condition
    switch (weatherAttrs.condition) {
      case 'rain':
      case 'drizzle':
        saturation = Math.max(30, saturation - 15);
        lightness = Math.max(40, lightness - 10);
        break;
      case 'snow':
        saturation = Math.max(20, saturation - 25);
        lightness = Math.min(85, lightness + 25);
        break;
      case 'thunderstorm':
        saturation = Math.min(80, saturation + 20);
        lightness = Math.max(30, lightness - 20);
        break;
      case 'clear':
        saturation = Math.min(85, saturation + 15);
        break;
    }

    // Temperature influence
    if (weatherAttrs.temperature < 10) {
      // Cool temperatures
      saturation = Math.max(40, saturation - 10);
      lightness = Math.min(70, lightness + 10);
    } else if (weatherAttrs.temperature > 25) {
      // Warm temperatures
      saturation = Math.min(90, saturation + 10);
      lightness = Math.max(45, lightness - 5);
    }

    return { saturation, lightness };
  }

  /**
   * Adjust hue based on season
   * @param {number} baseHue Starting hue
   * @param {string} season Current season
   * @returns {number} Adjusted hue
   */
  adjustForSeason(baseHue, season) {
    const seasonalAdjustments = {
      spring: 15,   // Shift toward greens
      summer: -10,  // Shift toward yellows
      fall: 25,     // Shift toward oranges
      winter: -15   // Shift toward blues
    };

    return (baseHue + (seasonalAdjustments[season] || 0)) % 360;
  }

  /**
   * Generate a complete color palette
   * @returns {Promise<Object>} Generated color palette
   */
  async generatePalette() {
    if (this.debug) {
      console.group('Generating Color Palette');
      console.time('Palette Generation');
      console.log('Starting palette generation...');
    }

    try {
      const timeOfDay = this.getTimeOfDay();
      if (this.debug) console.log('Time of day:', timeOfDay);
      let baseHue = this.getBaseHue(timeOfDay);
      let weatherAttrs = null;
      let season = 'summer'; // Default season

      // Get weather and season info if enabled
      if (this.features.weather_enabled && this.weatherService) {
        try {
          const location = await this.weatherService.getUserLocation();
          weatherAttrs = await this.weatherService.getWeatherAttributes();
          if (this.features.season_enabled) {
            season = this.weatherService.getSeason(location.lat);
            baseHue = this.adjustForSeason(baseHue, season);
          }
        } catch (error) {
          console.warn('Weather/season features error:', error);
          weatherAttrs = null;
        }
      }

      // Default color attributes
      let saturation = 60;
      let lightness = 50;

      // Adjust for weather if available
      if (weatherAttrs) {
        const adjustedAttrs = this.adjustForWeather(weatherAttrs);
        saturation = adjustedAttrs.saturation;
        lightness = adjustedAttrs.lightness;
      }

      if (this.debug) {
        console.log('Generating palette with:', {
          timeOfDay,
          season,
          weatherEnabled: this.features.weather_enabled,
          weatherAttrs,
          baseHue,
          saturation,
          lightness
        });
      }

      // Generate harmonious palette
      const palette = ColorUtils.generateHarmonics(baseHue, saturation, lightness);

      // Verify accessibility
      if (!ColorUtils.meetsAccessibilityStandards(
        palette.primary.main,
        'hsl(0, 0%, 100%)'  // White background
      )) {
        // Adjust lightness for better contrast
        const adjustedLightness = Math.max(45, lightness);
        return ColorUtils.generateHarmonics(baseHue, saturation, adjustedLightness);
      }

      this.currentPalette = palette;
      if (this.debug) {
        console.log('Final palette generated:', palette);
        console.timeEnd('Palette Generation');
        console.groupEnd();
      }
      return palette;
    } catch (error) {
      console.error('Error generating palette:', error);
      // Fallback to default palette
      return this.getDefaultPalette();
    }
  }

  /**
   * Get default color palette
   * @returns {Object} Default color palette
   */
  getDefaultPalette() {
    return ColorUtils.generateHarmonics(200, 60, 50);
  }

  /**
   * Start automatic palette updates
   */
  startAutoUpdate() {
    this.generatePalette(); // Initial generation
    setInterval(() => this.generatePalette(), this.updateInterval);
  }

  /**
   * Apply the current palette to the document
   * @param {Object} palette Optional palette to apply directly
   */
  applyPalette(palette) {
    if (this.debug) {
      console.group('Applying Color Palette');
      console.log('Input palette:', palette);
      console.log('Current palette:', this.currentPalette);
    }

    let colorsToApply = palette || this.currentPalette;
    if (!colorsToApply) {
      if (this.debug) console.warn('No palette to apply, using default');
      colorsToApply = this.getDefaultPalette();
      if (this.debug) console.log('Using default palette:', colorsToApply);
    }

    const root = document.documentElement;
    
    // Store previous colors for transition logging
    const previousColors = this.debug ? {
      primary: root.style.getPropertyValue('--primary-color'),
      secondary: root.style.getPropertyValue('--secondary-color')
    } : null;

    // Apply transitions if enabled
    if (this.features.transitions_enabled) {
      root.style.setProperty('--transition-duration', '1s');
      void root.offsetHeight; // Force reflow
    }

    // Apply colors
    const colorProps = {
      '--primary-color': colorsToApply.primary.main,
      '--primary-light': colorsToApply.primary.light,
      '--primary-dark': colorsToApply.primary.dark,
      '--secondary-color': colorsToApply.secondary.main,
      '--accent-first': colorsToApply.accent.first,
      '--accent-second': colorsToApply.accent.second
    };

    Object.entries(colorProps).forEach(([prop, value]) => {
      root.style.setProperty(prop, value);
    });

    if (this.debug) {
      console.log('Color Transition:', {
        from: previousColors,
        to: {
          primary: colorProps['--primary-color'],
          secondary: colorProps['--secondary-color']
        },
        transitionsEnabled: this.features.transitions_enabled
      });
      
      console.log('Applied Colors:', Object.fromEntries(
        Object.keys(colorProps).map(prop => [
          prop,
          root.style.getPropertyValue(prop)
        ])
      ));
      console.groupEnd();
    }
  }
}

export default ColorExperienceGenerator;
