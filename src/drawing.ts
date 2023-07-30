import { getRaincloudData } from './vis-utils';
import { max, groups, zip } from 'd3-array';
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

  ctx.clearRect(0, 0, width, height);

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

  ctx.clearRect(0, 0, width, height);

  if ('bandwidth' in x && 'bandwidth' in y) {
    // categorical scatterplot

    ctx.globalAlpha = alpha;

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
    if (x.bandwidth() >= minRainCloudSize) {
      // vertical raincloud plots
      const grouped = groups(zip(xValues, yValues, colorValues), (g) => g[0]);
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
      for (let i = 0; i < xValues.length; i++) {
        ctx.strokeStyle = color(colorValues[i]);
        ctx.beginPath();
        ctx.moveTo(x(xValues[i]) ?? 0, y(yValues[i]));
        ctx.lineTo((x(xValues[i]) ?? 0) + x.bandwidth(), y(yValues[i]));
        ctx.stroke();
      }
    }
  } else if (!('bandwidth' in x) && 'bandwidth' in y) {
    if (y.bandwidth() >= minRainCloudSize) {
      // horizontal raincloud plots
      const grouped = groups(zip(xValues, yValues, colorValues), (g) => g[1]);
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
      for (let i = 0; i < xValues.length; i++) {
        ctx.strokeStyle = color(colorValues[i]);
        ctx.beginPath();
        ctx.moveTo(x(xValues[i]), y(yValues[i]) ?? 0);
        ctx.lineTo(x(xValues[i]), (y(yValues[i]) ?? 0) + y.bandwidth());
        ctx.stroke();
      }
    }
  } else if (!('bandwidth' in x || 'bandwidth' in y)) {
    // scatterplot

    ctx.globalAlpha = alpha;

    for (let i = 0; i < xValues.length; i++) {
      ctx.strokeStyle = color(colorValues[i]);
      ctx.beginPath();
      ctx.arc(x(xValues[i]), y(yValues[i]), radius, 0, 2 * Math.PI);
      ctx.stroke();
    }
  }

  ctx.restore();
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

  ctx.clearRect(0, 0, width, height);

  // cloud

  ctx.fillStyle = cloudColor;
  ctx.beginPath();
  cloudArea(data.densities);
  ctx.fill();

  // rain

  ctx.globalAlpha = alpha;

  data.values.forEach(({ value, label }) => {
    ctx.beginPath();
    ctx.strokeStyle =
      typeof rainColor === 'function' ? rainColor(label) : rainColor;
    ctx.moveTo(x(value), height / 2 + padding);
    ctx.lineTo(x(value), height);
    ctx.stroke();
  });

  // lightning

  ctx.globalAlpha = 1;
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

  ctx.clearRect(0, 0, width, height);

  // cloud

  ctx.fillStyle = cloudColor;
  ctx.beginPath();
  cloudArea(data.densities);
  ctx.fill();

  // rain

  ctx.globalAlpha = alpha;

  data.values.forEach(({ value, label }) => {
    ctx.beginPath();
    ctx.strokeStyle =
      typeof rainColor === 'function' ? rainColor(label) : rainColor;
    ctx.moveTo(width / 2 + padding, y(value));
    ctx.lineTo(width, y(value));
    ctx.stroke();
  });

  // lightning

  ctx.globalAlpha = 1;
  ctx.fillStyle = lightningColor;
  ctx.strokeStyle = 'white';
  ctx.beginPath();
  ctx.arc(width / 2, y(data.mean), 5, 0, 2 * Math.PI);
  ctx.fill();
  ctx.stroke();

  ctx.restore();
}
