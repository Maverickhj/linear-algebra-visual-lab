/* One SVG renderer for the interactive view and the committed static figure. */
(function (root) {
  'use strict';
  const colors = { a: '#2563a6', b: '#9c641d', sum: '#087d79', axis: '#68777d' };
  const origin = [320, 300];
  const scale = 36;
  const point = vector => [origin[0] + scale * vector[0], origin[1] - scale * vector[1]];
  const pair = vector => `(${vector.join(', ')})`;

  function svg(result) {
    const parts = [];
    for (let value = -6; value <= 6; value++) {
      if (value === 0) continue;
      const [x, y] = point([value, value]);
      parts.push(`<path d="M ${x} 48 V 552 M 68 ${y} H 572" stroke="#e7ebe7" fill="none"/>`);
      if (value % 2 === 0) {
        parts.push(`<text x="${x}" y="323" text-anchor="middle">${value}</text><text x="306" y="${y + 5}" text-anchor="end">${value}</text>`);
      }
    }
    const vectors = [];
    function arrow(name, start, end, dashed, width) {
      const p = point(start), q = point(end);
      if (p[0] === q[0] && p[1] === q[1]) return;
      vectors.push(`<line data-vector="${dashed ? 'translated-' : ''}${name}" x1="${p[0]}" y1="${p[1]}" x2="${q[0]}" y2="${q[1]}" stroke="${colors[name]}" stroke-width="${width}" ${dashed ? 'stroke-dasharray="7 5"' : ''} marker-end="url(#arrow-${name})"/>`);
    }
    arrow('b', result.a, result.sum, true, 2.3);
    arrow('a', result.b, result.sum, true, 2.3);
    arrow('sum', [0, 0], result.sum, false, 4);
    arrow('a', [0, 0], result.a, false, 2.5);
    arrow('b', [0, 0], result.b, false, 2.5);
    const labels = [];
    const placed = [];
    for (const [name, vector, label] of [['a', result.a, 'a'], ['b', result.b, 'b'], ['sum', result.sum, 'a + b']]) {
      const [x, y] = point(vector);
      // Stack labels at coincident endpoints (zero vectors, equal vectors).
      let labelY = y - 14;
      while (placed.some(p => Math.abs(p[0] - x) < 70 && Math.abs(p[1] - labelY) < 23)) labelY -= 24;
      placed.push([x, labelY]);
      const zero = vector.every(v => v === 0);
      if (zero) labels.push(`<circle data-zero="${name}" cx="${x}" cy="${y}" r="${5 + (name === 'sum' ? 4 : name === 'b' ? 2 : 0)}" fill="none" stroke="${colors[name]}" stroke-width="2"/>`);
      labels.push(`<text x="${x + 12}" y="${labelY}" fill="${colors[name]}" font-family="Georgia,serif" font-size="21" font-style="italic" stroke="white" stroke-width="5" paint-order="stroke">${label}${zero ? ' = 0' : ''}</text>`);
    }
    const markers = Object.entries(colors).map(([name, color]) => `<marker id="arrow-${name}" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M 0 0 L 8 4 L 0 8 Z" fill="${color}"/></marker>`).join('');
    return `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="600" viewBox="0 0 640 600" role="img" aria-labelledby="vector-title vector-desc">
<title id="vector-title">向量加法：a ${pair(result.a)}，b ${pair(result.b)}，和 ${pair(result.sum)}</title>
<desc id="vector-desc">横轴向右，纵轴向上，横纵同一单位长度。蓝色 a 与棕色 b 从原点出发，虚线表示平移后首尾相接的路径，绿色 a + b 到达共同终点。零向量用圆环表示。</desc>
<defs>${markers}</defs>
<rect width="640" height="600" fill="white"/>
<g font-family="system-ui,sans-serif" font-size="14" fill="${colors.axis}">${parts.join('')}</g>
<path d="M 320 564 V 36" fill="none" stroke="${colors.axis}" stroke-width="1.5" marker-end="url(#arrow-axis)"/>
<path d="M 56 300 H 584" fill="none" stroke="${colors.axis}" stroke-width="1.5" marker-end="url(#arrow-axis)"/>
<g font-family="Georgia,serif" font-size="20" fill="#172c36"><text x="598" y="306">x</text><text x="329" y="28">y</text><text x="300" y="323" font-size="14">0</text></g>
<circle cx="320" cy="300" r="3" fill="#172c36"/>
${vectors.join('\n')}
${labels.join('\n')}
<text x="320" y="590" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#536870">虚线 = 平移副本 · 横纵比例 1 : 1</text>
</svg>`;
  }
  const view = { svg, point, scale };
  root.VectorAdditionView = view;
  if (typeof module !== 'undefined' && module.exports) module.exports = view;
})(typeof window === 'undefined' ? globalThis : window);
