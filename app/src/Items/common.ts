import { TextItemProps } from "./TextItem";
import { ImageItemProps } from "./ImageItem";
import { StateSetter } from "../types";

export const BUFFER_HEIGHT = 128;
export const PRINT_MARGIN = 30;
export const USABLE_HEIGHT = BUFFER_HEIGHT - (PRINT_MARGIN * 2);

export const color_fg = [0, 0, 0, 255];
export const color_bg = [255, 255, 255, 255];


export type LabelItemData = TextItemProps | ImageItemProps;




export const applyThreshold = (ctx: CanvasRenderingContext2D, threshold?: number, inverted?: boolean) => {
    if(typeof threshold === 'undefined') threshold = 128;

    const pixels = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
    for(let i = 0; i < pixels.data.length; i += 4) {
        const alpha_above_thresh = pixels.data[i+3] > threshold;
        const value = (pixels.data[i]+pixels.data[i+1]+pixels.data[i+2]) / 3;
        const bright_above_thresh = value > threshold;
        
        const color = alpha_above_thresh && (bright_above_thresh !== !inverted) ? color_fg : color_bg;
        pixels.data[i + 0] = color[0];
        pixels.data[i + 1] = color[1];
        pixels.data[i + 2] = color[2];
        pixels.data[i + 3] = color[3];
    }
    ctx.putImageData(pixels, 0, 0);
}


export const getImageDim = (dim: number | SVGAnimatedLength) => typeof dim === 'number' ? dim : dim.baseVal.value;

export interface ItemProps {
    key: string;
    threshold?: number;
    inverted?: boolean;
    rotated?: boolean;
    flippedHorizontal?: boolean;
    flippedVertical?: boolean;
    marginTop: number;
    marginBottom: number;
    marginLeft: number;
    marginRight: number;
}

export type ItemEditorProps<T> = { item: T, setItem: (item: T) => void }