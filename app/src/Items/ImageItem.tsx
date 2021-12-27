import { useEffect, useRef, useState } from "react";
import { Button, Form } from "semantic-ui-react";
import { StateSetter } from "../types";
import { ItemProps, USABLE_HEIGHT, applyThreshold, getImageDim, ItemEditorProps } from "./common";


export interface ImageItemProps extends ItemProps {
    type: 'image';
    image: string;
}



export const ImageItemEditor: React.FC<ItemEditorProps<ImageItemProps>> = (props) => {

    return (
        <>
            <Form>
                <Form.Field>
                    <label>Image:</label>
                    <Button content="Browse..." />
                </Form.Field>
            </Form>
        </>
    )
}

export const ImageItem: React.FC<ImageItemProps> = (props) => {
    const {threshold, inverted, image} = props;
    const [width, setWidth] = useState(200);
    const [imageLoaded, setImageLoaded] = useState(false);

    const imgRef = useRef<HTMLImageElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    useEffect(() => {
        const ctx = canvasRef.current?.getContext('2d');
        if(!ctx) return;
        if (!imgRef.current) return;
        if (!imageLoaded) return;

        const imgWidth = imgRef.current.width;
        const imgHeight = imgRef.current.height;

        ctx.imageSmoothingEnabled = false;
        // ctx.globalCompositeOperation


        ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height);

        const scaledWidth = imgWidth * (USABLE_HEIGHT / imgHeight);

        if (scaledWidth !== width) {
            ctx.canvas.width = scaledWidth;
            ctx.canvas.height = USABLE_HEIGHT;
            ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height);

            setWidth(scaledWidth);
            return;
        }

        ctx.drawImage(imgRef.current, 0, 0, scaledWidth,USABLE_HEIGHT);

        if (width <= 0) return;

        applyThreshold(ctx, threshold, inverted)

    }, [canvasRef, width, image, threshold, inverted, imageLoaded]);

    useEffect(()=> {
        setImageLoaded(false);
    }, [image]);

    return (
        <>
            <img ref={imgRef} src={image} style={{display: 'none'}} alt="" onLoad={()=>setImageLoaded(true)} />
            <canvas ref={canvasRef} style={{imageRendering: 'pixelated', height: '140px'}} />
        </>
    )
}