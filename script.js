let currentMonth = 'ENE';
let stationsVisible = true;
let playInterval = null;
let isPlaying = false;
let currentLang = 'en';
const monthsOrder = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC', 'Annual'];

const translations = {
    en: {
        title: "Solar Colombia | Radiation Dashboard",
        headerTitle1: "Solar",
        headerTitle2: "Colombia",
        headerSubtitle: "Spatial Radiation Analysis • IDEAM Station Network",
        btnPlay: "Play Year",
        btnPause: "Pause",
        monthSelector: {
            ENE: "January", FEB: "February", MAR: "March", ABR: "April",
            MAY: "May", JUN: "June", JUL: "July", AGO: "August",
            SEP: "September", OCT: "October", NOV: "November", DIC: "December",
            Annual: "Annual Average"
        },
        btnStations: "Stations",
        spatialAnalysis: "Spatial Analysis",
        methodology: "Methodology",
        model: "Model",
        grid: "Grid",
        gridPoints: "8,000 Points",
        footnote: "Values outside national boundaries have been removed using a geographical mask for territorial precision.",
        initError: "Initialization Error",
        loadError: "Error loading resources",
        solarPotential: "Solar Potential",
        potentials: {
            Bajo: "Low", Moderado: "Moderate", Alto: "High", Excelente: "Excellent"
        },
        stats: {
            average: "Average", maximum: "Maximum", regionalLeader: "Regional Leader",
            peakValue: "Peak Value", p90Index: "P90 Index (Guarantee)", nationalVariability: "Nat. Variability"
        }
    },
    es: {
        title: "Solar Colombia | Dashboard de Radiación",
        headerTitle1: "Solar",
        headerTitle2: "Colombia",
        headerSubtitle: "Análisis Espacial de Radiación • Red de estaciones IDEAM",
        btnPlay: "Reproducir Año",
        btnPause: "Pausar",
        monthSelector: {
            ENE: "Enero", FEB: "Febrero", MAR: "Marzo", ABR: "Abril",
            MAY: "Mayo", JUN: "Junio", JUL: "Julio", AGO: "Agosto",
            SEP: "Septiembre", OCT: "Octubre", NOV: "Noviembre", DIC: "Diciembre",
            Annual: "Promedio Anual"
        },
        btnStations: "Estaciones",
        spatialAnalysis: "Análisis Espacial",
        methodology: "Metodología",
        model: "Modelo",
        grid: "Malla",
        gridPoints: "8,000 Puntos",
        footnote: "Los valores fuera del límite nacional han sido removidos mediante máscara geográfica para precisión territorial.",
        initError: "Error de Inicialización",
        loadError: "Error al cargar recursos",
        solarPotential: "Potencial Solar",
        potentials: {
            Bajo: "Bajo", Moderado: "Moderado", Alto: "Alto", Excelente: "Excelente"
        },
        stats: {
            average: "Promedio", maximum: "Máximo", regionalLeader: "Líder Regional",
            peakValue: "Valor Pico", p90Index: "Índice P90 (Garantía)", nacionalVariability: "Variabilidad Nac."
        }
    },
    de: {
        title: "Solar Kolumbien | Strahlungs-Dashboard",
        headerTitle1: "Solar",
        headerTitle2: "Kolumbien",
        headerSubtitle: "Räumliche Strahlungsanalyse • IDEAM-Stationsnetz",
        btnPlay: "Jahr abspielen",
        btnPause: "Pause",
        monthSelector: {
            ENE: "Januar", FEB: "Februar", MAR: "März", ABR: "April",
            MAY: "Mai", JUN: "Juni", JUL: "Juli", AGO: "August",
            SEP: "September", OCT: "Oktober", NOV: "November", DIC: "Dezember",
            Annual: "Jahresdurchschnitt"
        },
        btnStations: "Stationen",
        spatialAnalysis: "Räumliche Analyse",
        methodology: "Methodik",
        model: "Modell",
        grid: "Gitter",
        gridPoints: "8.000 Punkte",
        footnote: "Werte außerhalb der Landesgrenzen wurden mittels geografischer Maskierung für territoriale Präzision entfernt.",
        initError: "Initialisierungsfehler",
        loadError: "Fehler beim Laden der Ressourcen",
        solarPotential: "Solarpotenzial",
        potentials: {
            Bajo: "Niedrig", Moderado: "Moderat", Alto: "Hoch", Excelente: "Exzellent"
        },
        stats: {
            average: "Durchschnitt", maximum: "Maximum", regionalLeader: "Regionaler Führer",
            peakValue: "Spitzenwert", p90Index: "P90-Index (Garantie)", nationalVariability: "Nat. Variabilität"
        }
    }
};

