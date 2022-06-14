import type { QuantitativeDoublePDPData } from "./types";
import type { ScaleLinear, ScaleSequential } from "d3";
export { scaleCanvas, drawQuantitativeHeatmap, };
declare function scaleCanvas(canvas: HTMLCanvasElement, context: CanvasRenderingContext2D, width: number, height: number): void;
declare function drawQuantitativeHeatmap(data: QuantitativeDoublePDPData, ctx: CanvasRenderingContext2D, width: number, height: number, x: ScaleLinear<number, number>, y: ScaleLinear<number, number>, color: ScaleSequential<string, string>): void;
