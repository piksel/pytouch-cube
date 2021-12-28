import React from "react";
import { Checkbox, Form, Input } from "semantic-ui-react";
import { ItemData, ItemEditorProps } from "./common";

// type GenericItemProps = ItemProps & {type: any, image?: any, text?: any};

export const LabelItemEditor: React.FC<ItemEditorProps<ItemData>> = (props) => {
    const {data, setData} = props;


    return (
        <Form>
            <Form.Group widths='equal'>
            <Form.Field>
                <Checkbox toggle checked={data.inverted} label="Inverted" disabled={(data as any).type === 'text'} onChange={(_, d) => setData(({...data, inverted: !!d.checked}))} />
            </Form.Field>
            <Form.Field>
                <Checkbox toggle checked={data.mask} label="Mask" onChange={(_, d) => setData(({...data, mask: !!d.checked}))} />
            </Form.Field>
            </Form.Group>
            <Form.Field>

                <Checkbox toggle checked={data.rotated} disabled label="Rotated" />
            </Form.Field>
            <Form.Field>

                <label>Flipped:</label>
        

                <Form.Group widths='equal'>
            <Form.Field>

                <Checkbox toggle checked={data.flippedHorizontal} disabled label="Horizontal" />
                </Form.Field>
                <Form.Field>
                <Checkbox toggle checked={data.flippedVertical} disabled label="Vertical" />
                
            </Form.Field>

                </Form.Group>
            </Form.Field>

            <Form.Field>
                <label>Threshold</label>
                <Input type="range" min="0" max="254" value={data.threshold ?? 128} onChange={(_, d) => setData(({...data, threshold: parseInt(d.value, 10)}))} />
            </Form.Field>

        </Form>
    )
} 
