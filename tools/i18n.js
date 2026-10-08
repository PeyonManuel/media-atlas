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
  const ROUTE_ES = {
    big3seinen: ['Los tres grandes del seinen', 'El trío que los lectores de seinen señalan como la cumbre del género: Berserk de Miura, Vagabond de Inoue y Monster de Urasawa.'],
    big3shonen: ['Los tres grandes de la Shōnen Jump', 'Las tres series que sostuvieron la Weekly Shōnen Jump durante los 2000.'],
    kurosawa: ['Los herederos de Kurosawa', 'George Lucas ha dicho que La fortaleza escondida dio forma a Star Wars, contada por dos campesinos que se pelean. Por un puñado de dólares de Sergio Leone es un remake no autorizado de Yojimbo.'],
    berserksouls: ['La larga sombra de Berserk', 'Hidetaka Miyazaki ha citado el Berserk de Kentaro Miura como una influencia clave en la fantasía oscura de FromSoftware.'],
    lovecraft: ['Los herederos de Lovecraft', 'El horror cósmico después de Lovecraft: La cosa de John Carpenter, Junji Ito (que cita a Lovecraft entre sus influencias) y Bloodborne de FromSoftware.'],
    killbill: ['Los ingredientes de Kill Bill', 'Tarantino construyó la venganza de la Novia sobre Lady Snowblood y eligió a Gordon Liu, estrella de La cámara 36 de Shaolin, en los dos volúmenes.'],
    square: ['La edad de oro de Square', 'Los juegos de rol de Square de 1994 a 2000, varios con música de Nobuo Uematsu.'],
    hbo: ['La edad de oro de HBO', 'Los dramas de prestigio de HBO, de Los Soprano a Chernobyl.'],
    leone: ['Leone y Morricone', 'Todas las películas de Sergio Leone que has visto tienen música de Ennio Morricone.'],
    cosmere: ['El Cosmere', 'Las novelas de Brandon Sanderson comparten un universo, unido por viajeros entre mundos como Hoid.'],
    shooters: ['De Doom a Ultrakill', 'Los shooters en primera persona que has jugado, en orden: el Doom de id, los shooters narrativos de Valve, Halo en consola y el revival retro.'],
  };
  for (const r of W.routes || []) if (ROUTE_ES[r.id]) [r.name, r.blurb] = ROUTE_ES[r.id];
}
const nfEs = d3.formatLocale({ decimal: ',', thousands: '.', grouping: [3], currency: ['', ' €'] }).format(',');
// Whole-text phrases (exact) and patterns, English to Spanish.
const PHRASES = new Map(Object.entries({
  'Ledger': 'Registro', 'Survey Ledger': 'Registro del mapa', 'Atlas': 'Atlas', 'Continent': 'Continente', 'Region': 'Región',
  'Sub-island': 'Subisla', 'Creator': 'Autor', 'Route': 'Ruta', 'KEY': 'LEYENDA',
  'Media': 'Medios', 'Summits': 'Cumbres', 'Continents': 'Continentes', 'Largest cross-media realms': 'Mayores reinos entre medios',
  'Routes · experimental': 'Rutas · experimental', 'Blind spots': 'Puntos ciegos', 'Where you part ways with the crowd': 'Donde no coincides con el público',
  'Peaks': 'Cimas', 'Lineage': 'Línea temporal', 'Works': 'Obras', 'Still in the fog': 'Aún en la niebla', 'Sub-islands': 'Subislas',
  'Portals': 'Portales', 'Length': 'Duración', 'Neighbours in this region': 'Vecinos en esta región', 'Where they sit': 'Dónde están',
  'Works, oldest first': 'Obras, de la más antigua a la más nueva', 'Regions': 'Regiones', 'Stops': 'Paradas',
  'By': 'De', 'Crowd': 'Público', 'Expansion of': 'Expansión de', 'Expansions': 'Expansiones', 'Played on': 'Jugado en',
  'Released': 'Estreno', 'Routes': 'Rutas', 'Seasons': 'Temporadas', 'Your rating': 'Tu nota', 'Not rated': 'Sin nota',
  'works charted': 'obras en el mapa', 'regions that cross media': 'regiones entre medios', 'works': 'obras', 'regions': 'regiones', 'charted': 'explorado',
  'Planned': 'Pendiente', 'Unexplored landmark': 'Hito sin explorar',
  'Colour and shape show the medium. Click one to hide it from the map.': 'El color y la forma indican el medio. Pulsa uno para ocultarlo del mapa.',
  'Bigger: your 9s and 4★ books (1.25×), 10s and 5★ books (1.5×); games also grow with length': 'Más grandes: tus 9 y libros de 4★ (1,25×), tus 10 y libros de 5★ (1,5×); los juegos también crecen con su duración',
  'The panel follows the map. Pan or zoom and it shows what you are looking at.': 'El panel sigue al mapa. Muévete o haz zoom y muestra lo que estás mirando.',
  'Surveyed from Letterboxd · Serializd · AniList · Goodreads · Backloggd · RateYourMusic, October 2026': 'Datos de Letterboxd · Serializd · AniList · Goodreads · Backloggd · RateYourMusic, octubre de 2026',
  'Each symbol is one work, shaped by its medium and sized by your rating. Continents group things by sensibility, so Berserk, Dark Souls and The First Law share the Grimlands. The land rises where you have gone deep and loved it, and the dashed rings offshore are landmarks you have not reached yet. Zoom in and the symbols turn into records, game cases, books and posters.':
    'Cada símbolo es una obra: su forma indica el medio y su tamaño, tu nota. Los continentes agrupan por sensibilidad, así que Berserk, Dark Souls y La Primera Ley comparten las Tierras Sombrías. El terreno se eleva donde más has profundizado y disfrutado, y los anillos punteados junto a la costa son hitos que aún no has alcanzado. Al acercarte, los símbolos se convierten en discos, cajas de juegos, libros y pósters.',
  'Curated threads that cross regions and media. Pick one to trace it across the map.': 'Hilos que cruzan regiones y medios. Elige uno para seguirlo por el mapa.',
  'Crowd scores come from Goodreads and AniList.': 'Las notas del público vienen de Goodreads y AniList.',
  'Not enough dated works to draw a timeline.': 'No hay suficientes obras con fecha para dibujar una línea temporal.',
  'Release order, oldest on the left. Dashed slots are landmarks you have not reached.': 'Orden de estreno, de izquierda a derecha. Los huecos punteados son hitos que aún no has alcanzado.',
  'Nothing charted here yet. Every point on this island is still in the fog.': 'Aquí aún no hay nada. Todo en esta isla sigue en la niebla.',
  'No works or regions match': 'Ninguna obra o región coincide', 'Try part of a title, an author or a region name': 'Prueba con parte de un título, un autor o una región',
  'It belongs here too. Click to go there.': 'También pertenece aquí. Pulsa para ir.', 'In progress': 'En curso', 'Web browser': 'Navegador web',
  'Map of works grouped into regions and continents by sensibility': 'Mapa de obras agrupadas en regiones y continentes por sensibilidad',
  'Map key': 'Leyenda del mapa', 'Zoom in': 'Acercar', 'Zoom out': 'Alejar', 'Show the whole map': 'Ver todo el mapa',
  'Search works, creators, regions': 'Busca obras, autores, regiones', 'Search works, creators and regions': 'Busca obras, autores y regiones',
}));
const PATTERNS = [
  [/^A survey of ([\d,.]+) works read, watched, played and heard, arranged by what they are rather than where they came from\.$/, 'Un mapa de $1 obras leídas, vistas, jugadas y escuchadas, ordenadas por lo que son y no por su origen.'],
  [/^regions on (\d+) continents$/, 'regiones en $1 continentes'],
  [/^Your (\d+) perfect scores, newest first\. Select one to find it on the map\.$/, 'Tus $1 notas perfectas, de la más reciente a la más antigua. Elige una para encontrarla en el mapa.'],
  [/^Charted share counts works against the ([\d,.]+) landmarks still in the fog\.$/, 'El porcentaje explorado compara tus obras con los $1 hitos que siguen en la niebla.'],
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
  [/^(.*)\. Longer than (\d+)% of your (.*)\.$/, (m, a, p, n) => `${trText(a)}. Más largo que el ${p} % de tus ${{ books: 'libros', comics: 'cómics', 'manga series': 'mangas', shows: 'series', games: 'juegos' }[n] || n}.`],
  [/^(\d+) on AniList, counted as one show$/, '$1 en AniList, contadas como una serie'],
  [/^All (\d+) works by (.*)$/, 'Las $1 obras de $2'],
  [/^([\d.,]+)\/(5|10) average$/, 'media de $1/$2'], [/^ \/ 10, your Serializd rating for the show$/, ' / 10, tu nota de Serializd para la serie'],
  [/^ \/ 10, average of rated seasons$/, ' / 10, media de las temporadas puntuadas'],
  [/^(.*) · you (.*), crowd (.*)$/, '$1 · tú $2, público $3'],
  [/^(\d+) works across (\d+) regions?\. Everything else on the map is dimmed\.$/, '$1 obras en $2 regiones. El resto del mapa queda atenuado.'],
  [/^(\d+) stops across (.*)\. Routes are an experiment: curated links that cross regions\.$/, '$1 paradas en $2. Las rutas son un experimento: enlaces que cruzan regiones.'],
  [/^Open on (.*) ↗$/, 'Abrir en $1 ↗'], [/^Creator · (\d+) works$/, 'Autor · $1 obras'], [/^Region · (.*)$/, 'Región · $1'],
  [/^Portal to (.*), on (.*)$/, 'Portal a $1, en $2'], [/^Portal to (.*)$/, 'Portal a $1'], [/^has a portal here \((.*)\)$/, 'tiene un portal aquí ($1)'],
  [/^Unexplored landmark(.*)$/, 'Hito sin explorar$1'], [/^(\d+) \/ 5$/, '$1 / 5'],
  [/^Around (.*): none of yours\.$/, 'Alrededor de $1: ninguna tuya.'],
  [/^(.*) to (.*): (\d+) of yours, (.*)$/, '$1 a $2: $3 tuyas, $4'],
  [/^Length compared with your other (.*)$/, 'Duración comparada con tus otros $1'], [/^Timeline of (.*)$/, 'Línea temporal de $1'],
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
