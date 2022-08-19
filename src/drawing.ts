import type {
  QuantitativeDoublePDPData,
  MixedDoublePDPData,
  CategoricalDoublePDPData,
} from './types';

import type {
  ScaleLinear,
  ScaleSequential,
  ScaleBand,
  ScaleDiverging,
} from 'd3';
import { pairs } from 'd3-array';

export { drawQuantitativeHeatmap, drawMixedHeatmap, drawCategoricalHeatmap };

function drawQuantitativeHeatmap(
  data: QuantitativeDoublePDPData,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleLinear<number, number>,
  y: ScaleLinear<number, number>,
  color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
  showInteractions: boolean
): void {
  ctx.save();

  ctx.clearRect(0, 0, width, height);

  const nextX = new Map(pairs(data.x_axis));
  const nextY = new Map(pairs(data.y_axis));

  for (let i = 0; i < data.x_values.length; i++) {
    const x1 = data.x_values[i];
    const y1 = data.y_values[i];
    const pred = data.mean_predictions[i];
    const interaction = data.interactions[i];

    const x2 = nextX.get(x1) ?? x1;
    const y2 = nextY.get(y1) ?? y1;

    ctx.fillStyle = color(showInteractions ? interaction : pred);

    ctx.fillRect(x(x1), y(y1), x(x2) - x(x1), y(y2) - y(y1));
  }

  ctx.restore();
}

function drawMixedHeatmap(
  data: MixedDoublePDPData,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleLinear<number, number>,
  y: ScaleBand<string | number>,
  color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
  showInteractions: boolean
): void {
  ctx.save();

  ctx.clearRect(0, 0, width, height);

  const nextX = new Map(pairs(data.x_axis));

  for (let i = 0; i < data.x_values.length; i++) {
    const x1 = data.x_values[i];
    const y1 = data.y_values[i];
    const pred = data.mean_predictions[i];
    const interaction = data.interactions[i];

    const x2 = nextX.get(x1) ?? x1;

    ctx.fillStyle = color(showInteractions ? interaction : pred);

    ctx.fillRect(x(x1), y(y1)! + 1, x(x2) - x(x1), y.bandwidth() - 2);
  }

  ctx.restore();
}

function drawCategoricalHeatmap(
  data: CategoricalDoublePDPData,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleBand<string | number>,
  y: ScaleBand<string | number>,
  color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
  showInteractions: boolean
): void {
  ctx.save();

  ctx.clearRect(0, 0, width, height);

  for (let i = 0; i < data.x_values.length; i++) {
    const x_val = data.x_values[i];
    const y_val = data.y_values[i];
    const pred = data.mean_predictions[i];
    const interaction = data.interactions[i];

    ctx.fillStyle = color(showInteractions ? interaction : pred);

    ctx.fillRect(
      x(x_val)! + 1,
      y(y_val)! + 1,
      x.bandwidth() - 2,
      y.bandwidth() - 2
    );
  }

  ctx.restore();
}
