import type { QuantitativeDoublePDPData, MixedDoublePDPData, CategoricalDoublePDPData } from "./types";
import type { ScaleLinear, ScaleSequential, ScaleBand } from "d3";

export {
  drawQuantitativeHeatmap,
  drawMixedHeatmap,
  drawCategoricalHeatmap
};

function drawQuantitativeHeatmap(
  data: QuantitativeDoublePDPData,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleLinear<number, number>,
  y: ScaleLinear<number, number>,
  color: ScaleSequential<string, string>
) {
  ctx.save();

  ctx.clearRect(0, 0, width, height);

  const maxX = x.domain()[1];
  const maxY = y.domain()[1];

  const x_axis_values = [...data.x_axis, maxX];
  const y_axis_values = [...data.y_axis, maxY];

  for (let i = 0; i < data.values.length; i++) {
    const cell = data.values[i];

    const x1 = cell.x;
    const y1 = cell.y;
    const x2 = x_axis_values[cell.col + 1];
    const y2 = y_axis_values[cell.row + 1];

    ctx.fillStyle = color(cell.avg_pred);

    ctx.fillRect(
      x(x1),
      y(y1),
      x(x2) - x(x1),
      y(y2) - y(y1),
    );
  }

  ctx.restore();
}

function drawMixedHeatmap(
  data: MixedDoublePDPData,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleLinear<number, number>,
  y: ScaleBand<string|number>,
  color: ScaleSequential<string, string>
) {
  ctx.save();

  ctx.clearRect(0, 0, width, height);

  const maxX = x.domain()[1];

  const x_axis_values = [...data.x_axis, maxX];

  for (let i = 0; i < data.values.length; i++) {
    const cell = data.values[i];

    const x1 = cell.x;
    const x2 = x_axis_values[cell.col + 1];

    ctx.fillStyle = color(cell.avg_pred);

    ctx.fillRect(
      x(cell.x),
      y(cell.y)! + 1,
      x(x2) - x(x1),
      y.bandwidth() - 2
    );
  }

  ctx.restore();
}

function drawCategoricalHeatmap(
  data: CategoricalDoublePDPData,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  x: ScaleBand<string|number>,
  y: ScaleBand<string|number>,
  color: ScaleSequential<string, string>
) {
  ctx.save();

  ctx.clearRect(0, 0, width, height);

  for (let cell of data.values) {
    ctx.fillStyle = color(cell.avg_pred);

    ctx.fillRect(
      x(cell.x)! + 1,
      y(cell.y)! + 1,
      x.bandwidth() - 2,
      y.bandwidth() - 2,
    );
  }

  ctx.restore();
}
