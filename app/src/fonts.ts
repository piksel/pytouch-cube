export interface WebFont{
    "kind": "webfonts#webfont",
    "family": string,
    "variants": FontVariant[],
    "subsets": FontSubset[],
    "version": string,
    "lastModified": string,
    "files": Map<FontVariant, string>,
   }

export type FontVariant = "regular" | "italic" | "700" | "700italic"
export type FontSubset = "greek" | "greek-ext" | "cyrillic-ext" | "latin-ext" | "latin" | "cyrillic"