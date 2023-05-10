import type { TwoWayPD } from './types';

import { scaleLinear } from 'd3-scale';

import type {
  ScaleLinear,
  ScaleSequential,
  ScaleBand,
  ScaleDiverging,
  ScaleOrdinal,
} from 'd3-scale';

export function drawHeatmap(
  data: TwoWayPD,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleLinear<number, number> | ScaleBand<number>,
  y: ScaleLinear<number, number> | ScaleBand<number>,
  color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
  colorShows: 'predictions' | 'interactions',
  rectWidth: number,
  rectHeight: number
): void {
  ctx.save();

  ctx.clearRect(0, 0, width, height);

  for (let i = 0; i < data.x_values.length; i++) {
    const x1 = data.x_values[i];
    const y1 = data.y_values[i];
    const pred = data.mean_predictions[i];
    const interaction = data.interactions[i];

    ctx.fillStyle = color(colorShows === 'interactions' ? interaction : pred);

    const rectX = 'bandwidth' in x ? (x(x1) ?? 0) + 1 : x(x1) - rectWidth / 2;
    const rectY = 'bandwidth' in y ? (y(y1) ?? 0) + 1 : y(y1) - rectHeight / 2;

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
  ctx.save();

  ctx.clearRect(0, 0, width, height);

  ctx.globalAlpha = alpha;

  if ('bandwidth' in x && 'bandwidth' in y) {
    // categorical scatterplot

    const inX = scaleLinear().domain([0, 1]).range([0, x.bandwidth()]);
    const inY = scaleLinear().domain([0, 1]).range([0, y.bandwidth()]);

    for (let i = 0; i < xValues.length; i++) {
      const rx = inX(randomPoints[i].x);
      const ry = inY(randomPoints[i].y);

      ctx.strokeStyle = color(colorValues[i]);
      ctx.beginPath();
      ctx.arc(
        (x(xValues[i]) ?? 0) + rx,
        (y(yValues[i]) ?? 0) + ry,
        radius,
        0,
        2 * Math.PI
      );
      ctx.stroke();
    }
  } else if ('bandwidth' in x && !('bandwidth' in y)) {
    // vertical strip plots
    for (let i = 0; i < xValues.length; i++) {
      ctx.strokeStyle = color(colorValues[i]);
      ctx.beginPath();
      ctx.moveTo(x(xValues[i]) ?? 0, y(yValues[i]));
      ctx.lineTo((x(xValues[i]) ?? 0) + x.bandwidth(), y(yValues[i]));
      ctx.stroke();
    }
  } else if (!('bandwidth' in x) && 'bandwidth' in y) {
    // horizontal strip plots
    for (let i = 0; i < xValues.length; i++) {
      ctx.strokeStyle = color(colorValues[i]);
      ctx.beginPath();
      ctx.moveTo(x(xValues[i]), y(yValues[i]) ?? 0);
      ctx.lineTo(x(xValues[i]), (y(yValues[i]) ?? 0) + y.bandwidth());
      ctx.stroke();
    }
  } else if (!('bandwidth' in x || 'bandwidth' in y)) {
    // scatterplot
    for (let i = 0; i < xValues.length; i++) {
      ctx.strokeStyle = color(colorValues[i]);
      ctx.beginPath();
      ctx.arc(x(xValues[i]), y(yValues[i]), radius, 0, 2 * Math.PI);
      ctx.stroke();
    }
  }

  ctx.restore();
}
