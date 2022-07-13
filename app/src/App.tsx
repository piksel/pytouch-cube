import { FC, useEffect, useMemo, useState, useRef, useCallback } from 'react';
import { useForm } from "react-hook-form";
import './App.scss';
// import 'semantic-ui-css/semantic.min.css';
import { ImageItem, ImageItemEditor, TextItemEditor, TextItem, LabelItemEditor } from './Items';
import { ItemData, LabelItemData } from './Items/common';
import { Button, Card, Checkbox, Container, Dropdown, Form, Header, Input, Loader, Menu, MenuItem, Popup, Radio, Segment } from 'semantic-ui-react';
import { valueOptions } from './util';
import { Link, Route } from 'wouter';
import { FontsPage } from './Pages/FontsPage';
import { WebFont } from './fonts';

const itemDefaults = { marginTop: 0,  marginBottom: 0,  marginLeft: 0,  marginRight: 0 };
const default_items: LabelItemData[] = [
  { key: 't1', type: 'text', text: 'Hello?', font: '40px sans-serif', ...itemDefaults },
  { key: 't2', type: 'text', text: 'Text with space', font: '40px sans-serif', ...itemDefaults },
  { key: 'i1', type: 'image', image: './shoutrrr.png', ...itemDefaults },
  { key: 't3', type: 'text', text: 'Wow!!', font: '40px sans-serif' , ...itemDefaults},
]

