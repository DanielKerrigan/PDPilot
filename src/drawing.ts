import type { TwoWayPD } from './types';

import type {
  ScaleLinear,
  ScaleSequential,
  ScaleBand,
  ScaleDiverging,
} from 'd3';

export function drawHeatmap(
  data: TwoWayPD,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleLinear<number, number> | ScaleBand<number>,
  y: ScaleLinear<number, number> | ScaleBand<number>,
  color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
  showInteractions: boolean,
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

    ctx.fillStyle = color(showInteractions ? interaction : pred);

    const rectX = 'bandwidth' in x ? (x(x1) ?? 0) + 1 : x(x1) - rectWidth / 2;
    const rectY = 'bandwidth' in y ? (y(y1) ?? 0) + 1 : y(y1) - rectHeight / 2;

    ctx.fillRect(rectX, rectY, rectWidth, rectHeight);
  }

  ctx.restore();
}

// function drawQuantitativeHeatmap(
//   data: QuantitativeDoublePDPData,
//   ctx: CanvasRenderingContext2D,
//   width: number,
//   height: number,
//   x: ScaleLinear<number, number>,
//   y: ScaleLinear<number, number>,
//   color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
//   showInteractions: boolean,
//   rectWidth: number,
//   rectHeight: number
// ): void {
//   ctx.save();

//   ctx.clearRect(0, 0, width, height);

//   for (let i = 0; i < data.x_values.length; i++) {
//     const x1 = data.x_values[i];
//     const y1 = data.y_values[i];
//     const pred = data.mean_predictions[i];
//     const interaction = data.interactions[i];

//     ctx.fillStyle = color(showInteractions ? interaction : pred);

//     ctx.fillRect(
//       x(x1) - rectWidth / 2,
//       y(y1) - rectHeight / 2,
//       rectWidth,
//       rectHeight
//     );
//   }

//   ctx.restore();
// }

// function drawMixedHeatmap(
//   data: MixedDoublePDPData,
//   ctx: CanvasRenderingContext2D,
//   width: number,
//   height: number,
//   x: ScaleLinear<number, number>,
//   y: ScaleBand<string | number>,
//   color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
//   showInteractions: boolean,
//   rectWidth: number
// ): void {
//   ctx.save();

//   ctx.clearRect(0, 0, width, height);

//   for (let i = 0; i < data.x_values.length; i++) {
//     const x1 = data.x_values[i];
//     const y1 = data.y_values[i];
//     const pred = data.mean_predictions[i];
//     const interaction = data.interactions[i];

//     ctx.fillStyle = color(showInteractions ? interaction : pred);

//     ctx.fillRect(
//       x(x1) - rectWidth / 2,
//       y(y1)! + 1,
//       rectWidth,
//       y.bandwidth() - 2
//     );
//   }

//   ctx.restore();
// }

// function drawCategoricalHeatmap(
//   data: CategoricalDoublePDPData,
//   ctx: CanvasRenderingContext2D,
//   width: number,
//   height: number,
//   x: ScaleBand<string | number>,
//   y: ScaleBand<string | number>,
//   color: ScaleSequential<string, string> | ScaleDiverging<string, string>,
//   showInteractions: boolean
// ): void {
//   ctx.save();

//   ctx.clearRect(0, 0, width, height);

//   for (let i = 0; i < data.x_values.length; i++) {
//     const x_val = data.x_values[i];
//     const y_val = data.y_values[i];
//     const pred = data.mean_predictions[i];
//     const interaction = data.interactions[i];

//     ctx.fillStyle = color(showInteractions ? interaction : pred);

//     ctx.fillRect(
//       x(x_val)! + 1,
//       y(y_val)! + 1,
//       x.bandwidth() - 2,
//       y.bandwidth() - 2
//     );
//   }

//   ctx.restore();
// }
