import { useEffect, useMemo, useRef, useState } from "react";
import { Dropdown, Form, Input, Message } from "semantic-ui-react";
import { valueOptions } from "../util";
import { ItemProps, USABLE_HEIGHT, applyThreshold, ItemEditorProps } from "./common";

export interface TextItemProps extends ItemProps {
    type: 'text';
    text: string;
    font: string;
}


export const TextItem: React.FC<TextItemProps> = (props) => {
    const {text, font, threshold, inverted} = props;
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

        ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height);

        ctx.font = font;
        
        const textRect = ctx.measureText(text);
        if (width !== textRect.width) {
            console.log(textRect.width, '!=', width);
            ctx.canvas.width = textRect.width;
            ctx.canvas.height = USABLE_HEIGHT;
            ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height);

            setWidth(textRect.width);
            return;
        }

        const textHeight = textRect.fontBoundingBoxAscent + textRect.fontBoundingBoxDescent + textRect.fontBoundingBoxDescent;
        const verticalOffset = (ctx.canvas.height - textHeight) / 2;
        
        ctx.fillText(text, 0, verticalOffset + textRect.actualBoundingBoxAscent + textRect.fontBoundingBoxDescent, width);

        if (width <= 0) return;

        applyThreshold(ctx, threshold, inverted);

        

        ctx.moveTo(0, verticalOffset);
        ctx.lineTo(width, verticalOffset);
        ctx.moveTo(0, verticalOffset + textRect.fontBoundingBoxDescent);
        ctx.lineTo(width, verticalOffset + textRect.fontBoundingBoxDescent);

        ctx.moveTo(0, verticalOffset + textRect.fontBoundingBoxAscent + textRect.fontBoundingBoxDescent);
        ctx.lineTo(width, verticalOffset + textRect.fontBoundingBoxAscent + textRect.fontBoundingBoxDescent);

        ctx.moveTo(0, verticalOffset + textHeight);
        ctx.lineTo(width, verticalOffset + textHeight);
        ctx.strokeStyle = "red";
        ctx.stroke();

    }, [canvasRef, width, text, font, threshold, inverted]);


    return (
        <canvas ref={canvasRef} style={{imageRendering: 'pixelated', height: '140px'}} />
    )
}

export const TextItemEditor: React.FC<ItemEditorProps<TextItemProps>> = (props) => {

    const {item, setItem} = props;
    const [text, setText] = useState('Hello!');
    const [fontName, setFontName] = useState('otsutome_font');
    const [fontSize, setFontSize] = useState(40);

    useEffect(() => {

        const [size, name] = item.font.split(' ');
        setFontName(name);

        const match = /([0-9]+)(.*)/.exec(size);
        if (match) {
            const parsedSize = parseInt(match[1]);
            setFontSize(parsedSize);
        }

    }, [item.font]);

    useEffect(() => {
        const fontString = `${fontSize}px ${fontName}`;
        if(item.font === fontString) return;
        setItem({...item, font: fontString});
    }, [fontName, fontSize, item, setItem])
    

    // const bumpFontSize = (amt: number) => {

    //     if(match && match.length === 3) {
    //         parts[0] = `${parseInt(match[1]) + amt}${match[2]}`;
    //         setFont(parts.join(' '));
    //     }
    // }

    const handleFontKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
        if(e.key === 'ArrowUp') {
            setFontSize(s => s + 1);
        } else if (e.key === 'ArrowDown') {
            setFontSize(s => s - 1);
        }
        else console.log(e.key);
    }

    const handleFontWheel: React.WheelEventHandler<HTMLInputElement> = (e) => {
        console.log(e.deltaY, e.deltaMode);
        setFontSize(s => s + (e.deltaY < 0 ? 1 : -1));
    }

    const fontOptions = useMemo(() => {
        const documentFonts = new Set(Array.from(document.fonts.entries()).map(([a, b]) =>a.family));
        const fonts = ['otsutome_font', ...documentFonts].sort((a, b) => ((al, bl) =>  al < bl ? -1 : al > bl ? 1 : 0)(a.toLowerCase(), b.toLowerCase()));
        return valueOptions(...fonts)
    }, []);

    const fontString = useMemo(() => `${fontSize}px ${fontName}`, [fontName, fontSize]);

    return (
        <>

            <Form style={{minWidth: '400px'}}>
                <Form.Group widths='equal'>
                    <Form.Field>
                        <label>Font</label>
                        <Dropdown selection search value={fontName} options={fontOptions}  />
                    </Form.Field>
                    <Form.Field width='6'>
                        <label>Size</label>
                        <Input type='number' value={fontSize} onKeyDownCapture={handleFontKeyDown} onWheel={handleFontWheel} labelPosition="right" label='px' />
                    </Form.Field>

                </Form.Group>

                    <Message content={<code>{fontString}</code>} header="Font string:" />

                <Form.Field>
                    <label>Text</label>
                    <Input type="text" value={text} onChange={e => setText(e.target.value)} />
                </Form.Field>
            </Form>
        </>
    )
}