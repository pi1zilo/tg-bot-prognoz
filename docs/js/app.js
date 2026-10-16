/**
 * Prognoz Telegram Mini App - Frontend Client Logic
 */

(function () {
    'use strict';

    // Telegram WebApp SDK instance
    const tg = window.Telegram?.WebApp;
    if (tg) {
        try {
            tg.ready();
            tg.expand();
        } catch (e) {
            console.warn("Telegram WebApp initialization error:", e);
        }
    }

    // App State
    const state = {
        city: 'Москва',
        display_name: 'Москва, Россия',
        lat: 55.751244,
        lon: 37.618423,
        tz: 'Europe/Moscow',
        offset: 0, // -1, 0, 1, 2, or 'week'
        lang: 'ru',
        theme: 'dark',
        telegram_id: null,
        data: null,
        isLoading: false,
    };

    // Translations for UI elements
    const i18n = {
        ru: {
            app_title: "Прогноз Погоды",
            yesterday: "Вчера",
            today: "Сегодня",
            tomorrow: "Завтра",
            after_tomorrow: "+2 дня",
            seven_days: "7 дней",
            feels_like: "Ощущается как",
            min: "Мин:",
            max: "Макс:",
            precip: "ОСАДКИ",
            wind: "ВЕТЕР",
            uv: "УФ-ИНДЕКС",
            hourly_title: "⏱ ПОЧАСОВОЙ ПРОГНОЗ",
            periods_title: "🌓 ВРЕМЯ СУТОК",
            week_title: "📅 ПРОГНОЗ НА 7 ДНЕЙ",
            metric_wind: "💨 ВЕТЕР",
            metric_humidity: "💧 ВЛАЖНОСТЬ",
            metric_uv: "☀️ УФ-ИНДЕКС",
            metric_pressure: "🧭 ДАВЛЕНИЕ",
            metric_sun: "🌅 СОЛНЦЕ",
            metric_precip: "🌧️ ОСАДКИ",
            sunrise: "Восход",
            sunset: "Закат",
            daylight: "Световой день",
            now: "Сейчас",
            send_to_chat: "Отправить в чат",
            save_city: "Сохранить",
            search_placeholder: "Поиск города, поселка или села...",
            popular_places: "Популярные направления:",
            city_saved_toast: "Город сохранен как основной",
            copied_toast: "Прогноз скопирован в буфер",
            geo_error_toast: "Не удалось определить геопозицию",
            geo_detecting: "Определяем координаты...",
            hours: "ч",
            minutes: "мин",
            pressure_unit: "мм рт. ст.",
            pressure_normal: "В норме",
            humidity_comfortable: "Комфортно",
            humidity_dry: "Сухой воздух",
            humidity_humid: "Высокая влажность",
            uv_low: "Низкий",
            uv_moderate: "Умеренный",
            uv_high: "Высокий",
            uv_very_high: "Очень высокий",
            uv_tip_low: "Защита не требуется",
            uv_tip_mod: "Рекомендуются очки и крем",
            uv_tip_high: "Необходим солнцезащитный крем",
        },
        en: {
            app_title: "Weather Forecast",
            yesterday: "Yesterday",
            today: "Today",
            tomorrow: "Tomorrow",
            after_tomorrow: "In 2 days",
            seven_days: "7 days",
            feels_like: "Feels like",
            min: "Min:",
            max: "Max:",
            precip: "PRECIPITATION",
            wind: "WIND",
            uv: "UV INDEX",
            hourly_title: "⏱ HOURLY FORECAST",
            periods_title: "🌓 DAY PHASES",
            week_title: "📅 7-DAY OUTLOOK",
            metric_wind: "💨 WIND",
            metric_humidity: "💧 HUMIDITY",
            metric_uv: "☀️ UV INDEX",
            metric_pressure: "🧭 PRESSURE",
            metric_sun: "🌅 SUN CYCLE",
            metric_precip: "🌧️ PRECIPITATION",
            sunrise: "Sunrise",
            sunset: "Sunset",
            daylight: "Daylight duration",
            now: "Now",
            send_to_chat: "Send to Chat",
            save_city: "Save City",
            search_placeholder: "Search city, village, settlement...",
            popular_places: "Popular destinations:",
            city_saved_toast: "Default city successfully saved",
            copied_toast: "Forecast copied to clipboard",
            geo_error_toast: "Unable to detect location",
            geo_detecting: "Detecting location...",
            hours: "h",
            minutes: "min",
            pressure_unit: "mmHg",
            pressure_normal: "Normal",
            humidity_comfortable: "Comfortable",
            humidity_dry: "Dry air",
            humidity_humid: "Humid",
            uv_low: "Low",
            uv_moderate: "Moderate",
            uv_high: "High",
            uv_very_high: "Very High",
            uv_tip_low: "No protection needed",
            uv_tip_mod: "Wear sunglasses & SPF",
            uv_tip_high: "Sunscreen recommended",
        }
    };

    // Helper: Haptic feedback
    function triggerHaptic(type = 'light') {
        try {
            if (tg?.HapticFeedback) {
                if (type === 'selection') tg.HapticFeedback.selectionChanged();
                else if (type === 'success') tg.HapticFeedback.notificationOccurred('success');
                else if (type === 'warning') tg.HapticFeedback.notificationOccurred('warning');
                else tg.HapticFeedback.impactOccurred(type);
            }
        } catch (e) {
            // Ignore if not supported
        }
    }

    // Helper: Show floating toast
    function showToast(text, icon = "✅") {
        const toast = document.getElementById("toastNotice");
        const toastText = document.getElementById("toastText");
        const toastIcon = document.getElementById("toastIcon");
        if (!toast) return;

        toastText.textContent = text;
        toastIcon.textContent = icon;
        toast.classList.add("show");
        setTimeout(() => {
            toast.classList.remove("show");
        }, 3000);
    }

    // Initialize user and stored preferences
    function initUserContext() {
        if (tg?.initDataUnsafe?.user) {
            state.telegram_id = tg.initDataUnsafe.user.id;
            if (tg.initDataUnsafe.user.language_code === 'en') {
                state.lang = 'en';
            }
        }

        // Check local storage
        const savedCity = localStorage.getItem('prognoz_city');
        const savedLat = localStorage.getItem('prognoz_lat');
        const savedLon = localStorage.getItem('prognoz_lon');
        const savedTz = localStorage.getItem('prognoz_tz');
        const savedLang = localStorage.getItem('prognoz_lang');
        const savedTheme = localStorage.getItem('prognoz_theme');

        if (savedCity && savedLat && savedLon) {
            state.city = savedCity;
            state.display_name = savedCity;
            state.lat = parseFloat(savedLat);
            state.lon = parseFloat(savedLon);
            state.tz = savedTz || 'auto';
        }

        if (savedLang) {
            state.lang = savedLang;
        }

        if (savedTheme) {
            state.theme = savedTheme;
            if (savedTheme === 'light') {
                document.body.classList.add('theme-light');
            }
        } else if (tg?.colorScheme === 'light') {
            state.theme = 'light';
            document.body.classList.add('theme-light');
        }

        // If user has telegram_id, try fetching saved city from DB
        if (state.telegram_id) {
            fetch(`/api/user?telegram_id=${state.telegram_id}`)
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.user && data.user.city) {
                        state.city = data.user.city;
                        state.display_name = data.user.city;
                        state.lat = data.user.latitude;
                        state.lon = data.user.longitude;
                        state.tz = data.user.timezone || 'auto';
                        if (data.user.language) state.lang = data.user.language;
                        updateUILabels();
                        loadWeather();
                    }
                })
                .catch(err => console.warn("Could not load user from DB:", err));
        }

        updateUILabels();
    }

    // Update static labels when language changes
    function updateUILabels() {
        const t = i18n[state.lang] || i18n.ru;
        document.title = t.app_title;

        const langBtn = document.getElementById("btnLangToggle");
        if (langBtn) langBtn.textContent = state.lang.toUpperCase();

        document.getElementById("tabYesterday").textContent = t.yesterday;
        document.getElementById("tabToday").textContent = t.today;
        document.getElementById("tabTomorrow").textContent = t.tomorrow;
        document.getElementById("tabAfterTomorrow").textContent = t.after_tomorrow;
        document.getElementById("tabWeek").textContent = t.seven_days;

        document.getElementById("labelHeroPrecip").textContent = t.precip;
        document.getElementById("labelHeroWind").textContent = t.wind;
        document.getElementById("labelHeroUv").textContent = t.uv;

        document.getElementById("titleHourlyForecast").textContent = t.hourly_title;
        document.getElementById("titlePeriods").textContent = t.periods_title;
        document.getElementById("titleWeekForecast").textContent = t.week_title;

        document.getElementById("titleMetricWind").textContent = t.metric_wind;
        document.getElementById("titleMetricHumidity").textContent = t.metric_humidity;
        document.getElementById("titleMetricUv").textContent = t.metric_uv;
        document.getElementById("titleMetricPressure").textContent = t.metric_pressure;
        document.getElementById("titleMetricSun").textContent = t.metric_sun;
        document.getElementById("titleMetricPrecip").textContent = t.metric_precip;

        document.getElementById("labelSunrise").textContent = t.sunrise;
        document.getElementById("labelSunset").textContent = t.sunset;
        document.getElementById("labelSendToChat").textContent = t.send_to_chat;
        document.getElementById("labelSaveCity").textContent = t.save_city;
        document.getElementById("searchInput").placeholder = t.search_placeholder;
        document.getElementById("labelPopularPlaces").textContent = t.popular_places;
    }

    // Client-side Open-Meteo parser for static hosting (GitHub Pages)
    function parseRawMeteo(raw, lat, lon, offset, lang) {
        const actualTz = raw.timezone || 'UTC';
        const now = new Date();
        const targetDate = new Date(now.getTime() + offset * 86400000);
        const y = targetDate.getFullYear();
        const m = String(targetDate.getMonth() + 1).padStart(2, '0');
        const d = String(targetDate.getDate()).padStart(2, '0');
        const targetDateStr = `${y}-${m}-${d}`;

        const cur = raw.current || {};
        const currCode = cur.weather_code || 0;
        const hpa = cur.surface_pressure || 1013.25;
        const mmhg = Math.round(hpa * 0.750062);

        const currentPayload = {
            temperature: Math.round((cur.temperature_2m || 0) * 10) / 10,
            apparent_temperature: Math.round((cur.apparent_temperature || 0) * 10) / 10,
            weather_code: currCode,
            weather_desc: window.WeatherIcons.getWeatherDescription(currCode, lang),
            weather_emoji: window.WeatherIcons.getWeatherEmoji(currCode),
            is_day: cur.is_day !== undefined ? cur.is_day : 1,
            humidity: Math.round(cur.relative_humidity_2m || 0),
            pressure_hpa: Math.round(hpa * 10) / 10,
            pressure_mmhg: mmhg,
            wind_speed: Math.round((cur.wind_speed_10m || 0) * 10) / 10,
            wind_direction: cur.wind_direction_10m || 0,
            wind_cardinal: window.WeatherIcons.getWindCardinal(cur.wind_direction_10m || 0, lang),
            cloud_cover: Math.round(cur.cloud_cover || 0),
            precipitation: Math.round((cur.precipitation || 0) * 10) / 10,
        };

        const hourly = raw.hourly || {};
        const times = hourly.time || [];
        const hourlyList = [];
        const tempsTarget = [];
        const precipTarget = [];
        const currHour = now.getHours();

        for (let i = 0; i < times.length; i++) {
            const tStr = times[i];
            if (!tStr.startsWith(targetDateStr)) continue;

            const timePart = tStr.includes('T') ? tStr.split('T')[1].substring(0, 5) : tStr;
            const hourInt = parseInt(timePart.split(':')[0], 10);
            const tempVal = hourly.temperature_2m ? hourly.temperature_2m[i] : 0;
            const appTempVal = hourly.apparent_temperature ? hourly.apparent_temperature[i] : tempVal;
            const hCode = hourly.weather_code ? hourly.weather_code[i] : 0;
            const precVal = hourly.precipitation ? hourly.precipitation[i] : 0;
            const probVal = hourly.precipitation_probability ? hourly.precipitation_probability[i] : 0;
            const wSpd = hourly.wind_speed_10m ? hourly.wind_speed_10m[i] : 0;
            const isDayVal = hourly.is_day ? hourly.is_day[i] : 1;
            const humVal = hourly.relative_humidity_2m ? hourly.relative_humidity_2m[i] : 0;
            const uvVal = hourly.uv_index ? hourly.uv_index[i] : 0;

            tempsTarget.push(tempVal);
            precipTarget.push(precVal);

            hourlyList.push({
                time: tStr,
                hour: hourInt,
                hour_display: timePart,
                temperature: Math.round(tempVal * 10) / 10,
                apparent_temperature: Math.round(appTempVal * 10) / 10,
                precipitation: Math.round(precVal * 10) / 10,
                precipitation_probability: Math.round(probVal),
                weather_code: hCode,
                weather_desc: window.WeatherIcons.getWeatherDescription(hCode, lang),
                weather_emoji: window.WeatherIcons.getWeatherEmoji(hCode),
                wind_speed: Math.round(wSpd * 10) / 10,
                humidity: Math.round(humVal),
                uv_index: Math.round(uvVal * 10) / 10,
                is_day: isDayVal,
                is_current: (offset === 0 && hourInt === currHour),
            });
        }

        // Periods of day
        const periods = {};
        const pDefs = {
            night: [0, 6, lang === 'ru' ? 'Ночь' : 'Night'],
            morning: [6, 12, lang === 'ru' ? 'Утро' : 'Morning'],
            day: [12, 18, lang === 'ru' ? 'День' : 'Day'],
            evening: [18, 24, lang === 'ru' ? 'Вечер' : 'Evening'],
        };
        for (const [pKey, [hStart, hEnd, pTitle]] of Object.entries(pDefs)) {
            const pHours = hourlyList.filter(h => h.hour >= hStart && h.hour < hEnd);
            if (pHours.length) {
                const pTemps = pHours.map(h => h.temperature);
                const pWind = pHours.map(h => h.wind_speed);
                const pCodes = pHours.map(h => h.weather_code);
                const midCode = pCodes[Math.floor(pCodes.length / 2)];
                const pSumPrec = pHours.reduce((sum, h) => sum + h.precipitation, 0);
                periods[pKey] = {
                    title: pTitle,
                    temp_min: Math.min(...pTemps),
                    temp_max: Math.max(...pTemps),
                    temp_avg: Math.round((pTemps.reduce((a, b) => a + b, 0) / pTemps.length) * 10) / 10,
                    weather_code: midCode,
                    weather_desc: window.WeatherIcons.getWeatherDescription(midCode, lang),
                    weather_emoji: window.WeatherIcons.getWeatherEmoji(midCode),
                    wind_speed: Math.round((pWind.reduce((a, b) => a + b, 0) / pWind.length) * 10) / 10,
                    precipitation: Math.round(pSumPrec * 10) / 10,
                };
            }
        }

        // Daily
        const daily = raw.daily || {};
        const dailyTimes = daily.time || [];
        let dIdx = dailyTimes.indexOf(targetDateStr);
        if (dIdx === -1 && dailyTimes.length) dIdx = 0;

        let sr = "--:--", ss = "--:--", uvMax = 0, pSum = 0, pProbMax = 0;
        let tMin = tempsTarget.length ? Math.min(...tempsTarget) : 0;
        let tMax = tempsTarget.length ? Math.max(...tempsTarget) : 0;
        let dCode = currCode;

        if (dIdx !== -1) {
            if (daily.sunrise && daily.sunrise[dIdx]) {
                const s = daily.sunrise[dIdx];
                sr = s.includes('T') ? s.split('T')[1].substring(0, 5) : s;
            }
            if (daily.sunset && daily.sunset[dIdx]) {
                const s = daily.sunset[dIdx];
                ss = s.includes('T') ? s.split('T')[1].substring(0, 5) : s;
            }
            if (daily.uv_index_max && daily.uv_index_max[dIdx] !== undefined) uvMax = Math.round(daily.uv_index_max[dIdx] * 10) / 10;
            if (daily.precipitation_sum && daily.precipitation_sum[dIdx] !== undefined) pSum = Math.round(daily.precipitation_sum[dIdx] * 10) / 10;
            if (daily.precipitation_probability_max && daily.precipitation_probability_max[dIdx] !== undefined) pProbMax = Math.round(daily.precipitation_probability_max[dIdx]);
            if (daily.temperature_2m_min && daily.temperature_2m_min[dIdx] !== undefined) tMin = Math.round(daily.temperature_2m_min[dIdx] * 10) / 10;
            if (daily.temperature_2m_max && daily.temperature_2m_max[dIdx] !== undefined) tMax = Math.round(daily.temperature_2m_max[dIdx] * 10) / 10;
            if (daily.weather_code && daily.weather_code[dIdx] !== undefined) dCode = daily.weather_code[dIdx];
        }

        const monthsRu = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"];
        const monthsEn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const daysRu = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];
        const daysEn = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

        const forecast7Days = [];
        const todayStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
        let startIdx = dailyTimes.indexOf(todayStr);
        if (startIdx === -1) startIdx = 0;

        for (let i = startIdx; i < Math.min(startIdx + 7, dailyTimes.length); i++) {
            const dtI = new Date(dailyTimes[i]);
            const relOffset = i - startIdx;
            let dName = lang === 'ru' ? daysRu[dtI.getDay()] : daysEn[dtI.getDay()];
            if (relOffset === 0) dName = lang === 'ru' ? 'Сегодня' : 'Today';
            else if (relOffset === 1) dName = lang === 'ru' ? 'Завтра' : 'Tomorrow';

            const dShort = `${dtI.getDate()} ${(lang === 'ru' ? monthsRu : monthsEn)[dtI.getMonth()]}`;
            const itemCode = daily.weather_code ? daily.weather_code[i] : 0;
            forecast7Days.push({
                date: dailyTimes[i],
                day_name: dName,
                date_short: dShort,
                temp_min: daily.temperature_2m_min ? Math.round(daily.temperature_2m_min[i] * 10) / 10 : 0,
                temp_max: daily.temperature_2m_max ? Math.round(daily.temperature_2m_max[i] * 10) / 10 : 0,
                weather_code: itemCode,
                weather_emoji: window.WeatherIcons.getWeatherEmoji(itemCode),
                weather_desc: window.WeatherIcons.getWeatherDescription(itemCode, lang),
                precipitation_probability: daily.precipitation_probability_max ? Math.round(daily.precipitation_probability_max[i] || 0) : 0,
            });
        }

        let dayFormatted = targetDate.toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'en-US', {
            weekday: 'long',
            day: 'numeric',
            month: 'long'
        });

        return {
            success: true,
            location: { latitude: lat, longitude: lon, timezone: actualTz },
            current: currentPayload,
            selected_day: {
                offset: offset,
                date: targetDateStr,
                date_formatted: dayFormatted,
                day_title: offset === 0 ? (lang === 'ru' ? 'Сегодня' : 'Today') : (offset === 1 ? (lang === 'ru' ? 'Завтра' : 'Tomorrow') : (offset === -1 ? (lang === 'ru' ? 'Вчера' : 'Yesterday') : (lang === 'ru' ? 'Послезавтра' : 'In 2 days'))),
                temp_min: tMin,
                temp_max: tMax,
                weather_code: dCode,
                weather_desc: window.WeatherIcons.getWeatherDescription(dCode, lang),
                weather_emoji: window.WeatherIcons.getWeatherEmoji(dCode),
                sunrise: sr,
                sunset: ss,
                uv_index_max: uvMax,
                precipitation_sum: pSum,
                precipitation_probability_max: pProbMax,
            },
            hourly: hourlyList,
            periods: periods,
            forecast_7days: forecast7Days,
        };
    }

    async function fetchOpenMeteoDirectly(lat, lon, tz, offset, lang) {
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&past_days=2&forecast_days=8&timezone=${encodeURIComponent(tz || 'auto')}&wind_speed_unit=ms&current=temperature_2m,apparent_temperature,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,relative_humidity_2m,surface_pressure,is_day&hourly=temperature_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,relative_humidity_2m,surface_pressure,uv_index,is_day&daily=weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_sum,precipitation_probability_max,wind_speed_10m_max`;
        const resp = await fetch(url);
        if (!resp.ok) throw new Error("Open-Meteo direct fetch failed");
        const raw = await resp.json();
        return parseRawMeteo(raw, lat, lon, offset, lang);
    }

    // Fetch and render weather data
    async function loadWeather() {
        if (state.isLoading) return;
        state.isLoading = true;

        const offsetParam = state.offset === 'week' ? 0 : state.offset;
        let data = null;

        // Try local backend API first (if available)
        try {
            const url = `/api/weather?lat=${state.lat}&lon=${state.lon}&timezone=${encodeURIComponent(state.tz)}&offset=${offsetParam}&lang=${state.lang}`;
            const resp = await fetch(url);
            if (resp.ok) {
                const resJson = await resp.json();
                if (resJson.success) data = resJson;
            }
        } catch (e) {
            // Static hosting or server unavailable
        }

        // Direct Open-Meteo fallback (e.g. for GitHub Pages / static hosting)
        if (!data) {
            try {
                data = await fetchOpenMeteoDirectly(state.lat, state.lon, state.tz, offsetParam, state.lang);
            } catch (err) {
                console.error("Weather load error:", err);
                showToast("Ошибка загрузки погоды", "⚠️");
            }
        }

        if (data) {
            state.data = data;
            renderAll(data);
        }
        state.isLoading = false;
    }

    // Render all UI components
    function renderAll(data) {
        document.getElementById("locationName").textContent = state.city;

        // Render Hero Card
        renderHero(data);

        // Render Hourly Slider
        renderHourly(data.hourly);

        // Render Periods
        renderPeriods(data.periods);

        // Render Detailed Metrics
        renderMetrics(data);

        // Render 7-day outlook
        renderWeek(data.forecast_7days);

        // Apply atmospheric theme
        const themeClass = window.WeatherIcons.getWeatherTheme(
            data.current.weather_code,
            data.current.is_day
        );
        document.body.className = `${state.theme === 'light' ? 'theme-light' : ''} ${themeClass}`;
    }

    // Render Hero Card
    function renderHero(data) {
        const t = i18n[state.lang] || i18n.ru;
        const cur = data.current;
        const day = data.selected_day;

        // Date & condition
        document.getElementById("heroDate").textContent = day.date_formatted;
        document.getElementById("heroConditionEmoji").textContent = state.offset === 0 ? cur.weather_emoji : day.weather_emoji;
        document.getElementById("heroConditionText").textContent = state.offset === 0 ? cur.weather_desc : day.weather_desc;

        // Animated SVG Icon
        const isDayTime = state.offset === 0 ? cur.is_day : 1;
        const iconCode = state.offset === 0 ? cur.weather_code : day.weather_code;
        const svgIcon = window.WeatherIcons.getIcon(iconCode, isDayTime);
        document.getElementById("heroVisual").innerHTML = svgIcon;

        // Temperatures
        const displayTemp = state.offset === 0 ? (cur.temperature > 0 ? `+${cur.temperature}` : `${cur.temperature}`) : (day.temp_max > 0 ? `+${day.temp_max}` : `${day.temp_max}`);
        document.getElementById("heroTemp").textContent = `${displayTemp}°`;

        const feelsLikeVal = state.offset === 0 ? cur.apparent_temperature : day.temp_max;
        const feelsSign = feelsLikeVal > 0 ? `+${feelsLikeVal}` : `${feelsLikeVal}`;
        document.getElementById("heroFeelsLike").textContent = `${t.feels_like} ${feelsSign}°`;

        const minSign = day.temp_min > 0 ? `+${day.temp_min}` : `${day.temp_min}`;
        const maxSign = day.temp_max > 0 ? `+${day.temp_max}` : `${day.temp_max}`;
        document.getElementById("heroMinTemp").textContent = `${minSign}°`;
        document.getElementById("heroMaxTemp").textContent = `${maxSign}°`;

        // Hero quick metrics
        document.getElementById("heroPrecip").textContent = `${day.precipitation_sum} мм (${day.precipitation_probability_max}%)`;
        document.getElementById("heroWind").textContent = `${cur.wind_speed} м/с ${cur.wind_cardinal}`;

        let uvRating = t.uv_low;
        if (day.uv_index_max >= 3 && day.uv_index_max <= 5) uvRating = t.uv_moderate;
        else if (day.uv_index_max >= 6 && day.uv_index_max <= 7) uvRating = t.uv_high;
        else if (day.uv_index_max >= 8) uvRating = t.uv_very_high;
        document.getElementById("heroUv").textContent = `${day.uv_index_max} • ${uvRating}`;
    }

    // Render Hourly Forecast Slider
    function renderHourly(hourlyList) {
        const container = document.getElementById("hourlyScroll");
        if (!container || !hourlyList) return;

        const t = i18n[state.lang] || i18n.ru;
        let html = '';

        hourlyList.forEach(item => {
            const timeLabel = item.is_current ? t.now : item.hour_display;
            const tempSign = item.temperature > 0 ? `+${item.temperature}` : `${item.temperature}`;
            const iconSvg = window.WeatherIcons.getIcon(item.weather_code, item.is_day);
            const activeClass = item.is_current ? 'current' : '';

            let precipBadge = '';
            if (item.precipitation_probability > 0) {
                precipBadge = `<span class="hour-precip-badge">💧 ${item.precipitation_probability}%</span>`;
            }

            html += `
                <div class="hour-card ${activeClass}">
                    <span class="hour-time">${timeLabel}</span>
                    <div class="hour-icon">${iconSvg}</div>
                    <span class="hour-temp">${tempSign}°</span>
                    ${precipBadge}
                </div>
            `;
        });

        container.innerHTML = html;

        // Auto-scroll to current hour
        const currentHourElem = container.querySelector('.hour-card.current');
        if (currentHourElem) {
            setTimeout(() => {
                currentHourElem.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
            }, 100);
        }
    }

    // Render Periods
    function renderPeriods(periods) {
        const grid = document.getElementById("periodsGrid");
        if (!grid || !periods) return;

        let html = '';
        const order = ['night', 'morning', 'day', 'evening'];

        order.forEach(pKey => {
            const p = periods[pKey];
            if (!p) return;
            const isDayPeriod = (pKey === 'morning' || pKey === 'day') ? 1 : 0;
            const iconSvg = window.WeatherIcons.getIcon(p.weather_code, isDayPeriod);
            const tempSign = p.temp_avg > 0 ? `+${p.temp_avg}` : `${p.temp_avg}`;

            html += `
                <div class="period-card">
                    <span class="period-name">${p.title}</span>
                    <div class="period-icon">${iconSvg}</div>
                    <span class="period-temp">${tempSign}°</span>
                    <span class="period-wind">${p.wind_speed} м/с</span>
                </div>
            `;
        });

        grid.innerHTML = html;
    }

    // Render Detailed Metrics
    function renderMetrics(data) {
        const t = i18n[state.lang] || i18n.ru;
        const cur = data.current;
        const day = data.selected_day;

        // Wind
        document.getElementById("metricWindSpeed").textContent = cur.wind_speed;
        const kmh = Math.round(cur.wind_speed * 3.6);
        document.getElementById("metricWindSubtext").textContent = `${cur.wind_cardinal} • ${kmh} км/ч (${cur.wind_direction}°)`;
        const needle = document.getElementById("compassNeedle");
        if (needle) {
            needle.style.transform = `rotate(${cur.wind_direction}deg)`;
        }

        // Humidity
        document.getElementById("metricHumidity").textContent = cur.humidity;
        document.getElementById("metricHumidityBar").style.width = `${cur.humidity}%`;
        let humNote = t.humidity_comfortable;
        if (cur.humidity < 40) humNote = t.humidity_dry;
        else if (cur.humidity > 75) humNote = t.humidity_humid;
        document.getElementById("metricHumidityNote").textContent = humNote;

        // UV Index
        document.getElementById("metricUvIndex").textContent = day.uv_index_max;
        let uvLevel = t.uv_low;
        let uvTip = t.uv_tip_low;
        let uvColor = "#34D399";
        let uvPercent = Math.min((day.uv_index_max / 11) * 100, 100);

        if (day.uv_index_max >= 3 && day.uv_index_max <= 5) {
            uvLevel = t.uv_moderate;
            uvTip = t.uv_tip_mod;
            uvColor = "#FBBF24";
        } else if (day.uv_index_max >= 6) {
            uvLevel = t.uv_high;
            uvTip = t.uv_tip_high;
            uvColor = "#FB7185";
        }
        document.getElementById("metricUvLevel").textContent = uvLevel;
        document.getElementById("metricUvTip").textContent = uvTip;
        const uvBar = document.getElementById("metricUvBar");
        if (uvBar) {
            uvBar.style.width = `${uvPercent}%`;
            uvBar.style.background = uvColor;
        }

        // Pressure
        document.getElementById("metricPressureMmhg").textContent = cur.pressure_mmhg;
        document.getElementById("metricPressureHpa").textContent = `${cur.pressure_hpa} гПа • ${t.pressure_normal}`;

        // Sun Cycle
        document.getElementById("sunriseTime").textContent = day.sunrise;
        document.getElementById("sunsetTime").textContent = day.sunset;
        if (day.sunrise && day.sunset && day.sunrise.includes(':') && day.sunset.includes(':')) {
            const [srH, srM] = day.sunrise.split(':').map(Number);
            const [ssH, ssM] = day.sunset.split(':').map(Number);
            let diffMins = (ssH * 60 + ssM) - (srH * 60 + srM);
            if (diffMins < 0) diffMins += 24 * 60;
            const durH = Math.floor(diffMins / 60);
            const durM = diffMins % 60;
            document.getElementById("daylightDuration").textContent = `${t.daylight}: ${durH} ${t.hours} ${durM} ${t.minutes}`;
        }

        // Precipitation
        document.getElementById("metricPrecipSum").textContent = day.precipitation_sum;
        document.getElementById("metricPrecipDetails").textContent = `Вероятность: ${day.precipitation_probability_max}% • Облачность: ${cur.cloud_cover}%`;
    }

    // Render 7-Day Extended Forecast List
    function renderWeek(forecastList) {
        const container = document.getElementById("forecast7DaysList");
        if (!container || !forecastList) return;

        let html = '';
        forecastList.forEach(item => {
            const minSign = item.temp_min > 0 ? `+${item.temp_min}` : `${item.temp_min}`;
            const maxSign = item.temp_max > 0 ? `+${item.temp_max}` : `${item.temp_max}`;
            const iconSvg = window.WeatherIcons.getIcon(item.weather_code, 1);

            html += `
                <div class="forecast-row">
                    <div>
                        <span class="forecast-day-name">${item.day_name}</span>
                        <span class="forecast-date-small">${item.date_short}</span>
                    </div>
                    <div class="forecast-icon">${iconSvg}</div>
                    <div class="forecast-desc">${item.weather_desc}</div>
                    <div class="forecast-temp-range">
                        <span class="temp-min-text">${minSign}°</span>
                        <span>•</span>
                        <span class="temp-max-text">${maxSign}°</span>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    // Bind UI Event Listeners
    function setupEventListeners() {
        // Day tabs
        const dayTabs = document.querySelectorAll(".day-tab");
        dayTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                triggerHaptic('selection');
                dayTabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");

                const offsetVal = tab.getAttribute("data-offset");
                state.offset = offsetVal === 'week' ? 'week' : parseInt(offsetVal, 10);

                if (state.offset === 'week') {
                    // Scroll down to 7-day forecast
                    const weekElem = document.getElementById("weekForecastSection");
                    if (weekElem) weekElem.scrollIntoView({ behavior: 'smooth' });
                } else {
                    loadWeather();
                }
            });
        });

        // Theme toggle
        document.getElementById("btnThemeToggle")?.addEventListener("click", () => {
            triggerHaptic('light');
            state.theme = state.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('prognoz_theme', state.theme);
            if (state.theme === 'light') {
                document.body.classList.add('theme-light');
            } else {
                document.body.classList.remove('theme-light');
            }
        });

        // Language toggle
        document.getElementById("btnLangToggle")?.addEventListener("click", () => {
            triggerHaptic('light');
            state.lang = state.lang === 'ru' ? 'en' : 'ru';
            localStorage.setItem('prognoz_lang', state.lang);
            updateUILabels();
            loadWeather();
        });

        // Search modal open/close
        const searchModal = document.getElementById("searchModal");
        const searchInput = document.getElementById("searchInput");

        document.getElementById("btnOpenSearch")?.addEventListener("click", () => {
            triggerHaptic('light');
            searchModal.classList.add("open");
            setTimeout(() => searchInput.focus(), 150);
        });

        document.getElementById("btnCloseSearch")?.addEventListener("click", () => {
            triggerHaptic('light');
            searchModal.classList.remove("open");
            searchInput.value = "";
            document.getElementById("searchResults").innerHTML = "";
        });

        // Close on outside click
        searchModal.addEventListener("click", (e) => {
            if (e.target === searchModal) {
                searchModal.classList.remove("open");
            }
        });

        // Popular search chips
        const chips = document.querySelectorAll(".search-chip");
        chips.forEach(chip => {
            chip.addEventListener("click", () => {
                triggerHaptic('selection');
                state.city = chip.getAttribute("data-city");
                state.display_name = state.city;
                state.lat = parseFloat(chip.getAttribute("data-lat"));
                state.lon = parseFloat(chip.getAttribute("data-lon"));
                state.tz = chip.getAttribute("data-tz") || 'auto';

                localStorage.setItem('prognoz_city', state.city);
                localStorage.setItem('prognoz_lat', state.lat);
                localStorage.setItem('prognoz_lon', state.lon);
                localStorage.setItem('prognoz_tz', state.tz);

                searchModal.classList.remove("open");
                loadWeather();
            });
        });

        // Search places with backend API & Open-Meteo direct geocoding fallback
        async function searchPlaces(query, lang) {
            // 1. Try local backend first
            try {
                const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}&lang=${lang}`);
                if (resp.ok) {
                    const res = await resp.json();
                    if (res && res.results && res.results.length) return res.results;
                }
            } catch (e) {
                // Ignore and fallback
            }

            // 2. Direct Open-Meteo geocoding API fallback (CORS-friendly, free, multi-language)
            try {
                const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=10&language=${lang}&format=json`;
                const resp = await fetch(url);
                if (resp.ok) {
                    const data = await resp.json();
                    if (data && data.results && data.results.length) {
                        return data.results.map(r => {
                            const parts = [r.name];
                            if (r.admin1 && r.admin1 !== r.name) parts.push(r.admin1);
                            if (r.country) parts.push(r.country);
                            return {
                                city: r.name,
                                display_name: parts.join(", "),
                                latitude: r.latitude,
                                longitude: r.longitude,
                                timezone: r.timezone || 'auto'
                            };
                        });
                    }
                }
            } catch (err) {
                console.warn("Direct geocoding error:", err);
            }
            return [];
        }

        // Reverse geocoding with backend API & BigDataCloud fallback
        async function reverseGeocode(lat, lon, lang) {
            // 1. Try local backend first
            try {
                const revResp = await fetch(`/api/reverse?lat=${lat}&lon=${lon}&lang=${lang}`);
                if (revResp.ok) {
                    const revData = await revResp.json();
                    if (revData.success && revData.city) {
                        return { city: revData.city, display_name: revData.display_name };
                    }
                }
            } catch (e) {
                // Ignore and fallback
            }

            // 2. Direct BigDataCloud reverse geocoding API fallback (CORS-friendly, free)
            try {
                const url = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=${lang}`;
                const resp = await fetch(url);
                if (resp.ok) {
                    const data = await resp.json();
                    const cityName = data.city || data.locality || data.principalSubdivision;
                    if (cityName) {
                        const parts = [cityName];
                        if (data.principalSubdivision && data.principalSubdivision !== cityName) parts.push(data.principalSubdivision);
                        if (data.countryName) parts.push(data.countryName);
                        return {
                            city: cityName,
                            display_name: parts.join(", ")
                        };
                    }
                }
            } catch (err) {
                console.warn("Direct reverse geocode error:", err);
            }

            return {
                city: lang === 'ru' ? "Мое местоположение" : "Current Location",
                display_name: `${Math.round(lat * 100) / 100}°, ${Math.round(lon * 100) / 100}°`
            };
        }

        // Debounced search input
        let searchTimer = null;
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.trim();
            clearTimeout(searchTimer);
            if (query.length < 2) {
                document.getElementById("searchResults").innerHTML = "";
                return;
            }

            searchTimer = setTimeout(async () => {
                const results = await searchPlaces(query, state.lang);
                renderSearchResults(results);
            }, 260);
        });

        // Geolocation button
        document.getElementById("btnGeolocation")?.addEventListener("click", () => {
            triggerHaptic('medium');
            const t = i18n[state.lang] || i18n.ru;
            showToast(t.geo_detecting, "🎯");

            if (!navigator.geolocation) {
                showToast(t.geo_error_toast, "⚠️");
                return;
            }

            navigator.geolocation.getCurrentPosition(
                async (pos) => {
                    triggerHaptic('success');
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    state.lat = lat;
                    state.lon = lon;

                    const geoResult = await reverseGeocode(lat, lon, state.lang);
                    state.city = geoResult.city;
                    state.display_name = geoResult.display_name;

                    localStorage.setItem('prognoz_city', state.city);
                    localStorage.setItem('prognoz_lat', state.lat);
                    localStorage.setItem('prognoz_lon', state.lon);

                    loadWeather();
                    showToast(state.city, "📍");
                },
                (err) => {
                    console.warn("Geolocation failed:", err);
                    triggerHaptic('warning');
                    showToast(t.geo_error_toast, "⚠️");
                },
                { timeout: 10000, enableHighAccuracy: true }
            );
        });

        // Save City Button
        document.getElementById("btnSaveCity")?.addEventListener("click", async () => {
            triggerHaptic('success');
            const t = i18n[state.lang] || i18n.ru;

            localStorage.setItem('prognoz_city', state.city);
            localStorage.setItem('prognoz_lat', state.lat);
            localStorage.setItem('prognoz_lon', state.lon);
            localStorage.setItem('prognoz_tz', state.tz);

            if (state.telegram_id) {
                try {
                    await fetch('/api/user', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            telegram_id: state.telegram_id,
                            city: state.city,
                            latitude: state.lat,
                            longitude: state.lon,
                            timezone: state.tz,
                            language: state.lang,
                        })
                    });
                } catch (e) {
                    console.warn("Save user error:", e);
                }
            }

            showToast(t.city_saved_toast, "⭐");
        });

        // Send to Chat Button
        document.getElementById("btnSendToChat")?.addEventListener("click", () => {
            triggerHaptic('medium');
            const t = i18n[state.lang] || i18n.ru;
            if (!state.data) return;

            const cur = state.data.current;
            const day = state.data.selected_day;
            const shareText = `🌤 ${state.city} (${day.date_formatted})\n` +
                `${cur.weather_emoji} ${cur.weather_desc}\n` +
                `🌡 Температура: ${cur.temperature > 0 ? '+' : ''}${cur.temperature}°C (ощущается как ${cur.apparent_temperature > 0 ? '+' : ''}${cur.apparent_temperature}°C)\n` +
                `📊 Мин: ${day.temp_min > 0 ? '+' : ''}${day.temp_min}°C • Макс: ${day.temp_max > 0 ? '+' : ''}${day.temp_max}°C\n` +
                `💨 Ветер: ${cur.wind_speed} м/с (${cur.wind_cardinal})\n` +
                `💧 Влажность: ${cur.humidity}%\n` +
                `🧭 Давление: ${cur.pressure_mmhg} мм рт. ст.\n` +
                `🌅 Восход: ${day.sunrise} | Закат: ${day.sunset}`;

            // Try Telegram sendData first
            if (tg && typeof tg.sendData === 'function') {
                try {
                    tg.sendData(JSON.stringify({
                        action: 'weather_share',
                        city: state.city,
                        lat: state.lat,
                        lon: state.lon,
                        summary: shareText
                    }));
                    return;
                } catch (e) {
                    console.warn("tg.sendData not available in this context:", e);
                }
            }

            // Fallback: copy to clipboard or native share
            if (navigator.clipboard) {
                navigator.clipboard.writeText(shareText)
                    .then(() => showToast(t.copied_toast, "📋"))
                    .catch(() => alert(shareText));
            } else {
                alert(shareText);
            }
        });
    }

    // Render search results
    function renderSearchResults(results) {
        const container = document.getElementById("searchResults");
        if (!container) return;

        if (!results.length) {
            container.innerHTML = '<div style="padding: 12px; text-align: center; color: var(--text-muted);">Ничего не найдено</div>';
            return;
        }

        let html = '';
        results.forEach((item, index) => {
            const admin = item.admin1 ? `${item.admin1}, ` : '';
            const sub = `${admin}${item.country || ''}`;
            html += `
                <div class="search-result-item" data-index="${index}">
                    <div>
                        <div class="search-result-name">${item.name}</div>
                        <div class="search-result-region">${sub}</div>
                    </div>
                    <span>➜</span>
                </div>
            `;
        });

        container.innerHTML = html;

        container.querySelectorAll(".search-result-item").forEach(itemElem => {
            itemElem.addEventListener("click", () => {
                const idx = parseInt(itemElem.getAttribute("data-index"), 10);
                const place = results[idx];
                if (!place) return;

                triggerHaptic('selection');
                state.city = place.name;
                state.display_name = place.display_name || place.name;
                state.lat = place.latitude;
                state.lon = place.longitude;
                state.tz = place.timezone || 'auto';

                localStorage.setItem('prognoz_city', state.city);
                localStorage.setItem('prognoz_lat', state.lat);
                localStorage.setItem('prognoz_lon', state.lon);
                localStorage.setItem('prognoz_tz', state.tz);

                document.getElementById("searchModal").classList.remove("open");
                loadWeather();
            });
        });
    }

    // Initialize application
    document.addEventListener("DOMContentLoaded", () => {
        initUserContext();
        setupEventListeners();
        loadWeather();
    });

})();