function setLanguage(lang) {
    currentLang = lang;
    document.documentElement.lang = lang;
    document.getElementById('lang-selector').value = lang;

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });

    document.title = translations[lang].title;

    const selector = document.getElementById('month-selector');
    const currentValue = selector.value;
    selector.innerHTML = '';
    monthsOrder.forEach(month => {
        const option = document.createElement('option');
        option.value = month;
        option.innerText = translations[lang].monthSelector[month];
        selector.appendChild(option);
    });
    selector.value = currentValue;

    const btnPlay = document.getElementById('btn-play');
    if (isPlaying) {
        btnPlay.querySelector('span').innerText = translations[lang].btnPause;
    } else {
        btnPlay.querySelector('span').innerText = translations[lang].btnPlay;
    }

    if (window.dashboardData) {
        updateMap(currentMonth);
    }
}

async function initializeMap() {
    try {
        const response = await fetch('dashboard_data.json');
        if (!response.ok) throw new Error(translations[currentLang].loadError);
        window.dashboardData = await response.json();
        await updateMap('ENE');
    } catch (error) {
        console.error("Init Error:", error);
        document.getElementById('map-container').innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-red-400 p-8 text-center">
                <i class="fas fa-triangle-exclamation text-4xl mb-4"></i>
                <p class="font-bold">${translations[currentLang].initError}</p>
                <p class="text-xs opacity-60 mt-2">${error.message}</p>
            </div>`;
    }
}

async function updateMap(month) {
    currentMonth = month;
    const selector = document.getElementById('month-selector');
    if (selector) selector.value = month;

    const interpData = window.dashboardData.interpolation[month];
    const stations = window.dashboardData.stations;
    const stats = window.dashboardData.stats[month];

    if (!interpData || !stats) {
        console.warn("No data for month:", month);
        return;
    }

    const globalMin = 1.5;
    const globalMax = 6.5;

    const krigingTrace = {
        type: 'densitymapbox',
        lat: interpData.lat,
        lon: interpData.lon,
        z: interpData.z,
        radius: 10,
        colorscale: 'Jet',
        zmin: globalMin,
        zmax: globalMax,
        opacity: 0.6,
        showscale: false,
        hoverinfo: 'none'
    };

    const stationsTrace = {
        type: 'scattermapbox',
        lat: stations.map(s => s.lat),
        lon: stations.map(s => s.lon),
        mode: 'markers',
        marker: {
            size: 8,
            color: stations.map(s => s[month]),
            colorscale: 'Jet',
            cmin: globalMin, cmax: globalMax,
            showscale: true,
            line: { color: 'white', width: 1 },
            colorbar: {
                thickness: 15,
                len: 0.5,
                title: { text: 'kWh/m²', font: { color: '#94a3b8' } },
                tickfont: { color: '#94a3b8' }
            }
        },
        text: stations.map(s => `<b>${s.name}</b><br>${s[month].toFixed(2)} kWh/m²`),
        hoverinfo: 'text',
        visible: stationsVisible
    };

    const layout = {
        mapbox: {
            style: 'carto-darkmatter',
            center: { lat: 4.5, lon: -73.5 },
            zoom: 4.0
        },
        margin: { t: 0, b: 0, l: 0, r: 0 },
        showlegend: false,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.react('map-container', [krigingTrace, stationsTrace], layout, { responsive: true, displayModeBar: false });
    renderStats(stats, month);
}

function renderStats(stats, month) {
    const t = translations[currentLang].stats;
    const potentialTranslated = translations[currentLang].potentials[stats.potential];

    let color, bg;
    switch (stats.potential) {
        case 'Excelente': color = 'text-emerald-400'; bg = 'bg-emerald-500/10'; break;
        case 'Alto': color = 'text-orange-400'; bg = 'bg-orange-500/10'; break;
        case 'Moderado': color = 'text-yellow-400'; bg = 'bg-yellow-500/10'; break;
        default: color = 'text-red-400'; bg = 'bg-red-500/10';
    }

    document.getElementById('stats-container').innerHTML = `
        <div class="${bg} p-2.5 rounded-xl mb-2 border border-white/5 text-center transition-all">
            <p class="text-[10px] uppercase font-bold text-slate-400 mb-0.5 tracking-widest">${translations[currentLang].solarPotential}</p>
            <p class="text-lg font-black ${color}">${potentialTranslated}</p>
        </div>
        
        <div class="grid grid-cols-2 gap-2 mb-2">
            <div class="bg-white/5 p-2 rounded-xl border border-white/5 text-center">
                <p class="text-[9px] text-slate-400 uppercase font-bold tracking-tighter">${t.average}</p>
                <p class="text-sm font-bold text-white">${stats.mean.toFixed(2)}</p>
            </div>
            <div class="bg-white/5 p-2 rounded-xl border border-white/5 text-center">
                <p class="text-[9px] text-slate-400 uppercase font-bold tracking-tighter">${t.maximum}</p>
                <p class="text-sm font-bold text-white">${stats.max.toFixed(2)}</p>
            </div>
        </div>

        <div class="mb-2">
            <h4 class="text-[9px] uppercase font-bold text-slate-500 mb-2 tracking-widest flex items-center gap-2">
                <i class="fas fa-crown text-yellow-500 text-[8px]"></i> ${t.regionalLeader}
            </h4>
            <div class="p-2 bg-gradient-to-br from-white/10 to-transparent rounded-xl border border-white/10 flex items-center justify-between">
                <div class="flex flex-col">
                    <span class="text-[12px] font-bold text-white tracking-tight">${stats.leader.dept}</span>
                    <span class="text-[8px] uppercase font-bold text-slate-500">${t.peakValue}</span>
                </div>
                <div class="text-right">
                    <span class="text-base font-black text-orange-400">${stats.leader.val.toFixed(2)}</span>
                    <span class="text-[8px] block font-bold text-slate-500">kWh/m²</span>
                </div>
            </div>
        </div>

        <div class="space-y-2 pt-1 border-t border-white/5">
            <div class="flex justify-between items-center text-[9px]">
                <span class="text-slate-400 uppercase font-bold text-[9px]">${t.p90Index}</span>
                <span class="font-bold text-emerald-400">${stats.p90.toFixed(2)}</span>
            </div>
            <div class="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-emerald-600 to-emerald-400" style="width: ${(stats.p90 / 7 * 100).toFixed(0)}%"></div>
            </div>
            
            <div class="flex justify-between items-center text-[9px]">
                <span class="text-slate-400 uppercase font-bold text-[9px]">${t.nationalVariability}</span>
                <span class="font-bold text-orange-400">${(stats.max - stats.min).toFixed(2)}</span>
            </div>
        </div>
    `;
}

function togglePlay() {
    const btn = document.getElementById('btn-play');
    isPlaying = !isPlaying;
    if (isPlaying) {
        btn.classList.add('bg-red-500/10', 'border-red-500/20', 'text-red-400');
        btn.classList.remove('bg-emerald-500/10', 'border-emerald-500/20', 'text-emerald-400');
        btn.innerHTML = `<i class="fas fa-pause"></i><span>${translations[currentLang].btnPause}</span>`;
        playInterval = setInterval(() => {
            let next = (monthsOrder.indexOf(currentMonth) + 1) % 12;
            updateMap(monthsOrder[next]);
        }, 1500);
    } else {
        clearInterval(playInterval);
        btn.classList.remove('bg-red-500/10', 'border-red-500/20', 'text-red-400');
        btn.classList.add('bg-emerald-500/10', 'border-emerald-500/20', 'text-emerald-400');
        btn.innerHTML = `<i class="fas fa-play"></i><span>${translations[currentLang].btnPlay}</span>`;
    }
}

function toggleStations() {
    stationsVisible = !stationsVisible;
    const icon = document.getElementById('station-icon');
    icon.className = stationsVisible ? 'fas fa-location-dot text-red-500' : 'fas fa-location-dot text-slate-500';
    updateMap(currentMonth);
}

document.addEventListener('DOMContentLoaded', () => {
    setLanguage('en');
    initializeMap();
});
