/**
 * Minimalist, animated SVG weather icons for Prognoz Weather Mini App.
 * Clean modern aesthetics, fully scalable and themed.
 */

const WeatherIcons = {
    // 0: Clear sky (Day / Night)
    clearDay: `
        <svg class="weather-icon-svg icon-clear-day" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle class="sun-glow" cx="32" cy="32" r="18" fill="url(#sunGlowGrad)" opacity="0.25"/>
            <circle class="sun-core" cx="32" cy="32" r="13" fill="url(#sunCoreGrad)"/>
            <g class="sun-rays" stroke="url(#sunRayGrad)" stroke-width="2.5" stroke-linecap="round">
                <line x1="32" y1="7" x2="32" y2="12" />
                <line x1="32" y1="52" x2="32" y2="57" />
                <line x1="7" y1="32" x2="12" y2="32" />
                <line x1="52" y1="32" x2="57" y2="32" />
                <line x1="14.3" y1="14.3" x2="17.8" y2="17.8" />
                <line x1="46.2" y1="46.2" x2="49.7" y2="49.7" />
                <line x1="14.3" y1="49.7" x2="17.8" y2="46.2" />
                <line x1="46.2" y1="17.8" x2="49.7" y2="14.3" />
            </g>
            <defs>
                <radialGradient id="sunGlowGrad" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#FDB813" stop-opacity="0.8"/>
                    <stop offset="100%" stop-color="#FDB813" stop-opacity="0"/>
                </radialGradient>
                <linearGradient id="sunCoreGrad" x1="20" y1="20" x2="44" y2="44" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#FFE066"/>
                    <stop offset="1" stop-color="#F59E0B"/>
                </linearGradient>
                <linearGradient id="sunRayGrad" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#FBBF24"/>
                    <stop offset="1" stop-color="#F59E0B"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    clearNight: `
        <svg class="weather-icon-svg icon-clear-night" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path class="moon-body" d="M37.5 14C27.8 14 20 21.8 20 31.5C20 41.2 27.8 49 37.5 49C42.2 49 46.5 47.1 49.6 44C38.5 43.5 30.5 33.5 32 22.4C32.6 18.2 35 15.3 37.5 14Z" fill="url(#moonGrad)"/>
            <circle class="star star-1" cx="17" cy="18" r="1.5" fill="#E0E7FF"/>
            <circle class="star star-2" cx="47" cy="15" r="1.2" fill="#E0E7FF"/>
            <circle class="star star-3" cx="14" cy="38" r="1" fill="#E0E7FF"/>
            <circle class="star star-4" cx="48" cy="33" r="1.2" fill="#E0E7FF"/>
            <defs>
                <linearGradient id="moonGrad" x1="20" y1="14" x2="49.6" y2="49" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#F1F5F9"/>
                    <stop offset="1" stop-color="#94A3B8"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    // 1, 2: Partly cloudy (Day)
    partlyCloudyDay: `
        <svg class="weather-icon-svg icon-partly-cloudy" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g class="sun-behind">
                <circle cx="25" cy="23" r="9" fill="url(#sunCoreGrad2)"/>
                <g class="sun-rays-mini" stroke="#FBBF24" stroke-width="2" stroke-linecap="round">
                    <line x1="25" y1="7" x2="25" y2="11" />
                    <line x1="9" y1="23" x2="13" y2="23" />
                    <line x1="14" y1="12" x2="17" y2="15" />
                    <line x1="36" y1="12" x2="33" y2="15" />
                </g>
            </g>
            <path class="cloud-front" d="M48 48H22C16.5 48 12 43.5 12 38C12 33 15.7 28.8 20.6 28.1C22.6 21.8 28.5 17.5 35.5 17.5C44 17.5 51 24.2 51.5 32.7C55.2 33.6 58 37 58 41C58 44.9 54.9 48 48 48Z" fill="url(#cloudGrad)"/>
            <defs>
                <linearGradient id="sunCoreGrad2" x1="16" y1="14" x2="34" y2="32" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#FFE066"/>
                    <stop offset="1" stop-color="#F59E0B"/>
                </linearGradient>
                <linearGradient id="cloudGrad" x1="12" y1="20" x2="58" y2="48" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#FFFFFF"/>
                    <stop offset="1" stop-color="#CBD5E1"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    // 1, 2: Partly cloudy (Night)
    partlyCloudyNight: `
        <svg class="weather-icon-svg icon-partly-cloudy-night" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path class="moon-behind" d="M30 14C23 14 18 19 18 26C18 31 21 35 25 36.8C24.4 29.5 28.5 22.8 35.5 20.5C34 16.5 32.2 14 30 14Z" fill="#CBD5E1"/>
            <path class="cloud-front" d="M48 48H22C16.5 48 12 43.5 12 38C12 33 15.7 28.8 20.6 28.1C22.6 21.8 28.5 17.5 35.5 17.5C44 17.5 51 24.2 51.5 32.7C55.2 33.6 58 37 58 41C58 44.9 54.9 48 48 48Z" fill="url(#cloudGradDark)"/>
            <defs>
                <linearGradient id="cloudGradDark" x1="12" y1="20" x2="58" y2="48" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#E2E8F0"/>
                    <stop offset="1" stop-color="#94A3B8"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    // 3: Overcast
    overcast: `
        <svg class="weather-icon-svg icon-overcast" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path class="cloud-back" opacity="0.6" d="M43 38H22C17.6 38 14 34.4 14 30C14 26 17 22.6 20.9 22.1C22.5 17 27.2 13.5 32.8 13.5C39.6 13.5 45.2 18.9 45.6 25.7C48.6 26.4 50.8 29.1 50.8 32.3C50.8 35.4 48.3 38 43 38Z" fill="#94A3B8"/>
            <path class="cloud-main" d="M48 50H20C14.5 50 10 45.5 10 40C10 35 13.7 30.8 18.6 30.1C20.6 23.8 26.5 19.5 33.5 19.5C42 19.5 49 26.2 49.5 34.7C53.2 35.6 56 39 56 43C56 46.9 52.4 50 48 50Z" fill="url(#overcastGrad)"/>
            <defs>
                <linearGradient id="overcastGrad" x1="10" y1="20" x2="56" y2="50" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#E2E8F0"/>
                    <stop offset="1" stop-color="#64748B"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    // 45, 48: Fog
    fog: `
        <svg class="weather-icon-svg icon-fog" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path class="cloud-fog" d="M46 36H20C15.6 36 12 32.4 12 28C12 24 15 20.6 18.9 20.1C20.5 15 25.2 11.5 30.8 11.5C37.6 11.5 43.2 16.9 43.6 23.7C46.6 24.4 48.8 27.1 48.8 30.3C48.8 33.4 46.3 36 46 36Z" fill="#94A3B8" opacity="0.7"/>
            <line class="fog-line fog-line-1" x1="14" y1="42" x2="50" y2="42" stroke="#CBD5E1" stroke-width="3" stroke-linecap="round"/>
            <line class="fog-line fog-line-2" x1="18" y1="48" x2="46" y2="48" stroke="#94A3B8" stroke-width="3" stroke-linecap="round"/>
            <line class="fog-line fog-line-3" x1="22" y1="54" x2="42" y2="54" stroke="#64748B" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
    `,

    // 51, 53, 55, 61, 80: Light/Moderate Rain
    rain: `
        <svg class="weather-icon-svg icon-rain" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path class="cloud-rain-body" d="M48 40H20C14.5 40 10 35.5 10 30C10 25 13.7 20.8 18.6 20.1C20.6 13.8 26.5 9.5 33.5 9.5C42 9.5 49 16.2 49.5 24.7C53.2 25.6 56 29 56 33C56 36.9 52.4 40 48 40Z" fill="url(#rainCloudGrad)"/>
            <g class="rain-drops" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round">
                <line class="drop drop-1" x1="22" y1="46" x2="19" y2="54" />
                <line class="drop drop-2" x1="33" y1="46" x2="30" y2="55" />
                <line class="drop drop-3" x1="44" y1="46" x2="41" y2="54" />
            </g>
            <defs>
                <linearGradient id="rainCloudGrad" x1="10" y1="10" x2="56" y2="40" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#CBD5E1"/>
                    <stop offset="1" stop-color="#475569"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    // 63, 65, 81, 82: Heavy Rain
    heavyRain: `
        <svg class="weather-icon-svg icon-heavy-rain" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path class="cloud-heavy-body" d="M48 38H20C14.5 38 10 33.5 10 28C10 23 13.7 18.8 18.6 18.1C20.6 11.8 26.5 7.5 33.5 7.5C42 7.5 49 14.2 49.5 22.7C53.2 23.6 56 27 56 31C56 34.9 52.4 38 48 38Z" fill="url(#heavyCloudGrad)"/>
            <g class="rain-drops-heavy" stroke="#0284C7" stroke-width="2.5" stroke-linecap="round">
                <line class="drop drop-1" x1="18" y1="44" x2="14" y2="54" />
                <line class="drop drop-2" x1="26" y1="44" x2="22" y2="55" />
                <line class="drop drop-3" x1="34" y1="44" x2="30" y2="54" />
                <line class="drop drop-4" x1="42" y1="44" x2="38" y2="55" />
                <line class="drop drop-5" x1="50" y1="44" x2="46" y2="54" />
            </g>
            <defs>
                <linearGradient id="heavyCloudGrad" x1="10" y1="8" x2="56" y2="38" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#94A3B8"/>
                    <stop offset="1" stop-color="#334155"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    // 71, 73, 75, 77, 85, 86: Snow
    snow: `
        <svg class="weather-icon-svg icon-snow" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path class="cloud-snow-body" d="M48 38H20C14.5 38 10 33.5 10 28C10 23 13.7 18.8 18.6 18.1C20.6 11.8 26.5 7.5 33.5 7.5C42 7.5 49 14.2 49.5 22.7C53.2 23.6 56 27 56 31C56 34.9 52.4 38 48 38Z" fill="url(#snowCloudGrad)"/>
            <g class="snow-flakes" fill="#BAE6FD">
                <!-- Flake 1 -->
                <g class="flake flake-1" transform="translate(20, 46)">
                    <circle cx="0" cy="0" r="2.2" />
                </g>
                <!-- Flake 2 -->
                <g class="flake flake-2" transform="translate(32, 50)">
                    <circle cx="0" cy="0" r="2.6" />
                </g>
                <!-- Flake 3 -->
                <g class="flake flake-3" transform="translate(44, 46)">
                    <circle cx="0" cy="0" r="2.2" />
                </g>
            </g>
            <defs>
                <linearGradient id="snowCloudGrad" x1="10" y1="8" x2="56" y2="38" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#F1F5F9"/>
                    <stop offset="1" stop-color="#94A3B8"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    // 95, 96, 99: Thunderstorm
    thunderstorm: `
        <svg class="weather-icon-svg icon-thunder" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path class="cloud-thunder-body" d="M48 36H20C14.5 36 10 31.5 10 26C10 21 13.7 16.8 18.6 16.1C20.6 9.8 26.5 5.5 33.5 5.5C42 5.5 49 12.2 49.5 20.7C53.2 21.6 56 25 56 29C56 32.9 52.4 36 48 36Z" fill="url(#thunderCloudGrad)"/>
            <polygon class="lightning-bolt" points="33,34 26,45 32,45 28,57 40,43 33,43 38,34" fill="url(#lightningGrad)" stroke="#F59E0B" stroke-width="0.8"/>
            <defs>
                <linearGradient id="thunderCloudGrad" x1="10" y1="5" x2="56" y2="36" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#64748B"/>
                    <stop offset="1" stop-color="#1E293B"/>
                </linearGradient>
                <linearGradient id="lightningGrad" x1="26" y1="34" x2="38" y2="57" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#FDE047"/>
                    <stop offset="1" stop-color="#F59E0B"/>
                </linearGradient>
            </defs>
        </svg>
    `,

    /**
     * Return the matching SVG for WMO code & is_day
     */
    getIcon(code, isDay = 1) {
        if (code === 0) {
            return isDay ? this.clearDay : this.clearNight;
        }
        if (code === 1 || code === 2) {
            return isDay ? this.partlyCloudyDay : this.partlyCloudyNight;
        }
        if (code === 3) {
            return this.overcast;
        }
        if (code === 45 || code === 48) {
            return this.fog;
        }
        if ([51, 53, 55, 56, 57, 61, 80].includes(code)) {
            return this.rain;
        }
        if ([63, 65, 66, 67, 81, 82].includes(code)) {
            return this.heavyRain;
        }
        if ([71, 73, 75, 77, 85, 86].includes(code)) {
            return this.snow;
        }
        if ([95, 96, 99].includes(code)) {
            return this.thunderstorm;
        }
        return isDay ? this.partlyCloudyDay : this.partlyCloudyNight;
    },

    /**
     * Return ambient CSS gradient theme class
     */
    getWeatherTheme(code, isDay = 1) {
        if (isDay === 0) {
            return "theme-night";
        }
        if (code === 0) {
            return "theme-sunny";
        }
        if (code === 1 || code === 2) {
            return "theme-fair";
        }
        if (code === 3) {
            return "theme-cloudy";
        }
        if (code === 45 || code === 48) {
            return "theme-fog";
        }
        if ([51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82].includes(code)) {
            return "theme-rain";
        }
        if ([71, 73, 75, 77, 85, 86].includes(code)) {
            return "theme-snow";
        }
        if ([95, 96, 99].includes(code)) {
            return "theme-storm";
        }
        return "theme-fair";
    },

    getWeatherDescription(code, lang = 'ru') {
        const map = {
            0: { ru: "Ясно", en: "Clear sky", emoji: "☀️" },
            1: { ru: "Преимущественно ясно", en: "Mainly clear", emoji: "🌤" },
            2: { ru: "Переменная облачность", en: "Partly cloudy", emoji: "⛅" },
            3: { ru: "Пасмурно", en: "Overcast", emoji: "☁️" },
            45: { ru: "Туман", en: "Fog", emoji: "🌫" },
            48: { ru: "Изморозь", en: "Depositing rime fog", emoji: "🌫" },
            51: { ru: "Небольшая морось", en: "Light drizzle", emoji: "🌧" },
            53: { ru: "Морось", en: "Moderate drizzle", emoji: "🌧" },
            55: { ru: "Сильная морось", en: "Dense drizzle", emoji: "🌧" },
            56: { ru: "Ледяная морось", en: "Freezing drizzle", emoji: "🌧" },
            57: { ru: "Сильная ледяная морось", en: "Dense freezing drizzle", emoji: "🌧" },
            61: { ru: "Небольшой дождь", en: "Slight rain", emoji: "🌧" },
            63: { ru: "Дождь", en: "Moderate rain", emoji: "🌧" },
            65: { ru: "Сильный дождь", en: "Heavy rain", emoji: "🌧" },
            66: { ru: "Ледяной дождь", en: "Freezing rain", emoji: "🌧" },
            67: { ru: "Сильный ледяной дождь", en: "Heavy freezing rain", emoji: "🌧" },
            71: { ru: "Небольшой снег", en: "Slight snowfall", emoji: "❄️" },
            73: { ru: "Снег", en: "Moderate snowfall", emoji: "❄️" },
            75: { ru: "Сильный снег", en: "Heavy snowfall", emoji: "❄️" },
            77: { ru: "Снежные зерна", en: "Snow grains", emoji: "❄️" },
            80: { ru: "Небольшой ливень", en: "Slight rain showers", emoji: "🌦" },
            81: { ru: "Ливень", en: "Moderate rain showers", emoji: "🌦" },
            82: { ru: "Сильный ливень", en: "Violent rain showers", emoji: "🌦" },
            85: { ru: "Небольшой снегопад", en: "Slight snow showers", emoji: "❄️" },
            86: { ru: "Сильный снегопад", en: "Heavy snow showers", emoji: "❄️" },
            95: { ru: "Гроза", en: "Thunderstorm", emoji: "⛈" },
            96: { ru: "Гроза с градом", en: "Thunderstorm with hail", emoji: "⛈" },
            99: { ru: "Сильная гроза с градом", en: "Thunderstorm with heavy hail", emoji: "⛈" },
        };
        const item = map[code];
        if (!item) return lang === 'en' ? 'Cloudy' : 'Облачно';
        return item[lang] || item.ru;
    },

    getWeatherEmoji(code) {
        const emojis = {
            0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️", 45: "🌫", 48: "🌫",
            51: "🌧", 53: "🌧", 55: "🌧", 56: "🌧", 57: "🌧",
            61: "🌧", 63: "🌧", 65: "🌧", 66: "🌧", 67: "🌧",
            71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
            80: "🌦", 81: "🌦", 82: "🌦", 85: "❄️", 86: "❄️",
            95: "⛈", 96: "⛈", 99: "⛈"
        };
        return emojis[code] || "🌤";
    },

    getWindCardinal(degrees, lang = 'ru') {
        if (degrees === null || degrees === undefined) return lang === 'ru' ? 'Н/Д' : 'N/A';
        const cardinals_ru = ["С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ", "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ", "ССЗ"];
        const cardinals_en = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
        const index = Math.round((degrees % 360) / 22.5) % 16;
        return lang === 'ru' ? cardinals_ru[index] : cardinals_en[index];
    }
};

window.WeatherIcons = WeatherIcons;