function App() {
  
  const [items, setItems] = useState<LabelItemData[]>(default_items);
  const [error, setError] = useState<{title: string, message?: string} | undefined>();
  const [webFonts, setWebFonts] = useState<WebFont[]>([]);

  const [background, setBackground] = useState<string>("#ffffff");
  const [foreground, setForeground] = useState<string>("#000000");
  const [showDebugLines, setShowDebugLines] = useState<boolean>(process.env.NODE_ENV === 'development');

  const labelColor: [number, number, number] = useMemo(() => (c => [(c >> 16) & 0xff, (c >> 8) & 0xff, c & 0xff])(parseInt(foreground.substring(1), 16)), [foreground])

  const [selectedItem, setSelectedItem] = useState<LabelItemData | null>(null);

  const updateItem = (newItem: LabelItemData | ItemData) =>
    setItems(current => current.map(i => i.key === newItem.key ? newItem : i) as LabelItemData[]);
  

  

  return (
    <div className="App">
      <Container>
        <Menu>
          <Link href={`${process.env.PUBLIC_URL}/label`}>
            <MenuItem content='Label'></MenuItem>
          </Link>
          <Link href={`${process.env.PUBLIC_URL}/fonts`}>
            <MenuItem content='Fonts'></MenuItem>
          </Link>
          <Link href={`${process.env.PUBLIC_URL}/printer`}>
            <MenuItem content='Printer'></MenuItem>
          </Link>
        </Menu>

      <Route path={`${process.env.PUBLIC_URL}/printer`}>
        <ConnectionCard />
      </Route>

      <Route path={`${process.env.PUBLIC_URL}/fonts`}>
        <FontsPage webFonts={webFonts} setWebFonts={setWebFonts} />
      </Route>

      <Route path={`${process.env.PUBLIC_URL}/label`}>
        <FontLoader webFonts={webFonts} onError={useCallback((e: Error) => setError({title: 'Error loading font', message: e?.message}), [setError])} />



      <Segment>
        <Header>Label editor


          <div style={{float: 'right'}}>
          <div style={{marginRight: '2ch', display: 'inline-block'}}>
            <Checkbox checked={showDebugLines} onChange={() => setShowDebugLines(v => !v)} label='Show debug lines' />
            </div>
            <label>FG:
          <input style={{marginLeft:'1ch'}}  type='color' value={foreground} onChange={e => setForeground(e.target.value)}></input>
            </label>
            <label style={{marginLeft: '2ch'}}>BG:
          <input style={{marginLeft:'1ch'}} type='color' value={background} onChange={e => setBackground(e.target.value)}></input>
            </label>
          </div>

        </Header>

      {error && (<dialog><header>{error.title}</header><div>{error.message  ?? 'Unknown error'}</div></dialog>)}
      <div style={{overflowY: 'visible',overflowX: 'auto', background: '#e9e9e9', padding: '10px', boxShadow: 'inset 1px 1px 4px #00000020' }}>
      <div style={{display: 'flex', flexDirection: 'row', alignItems: 'flex-start', background: background, width: 'fit-content', boxShadow: '1px 1px 4px #00000020'  }}>

        {items.map(item =>
        <Popup key={item.key} on='click' position='bottom right' onOpen={() => setSelectedItem(item)} onClose={() => setSelectedItem(null)} trigger={
          <div className={`label-item${selectedItem?.key === item.key?' selected':''}`}>{/* onClick={() => setSelectedItem(item)} */}
            <div className='indicator' />
          {
            item.type === 'text' ? <TextItem showDebugLines={showDebugLines} data={item} color={labelColor} /> :
            item.type === 'image' ? <ImageItem showDebugLines={showDebugLines}  data={item}  color={labelColor} /> :
            <div>Invalid item</div>
          }
            <div className='indicator' />
          </div>
        }>
          <LabelItemEditor data={item} setData={updateItem} />
          {item.type === 'text' && <TextItemEditor data={item} setData={updateItem} />}
          {item.type === 'image' && <ImageItemEditor data={item} setData={updateItem} />}
        </Popup>

        )}

      {/* <LabelPreview />
      <ImagePreview /> */}
      <div style={{flex: 'auto', opacity: 0.5, alignSelf: 'stretch', display: 'flex'}}>
        <Popup on='click' trigger={<Button icon='plus' basic style={{boxShadow: 'none', margin: 0}} size='massive' />}>
          <AddLabelDialog onAdd={(item) => setItems(items => [...items, item])} />
        </Popup>
        
        </div>
      </div>
      </div>
      </Segment>
      </Route>
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

const AddLabelDialog: FC<{onAdd: ((data: LabelItemData)=>void)}> = ({onAdd}) => {

  const [type, setType] = useState<'text'|'image'>('text');
  const [value, setValue] = useState('');
  
  const key = useMemo(() => new  Date().getTime().toFixed(0), []);

  const newItemData: LabelItemData = useMemo(()=> type === 'image' 
    ? ({ type, key,  ...itemDefaults,  image: value })
    : ({ type, key,  ...itemDefaults,  text: value, font: '40px sans-serif' })
  , [type, value, key]);

  return (
    <Form onSubmit={() => onAdd(newItemData)} style={{minWidth: '400px'}}>
      <Form.Group widths='equal'>
        <Form.Field>
      <Radio label='Text' checked={type === 'text'} onChange={() => setType('text')} />

        </Form.Field>
        <Form.Field>
      <Radio label='Image' checked={type === 'image'} onChange={() => setType('image')} />
        </Form.Field>

      </Form.Group>
      <Form.Group widths='equal'>
        <Form.Field width={12}>
      <Input type='text' fluid placeholder={type === 'text' ? 'Enter text...' : 'https://...'} value={value} onChange={e => setValue(e.target.value)} />
      </Form.Field>
        <Form.Field width={4}>
      <Button type='submit' content='Add' />
      </Form.Field>
      </Form.Group>
    </Form>
  )
}

const ConnectionCard = () => {

  const { register, handleSubmit, formState: { errors } } = useForm<SerialOptions>();
  const [currentPort, setCurrentPort] = useState<SerialPort | undefined>();
  const [error, setError] = useState<{title: string, message?: string} | undefined>();

  useEffect(() => {
    if(Object.values(errors).every(v => !v)) return;
    // setError({title: 'Errors', })
  }, [errors]);

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

  return (
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

      {error && (<dialog><header>{error.title}</header><div>{error.message  ?? 'Unknown error'}</div></dialog>)}

      </Form>
            </Card.Content>
      </Card>
  )
}





const FontLoader: React.FC<{webFonts: WebFont[], onError: ((error: Error) => void)}> = ({webFonts, onError}) => {

  const [loading, setLoading] = useState(true);

  const loadedFonts = useRef<FontFace[]>([]);

  useEffect(() => {

    const newFonts = webFonts.filter(ff => !loadedFonts.current.some(lf => lf.family === ff.family))
      .flatMap(font => font.variants.map(v => {
          const source = new URL(font.files[v]);
          const [, weight, style] = v.match(/([1-9]00)?(italic)?/) ?? [];
          source.protocol = document.location.protocol;
          const fontFace = new FontFace(font.family, `URL(${source})`, {weight, style});
          console.log(`Loading font "${font.family}" (${v}) from ${source}`);
          return fontFace;
      }));
    const keepFonts = loadedFonts.current.filter(ff => webFonts.some(lf => lf.family === ff.family));
    const delFonts = loadedFonts.current.filter(ff => !webFonts.some(lf => lf.family === ff.family));

    console.log("Fonts changed! New: %o Keep: %o Del: %o", newFonts.map(f => f.family), keepFonts.map(f => f.family), delFonts.map(f => f.family));

    delFonts.forEach(fontFace => {
        console.log(`Unloading "${fontFace.family} (${fontFace.variant})!`);
        document.fonts.delete(fontFace);
    });


      // const fontVariants = webFonts.flatMap(font => font.variants.map(v => {
      //     const source = new URL(font.files[v]);
      //     source.protocol = document.location.protocol;
      //     const fontFace = new FontFace(font.family, `URL(${source})`);
      //     console.log(`Loading font "${font.family}" (${v}) from ${source}`);
      //     return fontFace;
      // }));

      Promise.all(newFonts.map(async ff => {
        try {
          await ff.load();
          const variant = [ff.style, ff.weight].filter(t => t !== 'normal').join('/');
          console.log(`Loaded font %o %s`, ff.family, variant || 'regular');
          document.fonts.add(ff);
        } catch(error) {
          console.error("Failed to load font:", error)
          onError(error as Error);
        }
      })).then(() => setLoading(false));

      // return () => {
      //     fontVariants.forEach(fontFace => {
      //         console.log(`Unloading "${fontFace.family} // ${fontFace.featureSettings} // ${fontFace.style}!`);
      //         document.fonts.delete(fontFace);
      //     });
      // }

      loadedFonts.current = [...newFonts, ...keepFonts];
  }, [webFonts, onError]);

  return (
      <Loader active={loading} />
  )
}