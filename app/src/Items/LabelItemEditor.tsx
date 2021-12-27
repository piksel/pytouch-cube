import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { Checkbox, Form, Input, Label } from "semantic-ui-react";
import { ItemEditorProps, ItemProps } from "./common";

type GenericItemProps = ItemProps & {type: any, image?: any, text?: any};

export const LabelItemEditor: React.FC<ItemEditorProps<GenericItemProps>> = (props) => {
    const {item, setItem} = props;


    return (
        <Form>
            <Form.Field>
                <Checkbox toggle checked={item.inverted} label="Inverted" onChange={(_, d) => setItem(({...item, inverted: !!d.checked}))} />
            </Form.Field>
            <Form.Field>

                <Checkbox toggle checked={item.rotated} label="Rotated" />
            </Form.Field>
            <Form.Field>

                <label>Flipped:</label>
        

                <Form.Group widths='equal'>
            <Form.Field>

                <Checkbox toggle checked={item.flippedHorizontal} label="Horizontal" />
                <Form.Field>
                </Form.Field>
                <Checkbox toggle checked={item.flippedVertical} label="Vertical" />
            </Form.Field>

                </Form.Group>
            </Form.Field>

            <Form.Field>
                <label>Threshold</label>
                <Input type="range" min="0" max="254" value={item.threshold ?? 128} onChange={(_, d) => setItem(({...item, threshold: parseInt(d.value, 10)}))} />
            </Form.Field>

        </Form>
    )
} 
