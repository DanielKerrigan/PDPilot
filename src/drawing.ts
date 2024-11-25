import { getRaincloudData } from './vis-utils';
import { max, groups, zip, range } from 'd3-array';
import { scaleLinear } from 'd3-scale';
import { area } from 'd3-shape';
import type { RaincloudData, TwoWayPD } from './types';
import type {
  ScaleLinear,
  ScaleSequential,
  ScaleBand,
  ScaleDiverging,
  ScaleOrdinal,
} from 'd3-scale';
import type { Line } from 'd3-shape';
import { atOrValue } from './utils';

export function drawHeatmap(
  data: TwoWayPD,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleLinear<number, number> | ScaleBand<number>,
  y: ScaleLinear<number, number> | ScaleBand<number>,
  color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
  colorShows: 'predictions' | 'interactions',
  diffX: Map<number, { before: number; after: number }>,
  diffY: Map<number, { before: number; after: number }>
): void {
  ctx.save();

  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, width, height);

  for (let i = 0; i < data.x_values.length; i++) {
    const cx = data.x_values[i];
    const cy = data.y_values[i];
    const pred = data.mean_predictions[i];
    const interaction = data.interactions[i];

    ctx.fillStyle = color(colorShows === 'interactions' ? interaction : pred);

    // left position of rect
    const rectX =
      'bandwidth' in x ? x(cx) ?? 0 : x(cx - (diffX.get(cx)?.before ?? 0));

    // top position of rect
    const rectY =
      'bandwidth' in y ? y(cy) ?? 0 : y(cy + (diffY.get(cy)?.after ?? 0));

    const rectWidth =
      'bandwidth' in x
        ? x.bandwidth()
        : x(cx + (diffX.get(cx)?.after ?? 0)) - rectX;

    const rectHeight =
      'bandwidth' in y
        ? y.bandwidth()
        : y(cy - (diffY.get(cy)?.before ?? 0)) - rectY;

    ctx.fillRect(rectX, rectY, rectWidth, rectHeight);
  }

  ctx.restore();
}

export function drawScatterplot(
  ctx: CanvasRenderingContext2D | undefined,
  x: ScaleLinear<number, number> | ScaleBand<number>,
  y: ScaleLinear<number, number> | ScaleBand<number>,
  color: ScaleOrdinal<number, string> | ScaleSequential<string>,
  xValues: number[],
  yValues: number[],
  colorValues: number[],
  randomPoints: { x: number; y: number }[],
  width: number,
  height: number,
  radius: number,
  alpha: number
) {
  if (!ctx) {
    return;
  }

  const minRainCloudSize = 20;

  ctx.save();

  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, width, height);

  const I = range(xValues.length);

  if ('bandwidth' in x && 'bandwidth' in y) {
    // categorical scatterplot

    const inX = scaleLinear().domain([0, 1]).range([0, x.bandwidth()]);
    const inY = scaleLinear().domain([0, 1]).range([0, y.bandwidth()]);

    const xs = [];
    const ys = [];
    const colors = [];

    for (const i of I) {
      xs.push((x(xValues[i]) ?? 0) + inX(randomPoints[i].x));
      ys.push((y(yValues[i]) ?? 0) + inY(randomPoints[i].y));
      colors.push(color(colorValues[i]));
    }

    drawScatterPlotPoints(ctx, I, xs, ys, colors, radius, alpha);
  } else if ('bandwidth' in x && !('bandwidth' in y)) {
    if (x.bandwidth() >= minRainCloudSize) {
      // vertical raincloud plots
      const grouped = groups(zip(xValues, yValues, colorValues), (d) => d[0]);
      grouped.forEach(([key, group]) => {
        ctx.translate(x(key) ?? 0, 0);

        const values = group.map((d) => d[1]);
        const colorValues = group.map((d) => d[2]);
        const data = getRaincloudData(values, colorValues);

        drawVerticalRaincloudPlot(
          data,
          ctx,
          y,
          x.bandwidth(),
          height,
          alpha,
          'rgb(145, 145, 145)',
          'black',
          color
        );

        ctx.translate(-(x(key) ?? 0), 0);
      });
    } else {
      // vertical strip plots
      const x1 = [];
      const x2 = [];
      const ys = [];
      const colors = [];

      for (const i of I) {
        const x1Value = x(xValues[i]) ?? 0;
        x1.push(x1Value);
        x2.push(x1Value + x.bandwidth());
        ys.push(y(yValues[i]));
        colors.push(color(colorValues[i]));
      }

      drawStrips(ctx, I, x1, x2, ys, ys, colors, alpha);
    }
  } else if (!('bandwidth' in x) && 'bandwidth' in y) {
    if (y.bandwidth() >= minRainCloudSize) {
      // horizontal raincloud plots
      const grouped = groups(zip(xValues, yValues, colorValues), (d) => d[1]);
      grouped.forEach(([key, group]) => {
        ctx.translate(0, y(key) ?? 0);

        const values = group.map((d) => d[0]);
        const colorValues = group.map((d) => d[2]);
        const data = getRaincloudData(values, colorValues);

        drawHorizontalRaincloudPlot(
          data,
          ctx,
          x,
          width,
          y.bandwidth(),
          alpha,
          'rgb(145, 145, 145)',
          'black',
          color
        );

        ctx.translate(0, -(y(key) ?? 0));
      });
    } else {
      // horizontal strip plots
      const xs = [];
      const y1 = [];
      const y2 = [];
      const colors = [];

      for (const i of I) {
        const y1Value = y(yValues[i]) ?? 0;
        y1.push(y1Value);
        y2.push(y1Value + y.bandwidth());
        xs.push(x(xValues[i]));
        colors.push(color(colorValues[i]));
      }

      drawStrips(ctx, I, xs, xs, y1, y2, colors, alpha);
    }
  } else if (!('bandwidth' in x || 'bandwidth' in y)) {
    // scatterplot

    const xs = [];
    const ys = [];
    const colors = [];

    for (const i of I) {
      xs.push(x(xValues[i]));
      ys.push(y(yValues[i]));
      colors.push(color(colorValues[i]));
    }

    drawScatterPlotPoints(ctx, I, xs, ys, colors, radius, alpha);
  }

  ctx.restore();
}

