import React, { useEffect, useState } from 'react';
import { useForm } from "react-hook-form";
import './App.scss';
import 'semantic-ui-css/semantic.min.css';
import { ImageItem, ImageItemEditor, TextItemEditor, TextItem, LabelItemEditor } from './Items';
import { ItemProps, LabelItemData } from './Items/common';
import { Button, Card, Container, Dropdown, Form, Header, Message, Popup, Segment, Select } from 'semantic-ui-react';
import { valueOptions } from './util';

const itemDefaults = { marginTop: 0,  marginBottom: 0,  marginLeft: 0,  marginRight: 0 };
const default_items: LabelItemData[] = [
  { key: 't1', type: 'text', text: 'Hello?', font: '40px otsutome_font', ...itemDefaults },
  { key: 't2', type: 'text', text: 'Text with space', font: '40px otsutome_font', ...itemDefaults },
  { key: 'i1', type: 'image', image: '/shoutrrr.png', ...itemDefaults },
  { key: 't3', type: 'text', text: 'Wow!!', font: '40px otsutome_font' , ...itemDefaults},
]

function App() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<SerialOptions>();
  const [currentPort, setCurrentPort] = useState<SerialPort | undefined>();
  const [error, setError] = useState<{title: string, message?: string} | undefined>();

  const [items, setItems] = useState<LabelItemData[]>(default_items);

  const onSerialConnect = (e: Event) => {
    console.log(`Connected!`, e.target)
  }

  const onSerialDisconnect = (e: Event) => {
    console.log(`Disconnected!`, e.target)
  }

  useEffect(() => {
    if(!currentPort) return;
    currentPort.addEventListener('connect', onSerialConnect);
    currentPort.addEventListener('disconnect', onSerialDisconnect);
    return () => {
      currentPort.removeEventListener('connect', onSerialConnect);
      currentPort.removeEventListener('disconnect', onSerialDisconnect);
    }
  }, [currentPort])
  
  const updatePorts = async () => {

    
    // const rawPorts = await navigator.serial.getPorts();
    // console.log(`Got ${rawPorts.length} ports:`, rawPorts)
    // const newPorts = rawPorts.map(raw => {
    //   const info = raw.getInfo();
    //   return {
    //     ...info,
    //     key: `${info.vendorId}/${info.productId}`,
    //     raw,
    //   }
    // });
    // setPorts(newPorts);

    // button.addEventListener('click', () => {
    //   const usbVendorId = ...;
    //   navigator.serial.requestPort({ filters: [{ usbVendorId }]}).then((port) => {
    //     // Connect to `port` or add it to the list of available ports.
    //   }).catch((e) => {
    //     // The user didn't select a port.
    //   });
    // });
  }

  const doConnect = async (options: SerialOptions) => {
    try {
      const port = await navigator.serial.requestPort(); 
      console.log('Port:', {...port});
      console.log('Info:', port.getInfo());
      setCurrentPort(port);
      await port.open({baudRate: options.baudRate});
      console.log('Port connected(?)!');
      console.log('Info:', port.getInfo());
    } catch (e) {
      console.error(e);
      setError({title: `Error connecting web serial`, message: (e as any)?.message });
    }
    //console.log('Info:', port.getInfo());
  }

  const [selectedItem, setSelectedItem] = useState<LabelItemData | null>(null);

  const updateItem = (newItem: LabelItemData | ItemProps) => setItems(current => current.map(i => i.key === newItem.key ? newItem : i) as LabelItemData[]);

  return (
    <div className="App">
      <Container>
        <Card fluid>
          <Card.Header style={{padding: '10px'}}>
      <Button floated='right' color='violet' size='tiny' onClick={() => updatePorts()}>Update Ports</Button>
          <Header floated='left'>Printer communication</Header>

          </Card.Header>
          <Card.Content>

      <Form onSubmit={handleSubmit(doConnect)}>
      <Form.Group widths='equal'>
        <Form.Field>
        <label>Baud Rate:</label>
          <Dropdown selection options={valueOptions('75','110','300','1200','2400','4800','9600','19200','38400','57600','115200')} defaultValue="9600" {...register("baudRate")}>
            {/* <option value="">(default)</option>
            {['75','110','300','1200','2400','4800','9600','19200','38400','57600','115200'].map(v => <option key={v}>{v}</option>)} */}
          </Dropdown>
        </Form.Field>
        <Form.Field>
        <label>
          Data Bits:
          </label>
          <Dropdown selection options={valueOptions('5','6','7','8','9')} defaultValue="8" {...register("dataBits")} />
          </Form.Field>
        <Form.Field>
        <label>
          Flow control:
        </label>
          <Dropdown selection options={valueOptions('none', 'hardware')} defaultValue="none" {...register("flowControl")} />
          </Form.Field>
        <Form.Field>
        <label>
          Parity:
        </label>
          <Dropdown clearable selection options={valueOptions('none','odd','even','mark','space')} defaultValue="" {...register("parity")} />
          </Form.Field>
        <Form.Field>
        <label>
          Stop Bits:
        </label>
          <Dropdown clearable selection options={valueOptions('1', '1.5', '2')} defaultValue="" {...register("stopBits")} />
        </Form.Field>
        </Form.Group>

      <Button type="submit" content="Connect" />

      </Form>
            </Card.Content>
      </Card>
      <Segment>
        <Header>Label editor</Header>
      {error && (<dialog><header>{error.title}</header><div>{error.message  ?? 'Unknown error'}</div></dialog>)}

      <div style={{display: 'flex', flexDirection: 'row', alignItems: 'flex-start'}}>

        {items.map(item =>
        <Popup key={item.key} on='click' position="bottom center" onOpen={() => setSelectedItem(item)} onClose={() => setSelectedItem(null)} trigger={
          <div className={`label-item${selectedItem?.key === item.key?' selected':''}`}>{/* onClick={() => setSelectedItem(item)} */}
          {
            item.type === 'text' ? <TextItem {...item} /> :
            item.type === 'image' ? <ImageItem {...item} /> :
            <div>Invalid item</div>
          } 
          </div>
        }>
          <LabelItemEditor item={item} setItem={updateItem} />
          {item.type === 'text' && <TextItemEditor item={item} setItem={updateItem} />}
          {item.type === 'image' && <ImageItemEditor item={item} setItem={updateItem} />}
        </Popup>

        )}

      {/* <LabelPreview />
      <ImagePreview /> */}
      </div>
      </Segment>
      {/* <Segment attached='top'>
        {selectedItem ? (
          <>
                      {selectedItem.type === 'text' && <TextItemEditor item={selectedItem} />}
                      {selectedItem.type === 'image' && <ImageItemEditor item={selectedItem} />}
          </>
        ):(
          <Message content='Select an item to edit' />
        )}
      </Segment> */}
      </Container> 
    </div>
  );
}

// {ports.map(port => (
//   <li key={port.key}><details><summary>{port.key}</summary><pre>{JSON.stringify(port, null, 2)}</pre></details></li>
// ))}

export default App;
