import { useEffect, useRef, useState } from "react";
import { Button, Form } from "semantic-ui-react";
import { ItemProps, USABLE_HEIGHT, applyThreshold, ItemEditorProps, ItemData } from "./common";

export interface ImageItemData extends ItemData {
    type: 'image';
    image: string;
}

export interface ImageItemProps extends ItemProps {
    data: ImageItemData;
}



export const ImageItemEditor: React.FC<ItemEditorProps<ImageItemData>> = (props) => {

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
    const {data} = props;
    const {threshold, inverted, image} = props.data;
    const [width, setWidth] = useState(200);
    const [imageLoaded, setImageLoaded] = useState(false);
    const [imageError, setImageError] = useState(false);

    const imgRef = useRef<HTMLImageElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    useEffect(() => {
        const ctx = canvasRef.current?.getContext('2d');
        if(!ctx) return;
        if (!imgRef.current) return;
        if (!imageLoaded) return;

        if (imageError) {
            ctx.canvas.width = 100;
            setWidth(100);
            ctx.font = '40px sans-serif';
            ctx.fillText('😢', 20, 50);
            console.log('No image :(')
            return;
        }

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

        applyThreshold(ctx, props.color, threshold, inverted, data.mask)

    }, [canvasRef, width, image, threshold, inverted, imageLoaded, props.color, data.mask, imageError]);

    useEffect(()=> {
        setImageLoaded(false);
    }, [image]);

    const handleImageError = () => {
        setImageLoaded(true);
        setImageError(true);
    }

    useEffect(() => {
        const img = imgRef.current;
        if(!img) return;
        img.addEventListener('error', handleImageError);
        return () => img.removeEventListener('error', handleImageError);
    }, [imgRef])

    return (
        <>
            <img ref={imgRef} src={image} crossOrigin="anonymous" style={{display: 'none'}} alt="" onLoad={()=>setImageLoaded(true)} />
            <canvas ref={canvasRef} style={{imageRendering: 'pixelated', height: '140px'}} />
        </>
    )
}