function drawScatterPlotPoints(
  ctx: CanvasRenderingContext2D,
  I: number[],
  xs: number[],
  ys: number[],
  colors: string[],
  radius: number,
  globalAlpha: number
) {
  ctx.globalAlpha = globalAlpha;
  ctx.lineWidth = 1;

  const colorToIndex: [string, number[]][] = groups(I, (i) => colors[i]);

  if (globalAlpha === 1) {
    for (const [color, indices] of colorToIndex) {
      ctx.strokeStyle = color;

      ctx.beginPath();

      for (const i of indices) {
        ctx.moveTo(xs[i] + radius, ys[i]);
        ctx.arc(xs[i], ys[i], radius, 0, 2 * Math.PI);
      }

      ctx.stroke();
    }
  } else {
    for (const i of I) {
      ctx.strokeStyle = colors[i];
      ctx.beginPath();
      ctx.arc(xs[i], ys[i], radius, 0, 2 * Math.PI);
      ctx.stroke();
    }
  }
}

function drawStrips(
  ctx: CanvasRenderingContext2D,
  I: number[],
  x1: number[] | number,
  x2: number[] | number,
  y1: number[] | number,
  y2: number[] | number,
  color: string[] | string,
  globalAlpha: number
) {
  ctx.globalAlpha = globalAlpha;
  ctx.lineWidth = 1;

  const colorToIndex: [string, number[]][] = groups(I, (i) =>
    atOrValue(color, i)
  );

  if (globalAlpha === 1) {
    for (const [color, indices] of colorToIndex) {
      ctx.strokeStyle = color;

      ctx.beginPath();

      for (const i of indices) {
        ctx.moveTo(atOrValue(x1, i), atOrValue(y1, i));
        ctx.lineTo(atOrValue(x2, i), atOrValue(y2, i));
      }

      ctx.stroke();
    }
  } else {
    for (const i of I) {
      ctx.strokeStyle = atOrValue(color, i);
      ctx.beginPath();
      ctx.moveTo(atOrValue(x1, i), atOrValue(y1, i));
      ctx.lineTo(atOrValue(x2, i), atOrValue(y2, i));
      ctx.stroke();
    }
  }
}

