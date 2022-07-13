import { StateSetter } from "./types";

export const valueOptions = (...values: string[]) => values.map(v => ({key: v, value: v, text: v[0].toUpperCase()+v.substring(1) }));

export const updateIncluded = <T>(set: StateSetter<T[]>, item: T, included: boolean) => set(items => [...items.filter(i => i !== item), ...(included ? [item] : [])])