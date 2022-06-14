import type { QuantitativeDoublePDPData } from "./types";
import type { ScaleLinear, ScaleSequential } from "d3";

export {
  scaleCanvas,
  drawQuantitativeHeatmap,
};

// Adapted from https://www.html5rocks.com/en/tutorials/canvas/hidpi/
function scaleCanvas(canvas: HTMLCanvasElement, context: CanvasRenderingContext2D, width: number, height: number) {
  // assume the device pixel ratio is 1 if the browser doesn't specify it
  const devicePixelRatio = window.devicePixelRatio || 1;

  // set the 'real' canvas size to the higher width/height
  canvas.width = width * devicePixelRatio;
  canvas.height = height * devicePixelRatio;

  // ...then scale it back down with CSS
  canvas.style.width = width + 'px';
  canvas.style.height = height + 'px';

  // scale the drawing context so everything will work at the higher ratio
  context.scale(devicePixelRatio, devicePixelRatio);
}

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