export function drawHorizontalRaincloudPlot(
  data: RaincloudData,
  ctx: CanvasRenderingContext2D | undefined,
  x: ScaleLinear<number, number>,
  width: number,
  height: number,
  alpha: number,
  cloudColor: string,
  lightningColor: string,
  rainColor: ScaleOrdinal<number, string> | ScaleSequential<string> | string
) {
  if (!ctx) {
    return;
  }

  const padding = 2;

  const cloudHeight = scaleLinear()
    .domain([0, max(data.densities, (d) => d.density) ?? 0])
    .range([height / 2 - padding, 0]);

  const cloudArea = area<{ x: number; density: number }>()
    .x((d) => x(d.x))
    .y0(cloudHeight(0))
    .y1((d) => {
      const yCoord = cloudHeight(d.density);
      return yCoord > 0.01 ? yCoord : 0;
    })
    .context(ctx);

  ctx.save();

  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, width, height);

  // cloud

  ctx.fillStyle = cloudColor;
  ctx.beginPath();
  cloudArea(data.densities);
  ctx.fill();

  // rain

  const I = range(data.values.length);
  const colors =
    typeof rainColor === 'function'
      ? data.values.map(({ label }) => rainColor(label))
      : rainColor;
  const y1 = height / 2 + padding;
  const y2 = height;
  const xs = data.values.map(({ value }) => x(value));

  drawStrips(ctx, I, xs, xs, y1, y2, colors, alpha);

  // lightning

  ctx.globalAlpha = 1;
  ctx.lineWidth = 1;
  ctx.fillStyle = lightningColor;
  ctx.strokeStyle = 'white';
  ctx.beginPath();
  ctx.arc(x(data.mean), height / 2, 3, 0, 2 * Math.PI);
  ctx.fill();
  ctx.stroke();

  ctx.restore();
}

export function drawVerticalRaincloudPlot(
  data: RaincloudData,
  ctx: CanvasRenderingContext2D | undefined,
  y: ScaleLinear<number, number>,
  width: number,
  height: number,
  alpha: number,
  cloudColor: string,
  lightningColor: string,
  rainColor: ScaleOrdinal<number, string> | ScaleSequential<string> | string
) {
  if (!ctx) {
    return;
  }

  const padding = 2;

  const cloudWidth = scaleLinear()
    .domain([0, max(data.densities, (d) => d.density) ?? 0])
    .range([width / 2 - padding, 0]);

  const cloudArea = area<{ x: number; density: number }>()
    .x0((d) => {
      const xCoord = cloudWidth(d.density);
      return xCoord > 0.01 ? xCoord : 0;
    })
    .x1(cloudWidth.range()[0])
    .y((d) => y(d.x))
    .context(ctx);

  ctx.save();

  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, width, height);

  // cloud

  ctx.fillStyle = cloudColor;
  ctx.beginPath();
  cloudArea(data.densities);
  ctx.fill();

  // rain

  const I = range(data.values.length);
  const colors =
    typeof rainColor === 'function'
      ? data.values.map(({ label }) => rainColor(label))
      : rainColor;
  const x1 = width / 2 + padding;
  const x2 = width;
  const ys = data.values.map(({ value }) => y(value));

  drawStrips(ctx, I, x1, x2, ys, ys, colors, alpha);

  // lightning

  ctx.globalAlpha = 1;
  ctx.lineWidth = 1;
  ctx.fillStyle = lightningColor;
  ctx.strokeStyle = 'white';
  ctx.beginPath();
  ctx.arc(width / 2, y(data.mean), 3, 0, 2 * Math.PI);
  ctx.fill();
  ctx.stroke();

  ctx.restore();
}

export function drawICELines(
  ctx: CanvasRenderingContext2D,
  line: Line<number>,
  iceLines: number[][],
  indices: number[] | Set<number>,
  lineWidth: number,
  strokeStyle: string,
  globalAlpha: number
) {
  ctx.lineWidth = lineWidth;
  ctx.strokeStyle = strokeStyle;
  ctx.globalAlpha = globalAlpha;

  // if opacity is set to 1, then we can be efficient
  // and draw all of the lines in a single stroke.
  // otherwise, we have to draw each line individually
  // so that we can see darker colors where there is more
  // overlap.
  if (globalAlpha === 1) {
    ctx.beginPath();
    indices.forEach((i) => {
      line(iceLines[i]);
    });
    ctx.stroke();
  } else {
    indices.forEach((i) => {
      ctx.beginPath();
      line(iceLines[i]);
      ctx.stroke();
    });
  }
}
