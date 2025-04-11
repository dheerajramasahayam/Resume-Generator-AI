/**
 * Utility class for color manipulation and generation
 */
class ColorUtils {
  /**
   * Convert RGB to HSL
   * @param {number} r Red (0-255)
   * @param {number} g Green (0-255)
   * @param {number} b Blue (0-255)
   * @returns {[number, number, number]} [hue, saturation, lightness]
   */
  static rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      h /= 6;
    }

    return [h * 360, s * 100, l * 100];
  }

  /**
   * Convert HSL to RGB
   * @param {number} h Hue (0-360)
   * @param {number} s Saturation (0-100)
   * @param {number} l Lightness (0-100)
   * @returns {[number, number, number]} [red, green, blue]
   */
  static hslToRgb(h, s, l) {
    h /= 360;
    s /= 100;
    l /= 100;

    let r, g, b;

    if (s === 0) {
      r = g = b = l;
    } else {
      const hue2rgb = (p, q, t) => {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1/6) return p + (q - p) * 6 * t;
        if (t < 1/2) return q;
        if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
        return p;
      };

      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
  }

  /**
   * Calculate relative luminance for WCAG contrast calculations
   * @param {number} r Red (0-255)
   * @param {number} g Green (0-255)
   * @param {number} b Blue (0-255)
   * @returns {number} Relative luminance
   */
  static getLuminance(r, g, b) {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c /= 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  }

  /**
   * Calculate contrast ratio between two colors (WCAG)
   * @param {[number, number, number]} color1 RGB values
   * @param {[number, number, number]} color2 RGB values
   * @returns {number} Contrast ratio
   */
  static getContrastRatio(color1, color2) {
    const l1 = this.getLuminance(...color1);
    const l2 = this.getLuminance(...color2);
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    return (lighter + 0.05) / (darker + 0.05);
  }

  /**
   * Generate a complementary color using the golden ratio
   * @param {number} h Base hue (0-360)
   * @returns {number} Complementary hue
   */
  static getGoldenComplementary(h) {
    return (h + 360 * 0.618033988749895) % 360;
  }

  /**
   * Generate a harmonious color palette
   * @param {number} baseHue Base hue (0-360)
   * @param {number} baseSaturation Base saturation (0-100)
   * @param {number} baseLightness Base lightness (0-100)
   * @returns {Object} Color palette with primary, secondary, and accent colors
   */
  static generateHarmonics(baseHue, baseSaturation, baseLightness) {
    const complementaryHue = this.getGoldenComplementary(baseHue);
    const splitComplementary1 = (baseHue + 150) % 360;
    const splitComplementary2 = (baseHue + 210) % 360;
    const triadicHue1 = (baseHue + 120) % 360;
    const triadicHue2 = (baseHue + 240) % 360;
    const analogous1 = (baseHue + 30) % 360;
    const analogous2 = (baseHue - 30 + 360) % 360;

    // Generate shades with more variation
    const shades = {
      lightest: Math.min(baseLightness + 30, 95),
      lighter: Math.min(baseLightness + 15, 85),
      light: Math.min(baseLightness + 7, 75),
      main: baseLightness,
      dark: Math.max(baseLightness - 7, 25),
      darker: Math.max(baseLightness - 15, 15),
      darkest: Math.max(baseLightness - 30, 5)
    };

    // Generate saturations
    const saturations = {
      muted: Math.max(baseSaturation - 20, 20),
      normal: baseSaturation,
      vivid: Math.min(baseSaturation + 20, 100)
    };

    return {
      primary: {
        lightest: `hsl(${Math.round(baseHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.lightest)}%)`,
        lighter: `hsl(${Math.round(baseHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.lighter)}%)`,
        light: `hsl(${Math.round(baseHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.light)}%)`,
        main: `hsl(${Math.round(baseHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.main)}%)`,
        dark: `hsl(${Math.round(baseHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.dark)}%)`,
        darker: `hsl(${Math.round(baseHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.darker)}%)`,
        darkest: `hsl(${Math.round(baseHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.darkest)}%)`
      },
      secondary: {
        main: `hsl(${Math.round(complementaryHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.main)}%)`,
        light: `hsl(${Math.round(complementaryHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.light)}%)`,
        dark: `hsl(${Math.round(complementaryHue)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.dark)}%)`
      },
      accent: {
        first: `hsl(${Math.round(triadicHue1)}, ${Math.round(saturations.vivid)}%, ${Math.round(shades.main)}%)`,
        second: `hsl(${Math.round(triadicHue2)}, ${Math.round(saturations.vivid)}%, ${Math.round(shades.main)}%)`,
        muted1: `hsl(${Math.round(analogous1)}, ${Math.round(saturations.muted)}%, ${Math.round(shades.light)}%)`,
        muted2: `hsl(${Math.round(analogous2)}, ${Math.round(saturations.muted)}%, ${Math.round(shades.light)}%)`
      },
      tertiary: {
        split1: `hsl(${Math.round(splitComplementary1)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.main)}%)`,
        split2: `hsl(${Math.round(splitComplementary2)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.main)}%)`,
        analogous1: `hsl(${Math.round(analogous1)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.main)}%)`,
        analogous2: `hsl(${Math.round(analogous2)}, ${Math.round(saturations.normal)}%, ${Math.round(shades.main)}%)`
      }
    };
  }

  /**
   * Check if a color combination meets WCAG AA standards
   * @param {string} foreground HSL color string
   * @param {string} background HSL color string
   * @returns {boolean} True if meets WCAG AA standards
   */
  static meetsAccessibilityStandards(foreground, background) {
    // Parse HSL strings
    const parseHsl = (hslStr) => {
      const matches = hslStr.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
      if (!matches) throw new Error('Invalid HSL string');
      return this.hslToRgb(+matches[1], +matches[2], +matches[3]);
    };

    const fgRgb = parseHsl(foreground);
    const bgRgb = parseHsl(background);
    const ratio = this.getContrastRatio(fgRgb, bgRgb);
    
    // WCAG AA requires 4.5:1 for normal text, 3:1 for large text
    return ratio >= 4.5;
  }
}

export default ColorUtils;
