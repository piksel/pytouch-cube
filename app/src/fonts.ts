
export interface WebFontListPayload {
    kind: 'webfonts#webfontList';
    items: WebFont[];
}
export interface WebFont {
    "kind": "webfonts#webfont",
    "family": string,
    "variants": FontVariant[],
    "subsets": FontSubset[],
    "version": string,
    "lastModified": string,
    "files": Record<FontVariant, string>,
    category: FontCategory,
   }


export type FontCategory = 'handwriting' | 'sans-serif' | 'serif' | 'monospace' | 'display';
export type FontVariant = "regular" | "italic" | "700" | "700italic"
export type FontSubset = "greek" | "greek-ext" | "cyrillic-ext" | "latin-ext" | "latin" | "cyrillic"

export const AllFontCategories: FontCategory[] = ['handwriting', 'sans-serif', 'serif', 'monospace', 'display'];