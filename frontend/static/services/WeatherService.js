/**
 * Service for fetching and processing weather data
 */
class WeatherService {
  constructor(apiKey) {
    if (!apiKey) {
      throw new Error('WeatherService: API key is required');
    }
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.openweathermap.org/data/2.5';
    this.cache = new Map();
    this.cacheExpiration = 30 * 60 * 1000; // 30 minutes
    
    // Validate API key format
    if (typeof apiKey !== 'string' || apiKey.length < 32) {
      console.warn('WeatherService: API key may be invalid');
    }
  }

  /**
   * Get user's location using browser geolocation
   * @returns {Promise<{lat: number, lon: number}>}
   */
  async getUserLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lon: position.coords.longitude
          });
        },
        (error) => {
          reject(error);
        }
      );
    });
  }

  /**
   * Get current weather for given coordinates
   * @param {number} lat Latitude
   * @param {number} lon Longitude
   * @returns {Promise<Object>} Weather data
   */
  async getCurrentWeather(lat, lon) {
    try {
      console.log('Fetching weather data for:', { lat, lon });
      
      const cacheKey = `weather-${lat}-${lon}`;
      const cachedData = this.cache.get(cacheKey);
      
      if (cachedData && Date.now() - cachedData.timestamp < this.cacheExpiration) {
        console.log('Using cached weather data');
        return cachedData.data;
      }

      console.log('Making API request to OpenWeather');
      const response = await fetch(
        `${this.baseUrl}/weather?lat=${lat}&lon=${lon}&appid=${this.apiKey}&units=metric`
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Weather API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('Weather data received:', data);
      
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });

      return data;
    } catch (error) {
      console.error('Weather service error:', error);
      if (error.message === 'Weather API authorization failed') {
        // If authorization failed, disable weather features
        console.warn('Disabling weather features due to API key issue');
        if (window.templateVars?.config) {
          window.templateVars.config.COLOR_FEATURES.weather_enabled = false;
        }
      }
      // Return a default weather object
      return this.getDefaultWeather();
    }
  }

  /**
   * Get weather attributes for color adjustments
   * @returns {Promise<Object>} Weather attributes
   */
  async getWeatherAttributes() {
    try {
      const location = await this.getUserLocation();
      const weather = await this.getCurrentWeather(location.lat, location.lon);
      
      if (!weather) {
        return this.getDefaultAttributes();
      }

      return {
        condition: weather.weather[0].main.toLowerCase(),
        temperature: weather.main.temp,
        cloudiness: weather.clouds?.all || 0,
        timestamp: new Date(weather.dt * 1000)
      };
    } catch (error) {
      console.error('Error getting weather attributes:', error);
      return this.getDefaultAttributes();
    }
  }

  /**
   * Get default weather data when API fails
   * @returns {Object} Default weather object
   */
  getDefaultWeather() {
    return {
      weather: [{ main: 'Clear', description: 'clear sky' }],
      main: { temp: 20, humidity: 50 },
      clouds: { all: 0 },
      dt: Date.now() / 1000
    };
  }

  /**
   * Get default weather attributes when API fails
   * @returns {Object} Default attributes
   */
  getDefaultAttributes() {
    return {
      condition: 'clear',
      temperature: 20,
      cloudiness: 0,
      timestamp: new Date()
    };
  }

  /**
   * Get season based on current date and hemisphere
   * @param {number} latitude User's latitude
   * @returns {string} Current season
   */
  getSeason(latitude) {
    const month = new Date().getMonth();
    const isNorthernHemisphere = latitude > 0;

    // Adjust season based on hemisphere
    if (isNorthernHemisphere) {
      if (month >= 2 && month <= 4) return 'spring';
      if (month >= 5 && month <= 7) return 'summer';
      if (month >= 8 && month <= 10) return 'fall';
      return 'winter';
    } else {
      if (month >= 2 && month <= 4) return 'fall';
      if (month >= 5 && month <= 7) return 'winter';
      if (month >= 8 && month <= 10) return 'spring';
      return 'summer';
    }
  }
}

export default WeatherService;
