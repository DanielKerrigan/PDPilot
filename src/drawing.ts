import type { TwoWayPD } from './types';

import type {
  ScaleLinear,
  ScaleSequential,
  ScaleBand,
  ScaleDiverging,
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
