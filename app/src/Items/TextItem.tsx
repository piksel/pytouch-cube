import { useEffect, useMemo, useRef, useState } from "react";
import { Dropdown, Form, Input } from "semantic-ui-react";
import { Link } from "wouter";
import { valueOptions } from "../util";
import { ItemProps, applyThreshold, ItemEditorProps, ItemData } from "./common";


export interface TextItemData extends ItemData {
    type: 'text';
    text: string;
    font: string;
}
export interface TextItemProps extends ItemProps {
    data: TextItemData;
}

const defaultFonts = [
    // 'otsutome_font'
    'serif',
    'sans-serif',
    'monospace'
];

const guiFonts = [
    'Rating',
    'Step',
    'outline-icons',
    'Icons',
    'Checkbox',
    'Dropdown',
    'brand-icons',
    'Accordion'
];

export const TextItem: React.FC<TextItemProps> = (props) => {
    const {text, font, threshold, inverted} = props.data;
    const {showDebugLines} = props;
    const [width, setWidth] = useState(200);
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const ctx = canvasRef.current?.getContext('2d');
        if(!ctx) return;

        ctx.imageSmoothingEnabled = false;
        // ctx.globalCompositeOperation

        try {
            if (!document.fonts.check(font)) return;
        }
        catch {
            return;
        }

        // ctx.fillStyle = inverted ? 'white' : 'black';
        ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height);

        ctx.font = font;
        
        const textRect = ctx.measureText(text);
        const minWidth = Math.ceil(textRect.width);
        if (ctx.canvas.width !== minWidth) {
            //setTimeout(() => {

                console.log(textRect.width, '!=', width, ctx.canvas.width, minWidth, `(${text}) FONT: ${font}`);
                
                ctx.canvas.width = minWidth;
                // ctx.canvas.height = USABLE_HEIGHT;
                ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height);
                
                setWidth(minWidth);
                return;
           // }, 1000);
        }

        const textHeight = textRect.fontBoundingBoxAscent + textRect.fontBoundingBoxDescent + textRect.fontBoundingBoxDescent;
        const verticalOffset = (ctx.canvas.height - textHeight) / 2;
        
        
        ctx.fillText(text, 0, verticalOffset + textRect.actualBoundingBoxAscent + textRect.fontBoundingBoxDescent, width);

        if (width <= 0) return;

        applyThreshold(ctx, props.color, threshold, false, props.data.mask);

        
        if(showDebugLines) {
            ctx.moveTo(0, verticalOffset);
            ctx.lineTo(width, verticalOffset);
            ctx.moveTo(0, verticalOffset + textRect.fontBoundingBoxDescent);
            ctx.lineTo(width, verticalOffset + textRect.fontBoundingBoxDescent);

            ctx.moveTo(0, verticalOffset + textRect.fontBoundingBoxAscent + textRect.fontBoundingBoxDescent);
            ctx.lineTo(width, verticalOffset + textRect.fontBoundingBoxAscent + textRect.fontBoundingBoxDescent);

            ctx.moveTo(0, verticalOffset + textHeight);
            ctx.lineTo(width, verticalOffset + textHeight);
            ctx.strokeStyle = "#ff000030";
            ctx.stroke();
        }

    }, [canvasRef, width, text, font, threshold, inverted, props.color, props.data.mask, showDebugLines]);


    return (
        <canvas ref={canvasRef} style={{imageRendering: 'pixelated', height: '140px'}} />
    )
}

export const TextItemEditor: React.FC<ItemEditorProps<TextItemData>> = (props) => {

    const {data, setData} = props;
    const [fontName, setFontName] = useState<string>();
    const [fontSize, setFontSize] = useState<number>();

    useEffect(() => {
        // console.log('Font changed: ', data.font);

        const [size, name] = data.font.split(' ');
        if(!fontName) setFontName(name);

        const match = /([0-9]+)(.*)/.exec(size);
        if (match && !fontSize) {
            const parsedSize = parseInt(match[1]);
            setFontSize(parsedSize);
        }

    }, [data.font, fontName, fontSize]);

    useEffect(() => {
        if(!fontName || !fontSize) return;
        const fontString = `${fontSize}px ${fontName}`;
        if(data.font === fontString) return;

        setData({...data, font: fontString});
    }, [fontName, fontSize, data, setData])
    

    // const bumpFontSize = (amt: number) => {

    //     if(match && match.length === 3) {
    //         parts[0] = `${parseInt(match[1]) + amt}${match[2]}`;
    //         setFont(parts.join(' '));
    //     }
    // }

    const handleFontKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
        if(typeof fontSize !== 'number') return;
        if(e.key === 'ArrowUp') {
            setFontSize(s => bumpFontSize(s, 1));
        } else if (e.key === 'ArrowDown') {
            setFontSize(s => bumpFontSize(s, -1));
        };
    }

    const handleFontWheel: React.WheelEventHandler<HTMLInputElement> = (e) => {
        setFontSize(s => bumpFontSize(s, e.deltaY < 0 ? 1 : -1));
    }

    const handleFontSizeChanged: React.ChangeEventHandler<HTMLInputElement> = (e) => {
        if (fontSize == e.target.valueAsNumber) return;
        setFontSize(e.target.valueAsNumber);
    }

    const fontOptions = useMemo(() => {
        const documentFonts = new Set(Array.from(document.fonts.entries()).map(([a, b]) => a.family).filter(f => !guiFonts.includes(f)));
        const fonts = [...defaultFonts, ...documentFonts].sort((a, b) => ((al, bl) =>  al < bl ? -1 : al > bl ? 1 : 0)(a.toLowerCase(), b.toLowerCase()));
        return valueOptions(...fonts)
    }, []);

    return (
        <>

            <Form style={{minWidth: '400px'}}>

            <Form.Field>
                    <label>Text</label>
                    <Input type="text" value={data.text} onChange={e => setData({...data, text: e.target.value})} />
                </Form.Field>

                <Form.Group widths='equal'>
                    <Form.Field>
                        <label>Font</label>
                        <Dropdown selection search value={fontName} options={fontOptions} onChange={(_, d) => setFontName(d.value?.toString()) }  />
                    </Form.Field>
                    <Form.Field width='7'>
                        <label>Size</label>
                        <Input type='number' value={fontSize} onChange={handleFontSizeChanged} onKeyDownCapture={handleFontKeyDown} onWheel={handleFontWheel} labelPosition="right" label='px' />
                    </Form.Field>

                </Form.Group>
                    <Link href={`${process.env.PUBLIC_URL}/fonts`}>Add additional fonts...</Link>


            </Form>
        </>
    )
}

const bumpFontSize = (s: number | undefined, amount: number): number | undefined => 
    typeof s !== 'number' ? s : Math.max(s + amount, 1);

