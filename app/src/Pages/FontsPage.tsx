import { useEffect, useMemo, useState } from "react";
import { Checkbox, Label, Input, Pagination, Grid, Segment, Table, Header, SemanticCOLORS, SemanticWIDTHSNUMBER, Divider } from "semantic-ui-react";
import { WebFont, AllFontCategories, WebFontListPayload, FontCategory } from "../fonts";
import { StateSetter } from "../types";
import { updateIncluded } from "../util";


const categoryColor: Record<FontCategory, SemanticCOLORS> = {
    handwriting: 'orange',
    'sans-serif': 'blue', 
    serif: 'pink', 
    monospace: 'violet', 
    display: 'green'
};

export const FontsPage: React.FC<{webFonts: WebFont[], setWebFonts: StateSetter<WebFont[]>}> = (props) => {
    const { webFonts, setWebFonts } = props;
    
    const [fonts, setFonts] = useState<WebFont[]>();
    const [fontsPerPage, setFontsPerPage] = useState(10);
    const [activePage, setActivePage] = useState(1);
    const [search, setSearch] = useState("");
    // const [selected, setSelected] = useState<string[]>([]);

    const selected = useMemo(() => webFonts.map(f => f.family), [webFonts]);

    const [categories, setCategories] = useState(AllFontCategories);

    useEffect(() => {
        (async ()=> {
            const response = await fetch('./googlefonts.json', {method: 'GET'});
            const payload = (await response.json()) as WebFontListPayload;
            payload.items.forEach(f => {
                if(!AllFontCategories.includes(f.category)) {
                    console.warn(`Unknown font category in payload for font "${f.family}": "${f.category}". It will not be displayed.`);
                }
            })
            setFonts(payload.items);
        })()
    }, [])

    const toggleCategory = (category: FontCategory): ((event: any, data: {checked?: boolean}) => void) => (_, {checked}) => updateIncluded(setCategories, category, !!checked);

    // const renderCategoryLabel = (item: DropdownItemProps, index: number) => ({
    //     color: categoryColor[item.value as FontCategory],
    //     content: item.text,
    //     size: 'tiny'
    // })

    const filteredFonts = useMemo(() => (fonts ?? []).filter(f => 
        !selected.includes(f.family) && 
        categories.includes(f.category) && 
        f.family.toLowerCase().includes(search)
    ), [fonts, categories, search, selected]);
    const selectedFonts = useMemo(() => (fonts ?? []).filter(f => selected.includes(f.family)), [fonts, selected]);
    const fontPages = useMemo(() => Math.ceil(filteredFonts.length / fontsPerPage), [filteredFonts, fontsPerPage]);

    const updateSelected = (font: WebFont, selected: boolean) => setWebFonts(wfs => [...wfs.filter(wf => wf.family !== font.family), ...(selected ? [font] : [])])

    return (
        <>
        <Segment attached='top' loading={!fonts}>
                <div>
                    <Input type='text' placeholder='Filter fonts...' fluid value={search} onChange={(e) => setSearch(e.target.value.toLowerCase())} />
                </div>
                <Divider />
                <div>
                    <Grid widths='equal' stretched columns={(AllFontCategories.length + 1) as SemanticWIDTHSNUMBER}>
                        <Grid.Column width='2' >
                        <label>Categories: </label>

                        </Grid.Column>
                    {AllFontCategories.map(category => 
                        <Grid.Column  key={category}>
                            <Checkbox className="capitalized" label={category} checked={categories.includes(category)} onChange={toggleCategory(category)} />
                        </Grid.Column>)}
                    </Grid>
                </div>
        
        </Segment>

            <Table attached compact>
                <Table.Body>
                    <Table.Row>
                        <Table.HeaderCell>Selected:</Table.HeaderCell>
                        <Table.HeaderCell />
                    </Table.Row>
                    {selectedFonts.length > 0 ? (
                        selectedFonts.map(f => <FontTableRow key={f.family} selected={selected.includes(f.family)} onToggle={(checked) => updateSelected(f, false)} font={f} />)
                    ): (
                        <Table.Row>
                            <Table.Cell />
                            <Table.Cell />

                            <Table.Cell>No fonts selected</Table.Cell>
                            <Table.Cell />
                            <Table.Cell />

                        </Table.Row>
                        
                    )}
                    <Table.Row>
                        <Table.HeaderCell>{"Add:"}</Table.HeaderCell>
                        <Table.HeaderCell />
                    </Table.Row>
                    {fonts && filteredFonts.filter((_, i) => i >= fontsPerPage * (activePage-1) && i < fontsPerPage * activePage).map((f, i) => 
                        <FontTableRow key={f.family} selected={selected.includes(f.family)} onToggle={(checked) => updateSelected(f, true)} font={f} />

                    )}
                    </Table.Body>

            </Table>

        <Segment attached='bottom'> 
            <Grid>
                <Grid.Column verticalAlign="bottom" width='13'>
                    <label>Pages:</label><br />
                    <Pagination boundaryRange={2} siblingRange={2} activePage={activePage} totalPages={fontPages} onPageChange={(_, d) => setActivePage(d.activePage ? Number(d.activePage) : 1)} />
                </Grid.Column>
                <Grid.Column verticalAlign="bottom" width='3'>

                    <Input  fluid labelPosition='right'  type="number" value={fontsPerPage} onChange={(e, d) => setFontsPerPage(e.target.valueAsNumber)}>
                  
    <input />
    <Label className="normal-weight" basic>of <strong>{filteredFonts.length}</strong></Label>
                        </Input>

                    

                </Grid.Column>
            </Grid>
        </Segment>
        </>
    )
}

const FontTableRow: React.FC<{font: WebFont, selected: boolean, onToggle: ((checked: boolean) => void)}> = ({font, selected, onToggle}) => {

    const {category, family, variants} = font;

    return (
        <Table.Row>
                        <Table.Cell width='1'>
            <Checkbox style={{}} toggle checked={selected} onChange={(_, d) => onToggle(!!d.checked)} />
            </Table.Cell>
            <Table.Cell>
                
                <Header>
                    {family}
                </Header>
            </Table.Cell>

            <Table.Cell>
            <FontPreview size='22px' font={font} /> 
            </Table.Cell>

            <Table.Cell>

                    <small title={variants.join(', ')}>{variants.length} variant(s)</small>
            </Table.Cell>           
             <Table.Cell>
            <Label className="capitalized" content={category} size="tiny" color={categoryColor[category]} />
            </Table.Cell>



        </Table.Row>
    )
}


const FontPreview: React.FC<{font: WebFont, size: string}> = ({font, size}) => {

    useEffect(() => {
        const fontVariants = font.variants.map(v => {
            const source = new URL(font.files[v]);
            source.protocol = document.location.protocol;
            const fontFace = new FontFace(font.family, `URL(${source})`);
            console.log(`Loading font "${font.family}" (${v}) from ${source}`);
            fontFace.load().then(ff => {
                console.log(`Loaded "${font.family}" variant: ${v}!`);
                document.fonts.add(ff);
            })
            return fontFace;
        });

        return () => {
            fontVariants.forEach(fontFace => {
                console.log(`Unloading "${fontFace.family} // ${fontFace.featureSettings} // ${fontFace.style}!`);
                document.fonts.delete(fontFace);
            });
        }
    }, [font.family, font.variants, font.files]);

    return (
        <div style={{fontFamily: font.family, fontSize: size}}>Lorem jävla ipsum vafan</div>
    )
}