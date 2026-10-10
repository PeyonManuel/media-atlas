// ---------- language: Spanish when the browser prefers it ----------
// The map's data carries its own Spanish (island descriptions); the interface is translated as it is
// rendered: a phrase table rewrites text and labels in the panel, key, tooltip and search results.
const ES = (navigator.languages && navigator.languages.length ? navigator.languages[0] : navigator.language || 'en').toLowerCase().startsWith('es');
document.documentElement.lang = ES ? 'es' : 'en';
if (ES) {
  Object.assign(MEDIA_LABEL, { film: 'Cine', tv: 'Series', manga: 'Manga', comics: 'Cómics', books: 'Libros', game: 'Juegos', music: 'Música' });
  Object.assign(STATUS_LABEL, { done: 'Terminado', active: 'En curso', paused: 'En pausa', dropped: 'Abandonado', planned: 'Pendiente' });
  const CONT_ES = {
    grim: ['Las Tierras Sombrías', 'Ceniza, sangre y heroísmo sombrío: fantasía oscura en todos los medios.'],
    fantasy: ['El Confín de la Alta Fantasía', 'Mundos secundarios, sistemas de magia y largas búsquedas.'],
    space: ['La Frontera Estelar', 'Ciencia ficción, de la ópera espacial al cyberpunk.'],
    crime: ['El Inframundo', 'Mafiosos, detectives, traficantes y las ciudades que dominan.'],
    horror: ['La Ciénaga Encantada', 'Zombis, terror cósmico y cosas en la oscuridad.'],
    heroes: ['Capas y Shōnen', 'Superhéroes y shōnen de combate: fantasías de poder contadas con sinceridad.'],
    samurai: ['El Camino de la Espada', 'Samuráis, ronin y artes marciales.'],
    war: ['Campos de la Historia', 'Guerra, imperio y la épica histórica.'],
    western: ['La Frontera', 'Westerns, pistoleros y senderos solitarios.'],
    heart: ['El Corazón', 'Drama, romance, crecer y la vida tranquila.'],
    surreal: ['La Costa Onírica', 'Lo extraño, lo experimental y lo que retuerce la mente.'],
    play: ['Los Patios de Juego', 'Plataformas, comedia, cine familiar y diversión pura.'],
    action: ['La Costa de la Acción', 'Explosiones, superproducciones, shooters y adrenalina.'],
    build: ['La Meseta del Estratega', 'Estrategia, automatización, simulación e ideas.'],
    classic: ['Los Viejos Maestros', 'El canon: del cine mudo a los discos de la edad de oro.'],
    sports: ['La Arena', 'Rings de boxeo, canchas y las ganas de ganar.'],
  };
  for (const c of W.continents) if (CONT_ES[c.id]) [c.name, c.blurb] = CONT_ES[c.id];
  for (const p of W.provinces) if (p.blurb_es) p.blurb = p.blurb_es;
  for (const pt of W.portals || []) if (pt.label_es) pt.label = pt.label_es;
  for (const r of W.routes || []) if (r.name_es) [r.name, r.blurb] = [r.name_es, r.blurb_es];
}
const nfEs = d3.formatLocale({ decimal: ',', thousands: '.', grouping: [3], currency: ['', ' €'] }).format(',');
// Whole-text phrases (exact) and patterns, English to Spanish.
const PHRASES = new Map(Object.entries({
  'Ledger': 'Registro', 'Survey Ledger': 'Registro del mapa', 'Atlas': 'Atlas', 'Continent': 'Continente', 'Region': 'Región',
  'Sub-island': 'Subisla', 'Creator': 'Autor', 'Route': 'Ruta', 'KEY': 'LEYENDA',
  'Media': 'Medios', 'Summits': 'Cumbres', 'Continents': 'Continentes', 'Largest cross-media realms': 'Mayores reinos entre medios',
  'Connections': 'Conexiones', 'Connection': 'Conexión', 'Following': 'Siguiendo', 'Stop following': 'Dejar de seguir', 'Followed connections': 'Conexiones seguidas', 'Show them all on the map': 'Mostrarlas todas en el mapa', 'Hide them on the map': 'Ocultarlas del mapa',
  'Threads between works that sit apart on the map: who drew on whom, one hand or one composer across genres, one world in several media.': 'Hilos entre obras que están lejos en el mapa: quién se inspiró en quién, un mismo autor o compositor en varios géneros, un mismo mundo en varios medios.',
  'Blind spots': 'Puntos ciegos', 'At odds with the crowd': 'En desacuerdo con el público',
  'Peaks': 'Cimas', 'Lineage': 'Línea temporal', 'Works': 'Obras', 'Still in the fog': 'Aún en la niebla', 'Sub-islands': 'Subislas',
  'Portals': 'Portales', 'Length': 'Duración', 'Neighbours in this region': 'Vecinos en esta región', 'Where they sit': 'Dónde están',
  'Works, oldest first': 'Obras, de la más antigua a la más nueva', 'Regions': 'Regiones', 'Stops': 'Paradas',
  'By': 'De', 'Crowd': 'Público', 'Expansion of': 'Expansión de', 'Expansions': 'Expansiones', 'Played on': 'Jugado en',
  'Released': 'Estreno', 'Routes': 'Rutas', 'Seasons': 'Temporadas', 'Manu\'s rating': 'Nota de Manu', 'Not rated': 'Sin nota',
  'works charted': 'obras en el mapa', 'regions that cross media': 'regiones entre medios', 'works': 'obras', 'regions': 'regiones', 'charted': 'explorado',
  'Planned': 'Pendiente', 'Unexplored landmark': 'Hito sin explorar',
  'Colour and shape show the medium; each chip toggles its medium on the map.': 'El color y la forma indican el medio; cada etiqueta muestra u oculta su medio en el mapa.',
  'Bigger: 9s (1.35×) and 10s (1.7×); longer works are bigger too': 'Más grandes: los 9 (1,35×) y los 10 (1,7×); y lo más largo, más grande',
  'The panel follows the map, showing whatever is in view.': 'El panel sigue al mapa y muestra lo que está a la vista.',
  'Surveyed from Letterboxd · Serializd · AniList · Goodreads · Backloggd · RateYourMusic, October 2026': 'Datos de Letterboxd · Serializd · AniList · Goodreads · Backloggd · RateYourMusic, octubre de 2026',
  'Each symbol is one work, shaped by its medium and sized by its rating and its length. Continents group things by sensibility, so Berserk, Dark Souls and The First Law share the Grimlands. The land rises where the ratings run high: the higher the ground, the higher the scores there, and the dashed rings offshore are landmarks not yet reached. Up close, the symbols turn into records, game cases, books and posters.':
    'Cada símbolo es una obra: su forma indica el medio y su tamaño, su nota y su duración. Los continentes agrupan por sensibilidad, así que Berserk, Dark Souls y La Primera Ley comparten las Tierras Sombrías. El terreno se eleva donde las notas son altas: cuanto más alto, mejores las notas, y los anillos punteados junto a la costa son hitos aún no alcanzados. De cerca, los símbolos se convierten en discos, cajas de juegos, libros y pósters.',
  'Curated threads that cross regions and media, each traced across the map.': 'Hilos que cruzan regiones y medios, cada uno trazado sobre el mapa.',
  'Crowd scores come from Goodreads and AniList.': 'Las notas del público vienen de Goodreads y AniList.',
  'Not enough dated works to draw a timeline.': 'No hay suficientes obras con fecha para dibujar una línea temporal.',
  'Release order, oldest on the left. Dashed slots are landmarks not yet reached.': 'Orden de estreno, de izquierda a derecha. Los huecos punteados son hitos aún no alcanzados.',
  'Nothing charted here yet. Every point on this island is still in the fog.': 'Aquí aún no hay nada. Todo en esta isla sigue en la niebla.',
  'No works or regions match': 'Ninguna obra o región coincide', 'Search covers titles, authors and region names': 'La búsqueda abarca títulos, autores y regiones',
  'It belongs here too, and links there.': 'También pertenece aquí y enlaza allí.', 'In progress': 'En curso', 'Web browser': 'Navegador web',
  'Map of works grouped into regions and continents by sensibility': 'Mapa de obras agrupadas en regiones y continentes por sensibilidad',
  'Map key': 'Leyenda del mapa', 'Zoom in': 'Acercar', 'Zoom out': 'Alejar', 'Show the whole map': 'Ver todo el mapa',
  'Search works, creators, regions': 'Busca obras, autores, regiones', 'Search works, creators and regions': 'Busca obras, autores y regiones',
}));
const PATTERNS = [
  [/^A survey of ([\d,.]+) works read, watched, played and heard, arranged by what they are rather than where they came from\.$/, 'Un mapa de $1 obras leídas, vistas, jugadas y escuchadas, ordenadas por lo que son y no por su origen.'],
  [/^regions on (\d+) continents$/, 'regiones en $1 continentes'],
  [/^(\d+) perfect scores, newest first, each linked to its place on the map\.$/, '$1 notas perfectas, de la más reciente a la más antigua, cada una enlazada a su lugar en el mapa.'],
  [/^Charted share counts works against the ([\d,.]+) landmarks still in the fog\.$/, 'El porcentaje explorado compara las obras con los $1 hitos que siguen en la niebla.'],
  [/^(\d+) stops$/, '$1 paradas'], [/^Show all (\d+)$/, 'Ver las $1'], [/^Unvisited: (.*)$/, 'Sin visitar: $1'],
  [/^([\d,.]+) works, (\d+) landmarks in the fog$/, '$1 obras, $2 hitos en la niebla'],
  [/^A cross-media realm in (.*)\.$/, 'Un reino entre medios en $1.'],
  [/^A (series|cross-media realm|realm) on (.*), in (.*)\.$/, (m, k, a, b) => `${{ series: 'Una serie', 'cross-media realm': 'Un reino entre medios', realm: 'Un reino' }[k]} en ${a}, en ${b}.`],
  [/^A region of (.*)\.$/, 'Una región de $1.'], [/^(.*), in (.*)\.$/, '$1, en $2.'],
  [/^Series not finished: (\d+) of (\d+) books$/, 'Serie sin terminar: $1 de $2 libros'], [/^Series complete: all (\d+) books$/, 'Serie completa: los $1 libros'],
  [/^About ([\d,.]+) hours$/, 'Unas $1 horas'], [/^About ([\d,.]+) hours \(main story \+ extras\)$/, 'Unas $1 horas (historia + extras)'],
  [/^About ([\d,.]+) h( across (\d+) seasons)?$/, (m, a, b, c) => `Unas ${a} h${c ? ` en ${c} temporadas` : ''}`],
  [/^About ([\d,.]+) pages, ([\d,.]+) h of reading$/, 'Unas $1 páginas, $2 h de lectura'],
  [/^Main story ([\d,.]+ h) · with extras ([\d,.]+ h) · everything ([\d,.]+ h)$/, 'Historia $1 · con extras $2 · todo $3'],
  [/^([\d,.]+) (pages|chapters|episodes|minutes)$/, (m, n, u) => `${n} ${{ pages: 'páginas', chapters: 'capítulos', episodes: 'episodios', minutes: 'minutos' }[u]}`],
  [/^(.*)\. Longer than (\d+)% of the (.*) on the map\.$/, (m, a, p, n) => `${trText(a)}. Más largo que el ${p} % de ${{ books: 'los libros', comics: 'los cómics', 'manga series': 'los mangas', shows: 'las series', games: 'los juegos' }[n] || n} del mapa.`],
  [/^(\d+) on AniList, counted as one show$/, '$1 en AniList, contadas como una serie'],
  [/^All (\d+) works by (.*)$/, 'Las $1 obras de $2'],
  [/^([\d.,]+)\/(5|10) average$/, 'media de $1/$2'], [/^\/ 10, Serializd rating for the show$/, '/ 10, nota de Serializd para la serie'],
  [/^\/ 10, average of rated seasons$/, '/ 10, media de las temporadas puntuadas'],
  [/^(.*) · Manu (.*), crowd (.*)$/, '$1 · Manu $2, público $3'],
  [/^(\d+) works across (\d+) regions?\. Everything else on the map is dimmed\.$/, '$1 obras en $2 regiones. El resto del mapa queda atenuado.'],
  [/^(\d+) stops across (.*)\.$/, '$1 paradas en $2.'], [/^Connections (\d+)$/, 'Conexiones $1'], [/^Connection · (\d+) stops$/, 'Conexión · $1 paradas'],
  [/^(\d+) stops · (.*)$/, (m, n, a) => `${n} paradas · ${a.split(' · ').map(trText).join(' · ')}`],
  [/^Open on (.*) ↗$/, 'Abrir en $1 ↗'], [/^Creator · (\d+) works$/, 'Autor · $1 obras'], [/^Region · (.*)$/, 'Región · $1'],
  [/^Portal to (.*), on (.*)$/, 'Portal a $1, en $2'], [/^Portal to (.*)$/, 'Portal a $1'], [/^has a portal here \((.*)\)$/, 'tiene un portal aquí ($1)'],
  [/^Unexplored landmark(.*)$/, 'Hito sin explorar$1'], [/^(\d+) \/ 5$/, '$1 / 5'],
  [/^Around (.*): no works\.$/, 'Alrededor de $1: ninguna obra.'],
  [/^(.*) to (.*): (\d+) works, (.*)$/, '$1 a $2: $3 obras, $4'],
  [/^Length compared with the other (.*) on the map$/, 'Duración comparada con el resto de $1 del mapa'], [/^Timeline of (.*)$/, 'Línea temporal de $1'],
];
function trText(s) {
  if (!ES || !s) return s;
  const lead = s.match(/^\s*/)[0], tail = s.match(/\s*$/)[0], core = s.trim();
  if (!core) return s;
  if (PHRASES.has(core)) return lead + PHRASES.get(core) + tail;
  for (const [rx, rep] of PATTERNS) if (rx.test(core)) return lead + core.replace(rx, rep) + tail;
  return s;
}
function translateTree(root) {
  if (!ES || !root) return;
  if (root.nodeType === 3) { const t = trText(root.nodeValue); if (t !== root.nodeValue) root.nodeValue = t; return; }
  if (root.nodeType !== 1) return;
  for (const a of ['aria-label', 'title', 'placeholder']) { const v = root.getAttribute(a); if (v) { const t = trText(v); if (t !== v) root.setAttribute(a, t); } }
  const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
  while (tw.nextNode()) {
    const n = tw.currentNode;
    if (n.nodeType === 3) { const t = trText(n.nodeValue); if (t !== n.nodeValue) n.nodeValue = t; }
    else for (const a of ['aria-label', 'title', 'placeholder']) { const v = n.getAttribute(a); if (v) { const t = trText(v); if (t !== v) n.setAttribute(a, t); } }
  }
}
if (ES) {
  const mo = new MutationObserver(recs => {
    mo.disconnect();
    for (const r of recs) {
      if (r.type === 'characterData') translateTree(r.target);
      for (const n of r.addedNodes) translateTree(n);
    }
    watch();
  });
  const watch = () => mo.observe(document.body, { childList: true, subtree: true, characterData: true });
  translateTree(document.body);
  watch();
}
