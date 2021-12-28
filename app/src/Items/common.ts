import { TextItemData } from "./TextItem";
import { ImageItemData } from "./ImageItem";

export const BUFFER_HEIGHT = 128;
export const PRINT_MARGIN = 30;
export const USABLE_HEIGHT = BUFFER_HEIGHT - (PRINT_MARGIN * 2);

export const color_fg = [0, 0, 0, 255];
export const color_bg = [255, 255, 255, 0];


export type LabelItemData = TextItemData | ImageItemData;




export const applyThreshold = (ctx: CanvasRenderingContext2D, color: [number, number, number], threshold?: number, inverted?: boolean, mask?: boolean) => {
    if(typeof threshold === 'undefined') threshold = 128;

    const pixels = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
    for(let i = 0; i < pixels.data.length; i += 4) {
        const alpha_above_thresh = pixels.data[i+3] > threshold;
        const value = (pixels.data[i]+pixels.data[i+1]+pixels.data[i+2]) / 3;
        const bright_below_thresh = value < threshold;

        // First pass looks at pixel values and checks if they are beneath/above the threshold (depending on invertd)
        const above_thresh = alpha_above_thresh && bright_below_thresh !== (!!inverted);

        // Second pass inverts the threshold if masking
        const alpha = (!!mask) !== above_thresh ? 255 : 0;

        // const color = color_fg;

        pixels.data[i + 0] = color[0];
        pixels.data[i + 1] = color[1];
        pixels.data[i + 2] = color[2];
        pixels.data[i + 3] =  alpha; 
    }
    ctx.putImageData(pixels, 0, 0);
}


export const getImageDim = (dim: number | SVGAnimatedLength) => typeof dim === 'number' ? dim : dim.baseVal.value;

export interface ItemProps {
    color: [number, number, number];
}

export interface ItemData {
    key: string;
    threshold?: number;
    inverted?: boolean;
    mask?: boolean;
    rotated?: boolean;
    flippedHorizontal?: boolean;
    flippedVertical?: boolean;
    marginTop: number;
    marginBottom: number;
    marginLeft: number;
    marginRight: number;
}

export type ItemEditorProps<T> = { data: T, setData: (item: T) => void }